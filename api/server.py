from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api import db
from api.logging import LogManager
from api.routes import execution, logs, playbooks, triggers


def configure_frontend(app: FastAPI, build_dir: Path | None = None) -> None:
    """
    Attach the built React dashboard to the FastAPI application.

    The function mounts static assets and serves ``index.html`` from the
    ``ui/dist`` directory when it exists. If the build output is missing the
    backend keeps running and logs a warning so API endpoints remain usable.
    """

    resolved_build_dir = build_dir or Path(__file__).resolve().parent.parent / "ui" / "dist"
    if not resolved_build_dir.exists():
        print(f"[WARN] UI build directory not found at {resolved_build_dir}. API remains available.")
        return

    assets_dir = resolved_build_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="ui-assets")

    index_file = resolved_build_dir / "index.html"
    if index_file.exists():

        @app.get("/", include_in_schema=False)
        async def serve_index() -> FileResponse:  # type: ignore[unused-ignore]
            return FileResponse(index_file)
    else:
        print(f"[WARN] index.html not found in {resolved_build_dir}; only static assets will be served.")

    app.mount("/", StaticFiles(directory=resolved_build_dir, html=True), name="ui")


def create_app(mount_frontend: bool = True) -> FastAPI:
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

    if mount_frontend:
        configure_frontend(app)

    return app


app = create_app()
