from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, HTTPException, Request

from api import db
from api.logging import APILogger, LogManager, new_run_id
from engine.executor import Executor
from engine.loader import Loader
from engine.logger import get_logger

router = APIRouter(prefix="", tags=["execution"])

PLAYBOOK_DIR = Path("configs/playbooks")


async def _execute(run_id: str, playbook_name: str, manager: LogManager) -> None:
    path = _resolve_playbook(playbook_name)
    loader = Loader(get_logger())
    playbook = loader.load_playbook(path.as_posix())
    started_at = datetime.utcnow()
    trigger = None
    if isinstance(playbook.get("trigger"), dict):
        trigger = playbook.get("trigger", {}).get("type")
    elif isinstance(playbook.get("trigger"), str):
        trigger = str(playbook.get("trigger"))

    db.create_run(run_id, playbook.get("name", playbook_name), trigger, started_at.isoformat())
    logger = APILogger(run_id, manager)
    executor = Executor(logger=logger)

    status = "success"
    try:
        await executor.run_playbook(path.as_posix())
    except Exception as exc:  # pragma: no cover - surfaced via logs
        status = "failed"
        logger.error(str(exc))
    finally:
        finished_at = datetime.utcnow()
        duration = (finished_at - started_at).total_seconds()
        db.finish_run(run_id, status, finished_at.isoformat(), duration)
        await manager.publish(
            run_id,
            {"event": "complete", "status": status, "finished_at": finished_at.isoformat()},
        )


def _resolve_playbook(name: str) -> Path:
    candidate = name if name.endswith(('.yml', '.yaml')) else f"{name}.yml"
    path = PLAYBOOK_DIR / candidate
    if not path.exists():
        raise HTTPException(status_code=404, detail="Playbook not found")
    return path


@router.post("/playbooks/run/{name}")
async def run_playbook(name: str, request: Request) -> Dict[str, str]:
    run_id = new_run_id()
    manager: LogManager = request.app.state.log_manager
    asyncio.create_task(_execute(run_id, name, manager))
    return {"run_id": run_id, "playbook": name}


@router.get("/runs")
def list_runs() -> Dict[str, object]:
    return {"runs": db.fetch_runs()}


@router.get("/runs/{run_id}")
def get_run(run_id: str) -> Dict[str, object]:
    run = db.fetch_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    logs = db.fetch_logs(run_id)
    return {"run": run, "logs": logs}
