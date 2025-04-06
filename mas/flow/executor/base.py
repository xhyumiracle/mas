from abc import ABC, abstractmethod
from dataclasses import dataclass
from mas.graph import AgentTaskGraph
from mas.memory import FlowMemory
from mas.message import Message

@dataclass
class FlowExecutor(ABC):
    @abstractmethod
    def run(self, graph: AgentTaskGraph, memory: FlowMemory) -> Message:
        raise NotImplementedError
    
    @abstractmethod
    def get_execution_order_str(self):
        raise NotImplementedError