# SeraphAID storage package
from .base import StorageBackend
from .local_json import LocalJSONStorage

__all__ = ["StorageBackend", "LocalJSONStorage"]
