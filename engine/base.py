from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Trigger(ABC):
    """Base class for triggers."""

    type: str

    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.config = config
        self.logger = logger

    @abstractmethod
    async def run(self) -> List[Dict[str, Any]]:
        """Run the trigger and return a list of context events."""


class Condition(ABC):
    """Base class for conditions."""

    type: str

    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.config = config
        self.logger = logger

    @abstractmethod
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate the condition against the provided context."""


class Action(ABC):
    """Base class for actions."""

    type: str

    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.config = config
        self.logger = logger

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action and return an updated context."""
