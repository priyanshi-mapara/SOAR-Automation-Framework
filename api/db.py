from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path("data/soar.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_runs (
                id TEXT PRIMARY KEY,
                playbook TEXT NOT NULL,
                trigger TEXT,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                duration REAL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(run_id) REFERENCES execution_runs(id)
            );
            """
        )
        conn.commit()


def create_run(run_id: str, playbook: str, trigger: Optional[str], started_at: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO execution_runs (id, playbook, trigger, status, started_at) VALUES (?, ?, ?, ?, ?)",
            (run_id, playbook, trigger, "running", started_at),
        )
        conn.commit()


def finish_run(run_id: str, status: str, finished_at: str, duration: float) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE execution_runs SET status = ?, finished_at = ?, duration = ? WHERE id = ?",
            (status, finished_at, duration, run_id),
        )
        conn.commit()


def add_log(run_id: str, level: str, message: str, created_at: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO execution_logs (run_id, level, message, created_at) VALUES (?, ?, ?, ?)",
            (run_id, level, message, created_at),
        )
        conn.commit()


def fetch_runs(limit: int = 100) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, playbook, trigger, status, started_at, finished_at, duration FROM execution_runs ORDER BY started_at DESC LIMIT ?",
            (limit,),
        )
        return [dict(row) for row in cursor.fetchall()]


def fetch_run(run_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, playbook, trigger, status, started_at, finished_at, duration FROM execution_runs WHERE id = ?",
            (run_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def fetch_logs(run_id: str) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT level, message, created_at FROM execution_logs WHERE run_id = ? ORDER BY id ASC",
            (run_id,),
        )
        return [dict(row) for row in cursor.fetchall()]
