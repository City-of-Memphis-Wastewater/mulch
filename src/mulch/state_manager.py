# src/mulch/state_manager.py

import json
import sqlite3
import requests
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Literal, Union


StateBackend = Literal["json", "sqlite", "remote"]


class AbstractStateManager(ABC):
    """Abstract base for pluggable state storage backends."""

    @abstractmethod
    def load_state(self) -> dict:
        pass

    @abstractmethod
    def save_state(self, state: dict) -> None:
        pass


class FileStateManager(AbstractStateManager):
    """Stores state as a local JSON file."""

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load_state(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[StateManager] Failed to load state: {e}")
            return {}

    def save_state(self, state: dict) -> None:
        try:
            with self.path.open("w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"[StateManager] Failed to save state: {e}")


class SQLiteStateManager(AbstractStateManager):
    """Future: Stores state in a local SQLite database."""

    def __init__(self, db_path: Union[str, Path]):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self._ensure_table()

    def _ensure_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS state (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
            """)

    def load_state(self) -> dict:
        cur = self.conn.cursor()
        cur.execute("SELECT key, value FROM state;")
        return {row[0]: json.loads(row[1]) for row in cur.fetchall()}

    def save_state(self, state: dict) -> None:
        with self.conn:
            for key, value in state.items():
                self.conn.execute(
                    "REPLACE INTO state (key, value) VALUES (?, ?);",
                    (key, json.dumps(value))
                )


class RemoteAPIStateManager(AbstractStateManager):
    """Future: Stores state remotely via REST API."""

    def __init__(self, endpoint_url: str, auth_token: Optional[str] = None):
        self.url = endpoint_url.rstrip("/")
        self.auth_token = auth_token

    def load_state(self) -> dict:
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            response = requests.get(f"{self.url}/state", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[RemoteAPI] Failed to fetch remote state: {e}")
            return {}

    def save_state(self, state: dict) -> None:
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            response = requests.post(f"{self.url}/state", json=state, headers=headers)
            response.raise_for_status()
        except Exception as e:
            print(f"[RemoteAPI] Failed to save remote state: {e}")


class StateManagerFactory:
    """Creates the appropriate StateManager backend."""

    @staticmethod
    def create(backend: StateBackend = "json",
               location: Optional[Union[str, Path]] = None,
               remote_url: Optional[str] = None,
               auth_token: Optional[str] = None) -> AbstractStateManager:

        if backend == "json":
            state_path = Path(location) if location else Path(".mulch/state.json")
            return FileStateManager(state_path)

        elif backend == "sqlite":
            db_path = Path(location) if location else Path(".mulch/state.db")
            return SQLiteStateManager(db_path)

        elif backend == "remote":
            if not remote_url:
                raise ValueError("Remote backend requires remote_url")
            return RemoteAPIStateManager(remote_url, auth_token)

        else:
            raise ValueError(f"Unsupported backend: {backend}")
