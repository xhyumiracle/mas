from datetime import datetime

from mas.graph.types import NodeId
from mas.storage.base import Storage
from typing import Any, Dict, List, Tuple, Optional

class FlowMemory:
    def __init__(self, storage: Storage):
        self.storage = storage

    def add_entry(self, caller: NodeId, callee: NodeId, label: str, data: Dict[str, Any]) -> None:
        entry = {
            "caller": caller,
            "callee": callee,
            "label": label,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.storage.add_entry(entry)

    def get_entries_by_caller(self, caller: NodeId, mask: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        entries = self.storage.get_entries_by_caller(caller)
        return self.entries_mask(entries, mask)

    def get_entries_by_callee(self, callee: NodeId, mask: Optional[List[str]] = None) -> List[Tuple[NodeId, str]]:
        entries = self.storage.get_entries_by_callee(callee)
        return self.entries_mask(entries, mask)

    def get_data(self, caller: NodeId, callee: NodeId, label: str) -> Optional[Dict[str, Any]]:
        entry = self.storage.get_entry(caller, callee, label)
        return entry["data"] if entry else None

    def entries_mask(self, entries: List[Dict[str, Any]], keys: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        if keys is None:
            return entries  # full entry dicts

        # Apply mask
        return [
            {k: entry[k] for k in keys if k in entry}
            for entry in entries
        ]