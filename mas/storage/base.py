from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Optional

from mas.graph.types import NodeId

class Storage(ABC):
    @abstractmethod
    def add_entry(self, entry: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_entries_by_caller(self, caller: NodeId) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_entries_by_callee(self, callee: NodeId) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_entry(self, caller: NodeId, callee: NodeId, action: str) -> Optional[Dict[str, Any]]:
        pass