from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import db
from api.logging import LogManager
from api.routes import execution, logs, playbooks, triggers


def create_app() -> FastAPI:
    app = FastAPI(title="SOAR Automation Framework API", version="1.0.0")
    manager = LogManager()

    app.state.log_manager = manager

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(playbooks.router)
    app.include_router(execution.router)
    app.include_router(logs.router)
    app.include_router(triggers.router)

    @app.on_event("startup")
    async def _startup() -> None:
        db.init_db()

    build_dir = Path("ui/build")
    if build_dir.exists():
        app.mount("/", StaticFiles(directory=build_dir, html=True), name="ui")

    return app


app = create_app()
