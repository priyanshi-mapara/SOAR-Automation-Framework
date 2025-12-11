from pathlib import Path

import uvicorn
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.server import configure_frontend, create_app


def build_app() -> object:
    """Create the FastAPI app and attach the built UI if present."""

    application = create_app(mount_frontend=False)
    configure_frontend(application, build_dir=Path(__file__).parent / "ui" / "dist")
    return application


app = build_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
