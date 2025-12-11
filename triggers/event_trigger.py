from typing import Any, Dict, List

from engine.base import Trigger


class EventTrigger(Trigger):
    type = "event"

    async def run(self) -> List[Dict[str, Any]]:
        self.logger.info("Event trigger invoked with mock incident data")
        return [
            {
                "email": {
                    "sender_domain": "suspicious.com",
                    "sender_ip": "203.0.113.5",
                    "subject": "Security alert",
                },
                "severity": 8,
            }
        ]
