import asyncio
from typing import Any, Dict, List

from engine.base import Trigger


class ScheduleTrigger(Trigger):
    type = "schedule"

    async def run(self) -> List[Dict[str, Any]]:
        interval = int(self.config.get("interval", 2))
        runs = int(self.config.get("runs", 2))
        self.logger.info(f"Schedule trigger running every {interval}s for {runs} iterations")
        events: List[Dict[str, Any]] = []
        for run_index in range(runs):
            self.logger.debug(f"Generating scheduled event {run_index + 1}")
            events.append(
                {
                    "system": {
                        "user": "service-account",
                        "action": "iam_review",
                    },
                    "severity": run_index + 1,
                }
            )
            await asyncio.sleep(interval)
        return events
