from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator
from mas.graph import AgentTaskGraph
from mas.memory import FlowMemory
from mas.message import Message

@dataclass
class FlowExecutor(ABC):
    
    @abstractmethod
    async def run(self, graph: AgentTaskGraph, memory: FlowMemory) -> AsyncIterator[Message]:
        """Execute the flow and yield each step's result."""
        raise NotImplementedError

    async def run_to_completion(self, graph: AgentTaskGraph, memory: FlowMemory) -> Message:
        """Execute the flow and return the final result."""
        last_response = None
        async for response in self.run(graph, memory):
            last_response = response
        return last_response