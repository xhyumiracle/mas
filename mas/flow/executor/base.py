from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator, Optional
from mas.graph import AgentTaskGraph, NodeId
from mas.memory.memory import FlowMemory
from mas.message import Message

@dataclass
class FlowExecutor(ABC):
    execution_chain: Optional[Iterator[NodeId]] = None # for chain execution
    is_chain: Optional[bool] = True

    @abstractmethod
    def run(self, graph: AgentTaskGraph, memory: FlowMemory) -> Message:
        raise NotImplementedError
    
    def get_execution_chain_str(self):
        # return f"{self.__class__.__name__}(is_chain={self.is_chain})"
        return '->'.join([str(i) for i in self.execution_chain])

    def set_execution_chain(self, execution_chain: Iterator[NodeId]):
        self.execution_chain = execution_chain