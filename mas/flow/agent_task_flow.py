import logging
from typing import List, Optional, Iterator, Type, AsyncIterator
from pydantic import BaseModel, ConfigDict
import networkx as nx

from mas.agent.factory import create_agent
from mas.graph import AgentTaskGraph, NodeId
from mas.memory.flowmemory import FlowMemory
from mas.agent import Agent

from mas.graph.types import NodeAttr
from mas.flow.executor.base import FlowExecutor
from mas.storage import InMemoryStorage
from mas.memory.filemap import FileMap
logger = logging.getLogger(__name__)

# TODO: memory should be in flow or executor? maybe base executor
'''
Flow:
v0:
1. single start node
2. single branch (topological sort), for DAG only (get input from nx graph)
3. each node executes only when all (non-reject) in_arcs are done

v1: 
1. single branch (topological sort), support single node loop
2. reviewer node has at least 1 non-reject out_arc
3. action space: "default", "reject", "approve"
4. reviewer node on "approve": send its input to the next node

v2:
1. multi branch, or support cross-node loop
'''
class AgentTaskFlow(BaseModel):
    executor: FlowExecutor

    graph: Optional[AgentTaskGraph] = None
    memory: Optional[FlowMemory] = FlowMemory(storage=InMemoryStorage())
    filemap: Optional[FileMap] = FileMap()

    '''add {node_id: Agent(node_attr)} to each graph node'''
    def build_agents_on_graph(self, G: AgentTaskGraph):
        # nx.set_node_attributes(G, {node_id: self.cls_Agent(id=node_id, node_attr=NodeAttr(**attr)) for node_id, attr in G.nodes(data=True)}, name='agent')
        nx.set_node_attributes(G, {node_id: create_agent(id=node_id, attr=NodeAttr(**attr), filemap=self.filemap) for node_id, attr in G.nodes(data=True)}, name='agent')
        
    def build(self, G: AgentTaskGraph):
        self.build_agents_on_graph(G)
        self.graph = G
    
    async def run(self) -> AsyncIterator[Message]:
        """Execute the flow and yield each step's result."""
        return self.executor.run(self.graph, self.memory)

    async def run_to_completion(self) -> Message:
        """Execute the flow and return the final result."""
        return await self.executor.run_to_completion(self.graph, self.memory)

    '''
    for pydantic, resolve AgentTaskGraph compatiblity issue
    '''
    model_config = ConfigDict(arbitrary_types_allowed=True)