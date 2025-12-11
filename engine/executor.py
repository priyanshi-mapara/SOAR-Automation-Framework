import asyncio
from typing import Any, Dict, List

from engine.logger import Logger
from engine.loader import Loader
from utils import validator


class Executor:
    def __init__(self, logger: Logger | None = None) -> None:
        self.logger = logger or Logger()
        self.loader = Loader(self.logger)
        self.components: Dict[str, Dict[str, Any]] = {}

    async def run_playbook(self, playbook_path: str) -> None:
        playbook = self.loader.load_playbook(playbook_path)
        validator.validate_playbook(playbook)
        self.components = self.loader.discover_all()

        trigger_instance = self._instantiate_trigger(playbook.get("trigger"))
        contexts = await trigger_instance.run()

        for index, context in enumerate(contexts, start=1):
            self.logger.info(f"Processing event {index} for playbook '{playbook.get('name')}'")
            if self._evaluate_conditions(playbook.get("conditions", []), context):
                self._execute_actions(playbook.get("actions", []), context)
            else:
                self.logger.info("Conditions not met. Skipping actions for this event.")

    def _instantiate_trigger(self, trigger_data: Any) -> Any:
        trigger_config: Dict[str, Any] = {}
        trigger_type = ""
        if isinstance(trigger_data, dict):
            trigger_type = trigger_data.get("type", "")
            trigger_config = trigger_data
        else:
            trigger_type = str(trigger_data)
            trigger_config = {"type": trigger_type}

        trigger_class = self.components.get("triggers", {}).get(trigger_type)
        if not trigger_class:
            raise ValueError(f"Trigger '{trigger_type}' not found. Available: {list(self.components.get('triggers', {}).keys())}")
        self.logger.info(f"Starting trigger: {trigger_type}")
        return trigger_class(trigger_config, self.logger)

    def _evaluate_conditions(self, conditions: List[Dict[str, Any]], context: Dict[str, Any]) -> bool:
        for condition_config in conditions:
            condition_type = condition_config.get("type")
            condition_class = self.components.get("conditions", {}).get(condition_type)
            if not condition_class:
                raise ValueError(f"Condition '{condition_type}' not found. Available: {list(self.components.get('conditions', {}).keys())}")
            condition = condition_class(condition_config, self.logger)
            result = condition.evaluate(context)
            status = "passed" if result else "failed"
            self.logger.debug(f"Condition {status}: {condition_type}(field={condition_config.get('field')})")
            if not result:
                return False
        return True

    def _execute_actions(self, actions: List[Dict[str, Any]], context: Dict[str, Any]) -> None:
        for action_config in actions:
            action_type = action_config.get("type")
            action_class = self.components.get("actions", {}).get(action_type)
            if not action_class:
                raise ValueError(f"Action '{action_type}' not found. Available: {list(self.components.get('actions', {}).keys())}")
            action = action_class(action_config, self.logger)
            self.logger.info(f"Executing action: {action_type}")
            context = action.execute(context)
        self.logger.info(f"Completed actions. Final context keys: {list(context.keys())}")


def run_playbook(playbook_path: str) -> None:
    executor = Executor()
    asyncio.run(executor.run_playbook(playbook_path))
