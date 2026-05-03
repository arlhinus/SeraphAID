"""
storage/base.py — Interfaz abstracta para el backend de persistencia.

Diseñada para soportar:
- v0.x: JSON local por usuario anónimo (sesión única)
- v1.x: SQLite local con user_id
- v2.x: PostgreSQL / cloud con autenticación real

Cada método trabaja con user_id + session_id para preparar la
arquitectura multi-usuario desde el inicio.
"""
from abc import ABC, abstractmethod
from typing import Optional
import uuid


def new_session_id() -> str:
    return str(uuid.uuid4())


def new_user_id() -> str:
    return str(uuid.uuid4())


class StorageBackend(ABC):

    @abstractmethod
    def save_session(self, user_id: str, session_id: str, data: dict) -> None:
        """Guarda o actualiza los datos de una sesión."""
        ...

    @abstractmethod
    def get_session(self, user_id: str, session_id: str) -> Optional[dict]:
        """Recupera los datos de una sesión específica."""
        ...

    @abstractmethod
    def list_sessions(self, user_id: str) -> list[dict]:
        """Lista las sesiones de un usuario (metadata: id, timestamp, resumen)."""
        ...

    @abstractmethod
    def delete_session(self, user_id: str, session_id: str) -> None:
        """Elimina una sesión."""
        ...
