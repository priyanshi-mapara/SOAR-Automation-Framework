from typing import Any, Dict

from engine.base import Action
from utils.helpers import get_nested_value


class EnrichIPAction(Action):
    type = "enrich_ip"

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        field = self.config.get("field")
        ip_value = get_nested_value(context, field) if field else None
        enrichment = {
            "ip": ip_value or "0.0.0.0",
            "reputation": "suspicious" if ip_value == "203.0.113.5" else "unknown",
            "geo": "Example City",
        }
        self.logger.info(f"Enriched IP {enrichment['ip']} with reputation {enrichment['reputation']}")
        context.setdefault("enrichments", []).append(enrichment)
        return context
