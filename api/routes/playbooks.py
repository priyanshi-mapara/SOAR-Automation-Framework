from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, UploadFile

from engine.loader import Loader
from engine.logger import get_logger

PLAYBOOK_DIR = Path("configs/playbooks")
PLAYBOOK_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/playbooks", tags=["playbooks"])


class PlaybookStore:
    def __init__(self) -> None:
        self.loader = Loader(get_logger())

    def list_playbooks(self) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for path in list(PLAYBOOK_DIR.glob("*.yml")) + list(PLAYBOOK_DIR.glob("*.yaml")):
            data = self.loader.load_playbook(path.as_posix())
            items.append(
                {
                    "name": data.get("name") or path.stem,
                    "file": path.name,
                    "trigger": data.get("trigger"),
                    "actions": data.get("actions", []),
                    "conditions": data.get("conditions", []),
                }
            )
        return items

    def read_playbook(self, name: str) -> Dict[str, Any]:
        path = self._resolve_path(name)
        if not path.exists():
            raise HTTPException(status_code=404, detail="Playbook not found")
        return self.loader.load_playbook(path.as_posix())

    def write_playbook(self, name: str, content: str) -> None:
        path = self._resolve_path(name)
        path.write_text(content, encoding="utf-8")

    def delete_playbook(self, name: str) -> None:
        path = self._resolve_path(name)
        if not path.exists():
            raise HTTPException(status_code=404, detail="Playbook not found")
        path.unlink()

    def _resolve_path(self, name: str) -> Path:
        filename = name if name.endswith(('.yml', '.yaml')) else f"{name}.yml"
        return PLAYBOOK_DIR / filename


store = PlaybookStore()


@router.get("")
def list_playbooks() -> List[Dict[str, Any]]:
    return store.list_playbooks()


@router.get("/{name}")
def get_playbook(name: str) -> Dict[str, Any]:
    return store.read_playbook(name)


@router.post("/upload")
async def upload_playbook(file: UploadFile) -> Dict[str, Any]:
    content = await file.read()
    target = PLAYBOOK_DIR / file.filename
    target.write_bytes(content)
    return {"message": "Playbook uploaded", "file": file.filename}


@router.put("/{name}")
async def update_playbook(name: str, body: Dict[str, Any]) -> Dict[str, Any]:
    import yaml  # type: ignore

    if "content" in body and isinstance(body["content"], str):
        content = body["content"]
    else:
        content = yaml.safe_dump(body)
    store.write_playbook(name, content)
    return {"message": "Playbook updated", "name": name}


@router.delete("/{name}")
def delete_playbook(name: str) -> Dict[str, Any]:
    store.delete_playbook(name)
    return {"message": "Playbook deleted", "name": name}
