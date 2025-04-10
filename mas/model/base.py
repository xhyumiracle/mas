from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable
from mas.message import Message

class Model(ABC):
    @abstractmethod
    async def run(self, messages: List[Message], tool_definitions: List[Dict[str, Any]] = None) -> Message:
        pass
    
    @abstractmethod
    def create_tool_definitions(self, tools: List[Callable]) -> List[Dict[str, Any]]:
        raise NotImplementedError("This model doesn't support tool calling")
