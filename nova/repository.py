"""Persistence contract and SQLite implementation for Nova conversation state."""
from pathlib import Path
import sqlite3
from typing import Protocol

from nova.workflow import NovaState, Status, Step


class StateRepository(Protocol):
    def load(self, conversation_id: str) -> NovaState | None: ...
    def save(self, conversation_id: str, state: NovaState) -> None: ...


class InMemoryStateRepository:
    def __init__(self) -> None:
        self.sessions: dict[str, NovaState] = {}

    def load(self, conversation_id: str) -> NovaState | None:
        state = self.sessions.get(conversation_id)
        return None if state is None else NovaState(
            intent=state.intent,
            order_id=state.order_id,
            next_step=state.next_step,
            status=state.status,
            pending_order_id=state.pending_order_id,
        )

    def save(self, conversation_id: str, state: NovaState) -> None:
        self.sessions[conversation_id] = NovaState(
            intent=state.intent,
            order_id=state.order_id,
            next_step=state.next_step,
            status=state.status,
            pending_order_id=state.pending_order_id,
        )


class SQLiteStateRepository:
    """Local durable store; not designed for concurrent multi-worker writes."""

    def __init__(self, db_path: str | Path = "nova_state.sqlite3") -> None:
        self.db_path = str(db_path)
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_states (
                    conversation_id TEXT PRIMARY KEY,
                    intent TEXT NOT NULL,
                    order_id TEXT,
                    next_step TEXT NOT NULL,
                    status TEXT NOT NULL,
                    pending_order_id TEXT
                )
            """)
            columns = {
                row[1] for row in conn.execute("PRAGMA table_info(conversation_states)")
            }
            if "pending_order_id" not in columns:
                conn.execute(
                    "ALTER TABLE conversation_states ADD COLUMN pending_order_id TEXT"
                )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def load(self, conversation_id: str) -> NovaState | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT intent, order_id, next_step, status, pending_order_id "
                "FROM conversation_states WHERE conversation_id = ?",
                (conversation_id,),
            ).fetchone()
        if row is None:
            return None
        intent, order_id, next_step, status, pending_order_id = row
        return NovaState(
            intent=intent,
            order_id=order_id,
            next_step=Step(next_step),
            status=Status(status),
            pending_order_id=pending_order_id,
        )

    def save(self, conversation_id: str, state: NovaState) -> None:
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO conversation_states
                   (conversation_id, intent, order_id, next_step, status, pending_order_id)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(conversation_id) DO UPDATE SET
                     intent=excluded.intent,
                     order_id=excluded.order_id,
                     next_step=excluded.next_step,
                     status=excluded.status,
                     pending_order_id=excluded.pending_order_id""",
                (conversation_id, state.intent, state.order_id,
                 state.next_step.value, state.status.value, state.pending_order_id),
            )
