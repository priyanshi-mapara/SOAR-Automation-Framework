from typing import Any, Dict


def get_nested_value(data: Dict[str, Any], field: str) -> Any:
    keys = field.split(".")
    value: Any = data
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value
