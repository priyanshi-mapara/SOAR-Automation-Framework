from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/logs", tags=["logs"])


@router.websocket("/stream/{run_id}")
async def stream_logs(websocket: WebSocket, run_id: str) -> None:
    await websocket.accept()
    manager = websocket.app.state.log_manager
    queue = manager.register(run_id)
    try:
        while True:
            payload = await queue.get()
            await websocket.send_json(payload)
    except WebSocketDisconnect:
        manager.unregister(run_id, queue)
    finally:
        manager.unregister(run_id, queue)
