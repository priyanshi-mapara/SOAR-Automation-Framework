from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter

from api import db
from engine.loader import Loader
from engine.logger import get_logger

router = APIRouter(prefix="/triggers", tags=["triggers"])

active_triggers: Dict[str, bool] = {}


def _ensure_triggers() -> None:
    global active_triggers
    if active_triggers:
        return
    loader = Loader(get_logger())
    components = loader.discover_all().get("triggers", {})
    active_triggers = {name: True for name in components.keys()}


def _last_run(trigger_name: str) -> str | None:
    for run in db.fetch_runs(limit=100):
        if run.get("trigger") == trigger_name:
            return run.get("finished_at") or run.get("started_at")
    return None


@router.get("")
def list_triggers() -> Dict[str, List[Dict[str, object]]]:
    _ensure_triggers()
    data = [
        {"name": name, "active": status, "last_run": _last_run(name)}
        for name, status in active_triggers.items()
    ]
    return {"triggers": data}


@router.post("/enable/{name}")
def enable_trigger(name: str) -> Dict[str, object]:
    _ensure_triggers()
    active_triggers[name] = True
    return {"name": name, "active": True}


@router.post("/disable/{name}")
def disable_trigger(name: str) -> Dict[str, object]:
    _ensure_triggers()
    active_triggers[name] = False
    return {"name": name, "active": False}
