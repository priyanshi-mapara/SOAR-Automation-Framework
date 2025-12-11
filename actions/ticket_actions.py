from typing import Any, Dict

from engine.base import Action


class CreateTicketAction(Action):
    type = "create_ticket"

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        priority = self.config.get("priority", "Medium")
        summary = self.config.get("summary", "Automated incident created")
        ticket = {
            "id": context.get("ticket_id", "TICKET-1001"),
            "priority": priority,
            "summary": summary,
        }
        self.logger.info(f"Ticket created: {ticket['id']} (Priority: {priority})")
        context["ticket"] = ticket
        return context
