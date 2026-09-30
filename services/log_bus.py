"""Central log bus — fans out messages to UI and DB."""
import json
from datetime import datetime
from typing import Callable

from storage.db import get_connection


MAX_HISTORY = 500


class LogBus:
    def __init__(self) -> None:
        self._subscribers: list[Callable[[dict], None]] = []
        self._history: list[dict] = []
        self._project_id: int | None = None

    # --- Project context ---
    def set_project(self, project_id: int | None) -> None:
        self._project_id = project_id
        # New project context → clear history so previous project logs don't leak
        self._history.clear()

    # --- Subscription ---
    def subscribe(self, fn: Callable[[dict], None]) -> None:
        if fn not in self._subscribers:
            self._subscribers.append(fn)

    def unsubscribe(self, fn: Callable[[dict], None]) -> None:
        try:
            self._subscribers.remove(fn)
        except ValueError:
            pass

    def clear_subscribers(self) -> None:
        self._subscribers.clear()

    # --- History ---
    def get_history(self) -> list[dict]:
        return list(self._history)

    # --- Emit ---
    def emit(self, level: str, message: str, technical: dict | None = None) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        event = {
            "level": level,
            "message": message,
            "time": ts,
            "technical": technical or {},
        }

        # Save to in-memory history
        self._history.append(event)
        if len(self._history) > MAX_HISTORY:
            self._history = self._history[-MAX_HISTORY:]

        # Push to subscribers
        for fn in list(self._subscribers):
            try:
                fn(event)
            except Exception:
                pass

        # Persist to DB
        try:
            with get_connection() as conn:
                conn.execute(
                    "INSERT INTO logs (project_id, level, message, technical) VALUES (?,?,?,?)",
                    (
                        self._project_id,
                        level,
                        message,
                        json.dumps(technical or {}, ensure_ascii=False),
                    ),
                )
                conn.commit()
        except Exception:
            pass


log_bus = LogBus()