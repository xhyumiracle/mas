from datetime import datetime

from mas.graph.types import NodeId
from mas.storage.base import Storage
from typing import Any, Dict, List, Tuple, Optional

class FlowMemory:
    def __init__(self, storage: Storage):
        self.storage = storage

    def add_entry(self, caller: NodeId, callee: NodeId, action: str, data: Dict[str, Any]) -> None:
        entry = {
            "caller": caller,
            "callee": callee,
            "action": action,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.storage.add_entry(entry)

    def get_entries_by_caller(self, caller: NodeId) -> List[Tuple[NodeId, str]]:
        return self.storage.get_entries_by_caller(caller)
        # return [(e["callee"], e["action"]) for e in entries]

    def get_entries_by_callee(self, callee: NodeId) -> List[Tuple[NodeId, str]]:
        return self.storage.get_entries_by_callee(callee)
        # return [(e["caller"], e["action"]) for e in entries]

    def get_data(self, caller: NodeId, callee: NodeId, action: str) -> Optional[Dict[str, Any]]:
        entry = self.storage.get_entry(caller, callee, action)
        return entry["data"] if entry else None