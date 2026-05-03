"""
storage/local_json.py — Backend de almacenamiento local en JSON.

Implementación para v0.x: cada usuario tiene un archivo JSON en .seraphaid_data/.
En v1.x se reemplazará por SQLiteStorage sin cambiar la interfaz.

Estructura de archivos:
    .seraphaid_data/
        {user_id}/
            sessions.json   ← lista de sesiones con metadata
            {session_id}.json ← datos completos de cada sesión
"""
import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

from .base import StorageBackend

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", ".seraphaid_data")


class LocalJSONStorage(StorageBackend):
    """
    Almacenamiento local en JSON. Simple, sin dependencias externas.
    Válido para uso personal local (v0.x).
    """

    def __init__(self, base_dir: str = DATA_DIR):
        self._base = base_dir

    def _user_dir(self, user_id: str) -> str:
        path = os.path.join(self._base, user_id)
        os.makedirs(path, exist_ok=True)
        return path

    def _sessions_index_path(self, user_id: str) -> str:
        return os.path.join(self._user_dir(user_id), "sessions.json")

    def _session_path(self, user_id: str, session_id: str) -> str:
        return os.path.join(self._user_dir(user_id), f"{session_id}.json")

    def save_session(self, user_id: str, session_id: str, data: dict) -> None:
        try:
            # Guardar datos completos
            with open(self._session_path(user_id, session_id), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # Actualizar índice
            index = self._load_index(user_id)
            entry = {
                "session_id": session_id,
                "timestamp": data.get("timestamp", datetime.now(timezone.utc).isoformat()),
                "summary": data.get("summary", ""),
                "altered_count": data.get("altered_count", 0),
            }
            # Reemplazar si existe, agregar si no
            index = [e for e in index if e["session_id"] != session_id]
            index.append(entry)
            index.sort(key=lambda x: x["timestamp"], reverse=True)

            with open(self._sessions_index_path(user_id), "w", encoding="utf-8") as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"LocalJSONStorage.save_session error: {e}")

    def get_session(self, user_id: str, session_id: str) -> Optional[dict]:
        try:
            path = self._session_path(user_id, session_id)
            if not os.path.exists(path):
                return None
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"LocalJSONStorage.get_session error: {e}")
            return None

    def list_sessions(self, user_id: str) -> list[dict]:
        return self._load_index(user_id)

    def delete_session(self, user_id: str, session_id: str) -> None:
        try:
            path = self._session_path(user_id, session_id)
            if os.path.exists(path):
                os.remove(path)
            index = [e for e in self._load_index(user_id) if e["session_id"] != session_id]
            with open(self._sessions_index_path(user_id), "w", encoding="utf-8") as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"LocalJSONStorage.delete_session error: {e}")

    def _load_index(self, user_id: str) -> list[dict]:
        path = self._sessions_index_path(user_id)
        if not os.path.exists(path):
            return []
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
