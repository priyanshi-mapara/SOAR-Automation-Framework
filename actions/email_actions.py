from typing import Any, Dict

from engine.base import Action


class SendEmailAction(Action):
    type = "send_email"

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        recipient = self.config.get("recipient", "security@example.com")
        subject = self.config.get("subject", "Security Notification")
        self.logger.info(f"Sending email to {recipient} with subject '{subject}'")
        context.setdefault("notifications", []).append({
            "recipient": recipient,
            "subject": subject,
        })
        return context
