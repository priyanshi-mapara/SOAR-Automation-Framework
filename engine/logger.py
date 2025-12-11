from datetime import datetime
from typing import Any


class Logger:
    def _log(self, level: str, message: str) -> None:
        timestamp = datetime.utcnow().isoformat()
        print(f"[{level}] {timestamp} - {message}")

    def info(self, message: str) -> None:
        self._log("INFO", message)

    def debug(self, message: str) -> None:
        self._log("DEBUG", message)

    def error(self, message: str) -> None:
        self._log("ERROR", message)


def get_logger(_: Any = None) -> Logger:
    return Logger()
