from typing import Any, Dict

from engine.base import Condition
from utils.helpers import get_nested_value


class EqualsCondition(Condition):
    type = "equals"

    def evaluate(self, context: Dict[str, Any]) -> bool:
        field_value = get_nested_value(context, self.config.get("field", ""))
        return field_value == self.config.get("value")


class ContainsCondition(Condition):
    type = "contains"

    def evaluate(self, context: Dict[str, Any]) -> bool:
        field_value = get_nested_value(context, self.config.get("field", ""))
        expected = self.config.get("value")
        return expected in field_value if isinstance(field_value, str) else False


class GreaterThanCondition(Condition):
    type = "greater_than"

    def evaluate(self, context: Dict[str, Any]) -> bool:
        field_value = get_nested_value(context, self.config.get("field", ""))
        expected = self.config.get("value")
        try:
            return float(field_value) > float(expected)
        except (TypeError, ValueError):
            return False
