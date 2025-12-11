from typing import Any, Dict, List


REQUIRED_FIELDS = {"name", "trigger", "conditions", "actions"}


def _ensure_keys(playbook: Dict[str, Any]) -> None:
    missing = REQUIRED_FIELDS - set(playbook.keys())
    if missing:
        raise ValueError(f"Playbook is missing required fields: {', '.join(sorted(missing))}")


def _ensure_list(key: str, value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"'{key}' must be a list in the playbook definition.")
    return value


def _ensure_action_condition_structure(entries: List[Dict[str, Any]], entry_name: str) -> None:
    for entry in entries:
        if not isinstance(entry, dict) or "type" not in entry:
            raise ValueError(f"Each {entry_name} requires a 'type' field. Offending entry: {entry}")


def validate_playbook(playbook: Dict[str, Any]) -> None:
    _ensure_keys(playbook)
    _ensure_action_condition_structure(_ensure_list("conditions", playbook.get("conditions")), "condition")
    _ensure_action_condition_structure(_ensure_list("actions", playbook.get("actions")), "action")
