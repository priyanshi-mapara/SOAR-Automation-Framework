from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from engine.logger import Logger

import api.db as db


class LogManager:
    def __init__(self) -> None:
        self.subscribers: Dict[str, List[asyncio.Queue[Dict[str, Any]]]] = {}

    def register(self, run_id: str) -> asyncio.Queue[Dict[str, Any]]:
        queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self.subscribers.setdefault(run_id, []).append(queue)
        return queue

    def unregister(self, run_id: str, queue: asyncio.Queue[Dict[str, Any]]) -> None:
        if run_id in self.subscribers:
            self.subscribers[run_id] = [q for q in self.subscribers[run_id] if q is not queue]
            if not self.subscribers[run_id]:
                self.subscribers.pop(run_id, None)

    async def publish(self, run_id: str, payload: Dict[str, Any]) -> None:
        if run_id not in self.subscribers:
            return
        for queue in list(self.subscribers[run_id]):
            await queue.put(payload)


class APILogger(Logger):
    def __init__(self, run_id: str, manager: LogManager) -> None:
        super().__init__()
        self.run_id = run_id
        self.manager = manager

    def _log(self, level: str, message: str) -> None:  # type: ignore[override]
        timestamp = datetime.utcnow().isoformat()
        super()._log(level, message)
        db.add_log(self.run_id, level, message, timestamp)
        asyncio.create_task(
            self.manager.publish(
                self.run_id, {"level": level, "message": message, "timestamp": timestamp}
            )
        )


def new_run_id() -> str:
    return uuid4().hex
