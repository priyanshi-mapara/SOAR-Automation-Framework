import argparse
import asyncio
from pathlib import Path

from engine.executor import Executor
from engine.logger import get_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a SOAR playbook")
    parser.add_argument(
        "--playbook",
        default="configs/playbooks/phishing_triage.yml",
        help="Path to the playbook YAML file",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    playbook_path = Path(args.playbook)
    if not playbook_path.exists():
        raise FileNotFoundError(f"Playbook not found at {playbook_path}")

    logger = get_logger()
    executor = Executor(logger=logger)
    logger.info(f"Running playbook {playbook_path}")
    asyncio.run(executor.run_playbook(playbook_path.as_posix()))


if __name__ == "__main__":
    main()
