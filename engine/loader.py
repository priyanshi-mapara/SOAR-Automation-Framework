import importlib
import json
import pkgutil
from typing import Any, Dict, List, Type

from engine.base import Action, Condition, Trigger


class Loader:
    def __init__(self, logger: Any) -> None:
        self.logger = logger

    def load_playbook(self, path: str) -> Dict[str, Any]:
        self.logger.info(f"Loading playbook from {path}...")
        with open(path, "r", encoding="utf-8") as handle:
            raw = handle.read()
        try:
            import yaml  # type: ignore

            return yaml.safe_load(raw)
        except ModuleNotFoundError:
            self.logger.error("PyYAML not installed. Falling back to JSON parser (YAML subset only).")
            try:
                return json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ImportError(
                    "PyYAML is required for non-JSON YAML playbooks. Install with 'pip install pyyaml'."
                ) from exc

    def _import_modules(self, package: Any) -> None:
        prefix = package.__name__ + "."
        for module_info in pkgutil.iter_modules(package.__path__, prefix):
            importlib.import_module(module_info.name)

    def _collect_subclasses(self, base_class: Type, package_name: str) -> List[Type]:
        subclasses: List[Type] = []
        for subclass in base_class.__subclasses__():
            if subclass.__module__.startswith(package_name):
                subclasses.append(subclass)
            subclasses.extend(self._collect_subclasses(subclass, package_name))
        return subclasses

    def discover_components(self, package: Any, base_class: Type) -> Dict[str, Type]:
        self._import_modules(package)
        discovered: Dict[str, Type] = {}
        for subclass in self._collect_subclasses(base_class, package.__name__):
            component_type = getattr(subclass, "type", subclass.__name__.lower())
            discovered[component_type] = subclass
            self.logger.debug(
                f"Discovered {base_class.__name__}: {component_type} -> {subclass.__module__}.{subclass.__name__}"
            )
        return discovered

    def discover_all(self) -> Dict[str, Dict[str, Type]]:
        import actions
        import conditions
        import triggers

        return {
            "actions": self.discover_components(actions, Action),
            "conditions": self.discover_components(conditions, Condition),
            "triggers": self.discover_components(triggers, Trigger),
        }
