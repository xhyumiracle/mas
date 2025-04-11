from abc import abstractmethod
import logging
from typing import List, Optional, AsyncIterator
from pydantic import BaseModel, ConfigDict, Field

from mas.graph import TaskGraph
from mas.memory.flowmemory import FlowMemory
from mas.message.types import Message
from mas.storage import InMemoryStorage
from mas.memory.filemap import FileMap
logger = logging.getLogger(__name__)

'''
Flow:
v0:
1. single start node
2. single branch (topological sort), for DAG only (get input from nx graph)
3. each node executes only when all (non-reject) in_arcs are done

v1: 
1. single branch (topological sort), support single node loop
2. reviewer node has at least 1 non-reject out_arc
3. edge label space: "default", "reject", "approve"
4. reviewer node on "approve": send its input to the next node

v2:
1. multi branch, or support cross-node loop
'''
class GraphExecutor(BaseModel):
    """Base class for graph-based task executors."""
    
    graph: TaskGraph
    memory: FlowMemory = Field(default_factory=lambda: FlowMemory(storage=InMemoryStorage()))
    filemap: FileMap = Field(default_factory=FileMap)

    def __init__(self, graph: TaskGraph, **kwargs):
        super().__init__(graph=graph, **kwargs)

    @abstractmethod
    async def run(self) -> AsyncIterator[Message]:
        """Execute the flow and yield each step's result."""
        raise NotImplementedError

    async def run_to_completion(self) -> Message:
        """Execute the flow and return the final result."""
        last_response = None
        async for response in self.run():
            last_response = response
        return last_response
    '''
    for pydantic, resolve TaskGraph compatiblity issue
    '''
    model_config = ConfigDict(arbitrary_types_allowed=True)