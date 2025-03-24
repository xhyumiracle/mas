from collections import defaultdict
from typing import Any, Dict, List, Tuple, Optional
from mas.graph.types import NodeId
from mas.storage.base import Storage

class InMemoryStorage(Storage):
    def __init__(self):
        self.entries = []
        self.caller_index = defaultdict(list)
        self.callee_index = defaultdict(list)
        self.entry_index = {}

    def add_entry(self, entry: Dict[str, Any]) -> None:
        self.entries.append(entry)
        caller = entry["caller"]
        callee = entry["callee"]
        action = entry["action"]
        self.caller_index[caller].append(entry)
        self.callee_index[callee].append(entry)
        self.entry_index[(caller, callee, action)] = entry

    def get_entries_by_caller(self, caller: NodeId) -> List[Dict[str, Any]]:
        return self.caller_index.get(caller, [])

    def get_entries_by_callee(self, callee: NodeId) -> List[Dict[str, Any]]:
        return self.callee_index.get(callee, [])

    def get_entry(self, caller: NodeId, callee: NodeId, action: str) -> Optional[Dict[str, Any]]:
        return self.entry_index.get((caller, callee, action), None)