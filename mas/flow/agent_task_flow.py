from typing import List, Optional, Iterator, Type
from pydantic import BaseModel, ConfigDict
import networkx as nx

from mas.agent.agno import AgnoAgent
from mas.agent.mock import MockAgent
from mas.graph import AgentTaskGraph, NodeId
from mas.memory.memory import FlowMemory
from mas.agent import Agent

from mas.graph.types import NodeAttr
from mas.flow.executor.base import FlowExecutor
from mas.model.pool import ModelPool
from mas.storage import InMemoryStorage
from mas.tool.pool import ToolPool

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
    agent_cls: Type[Agent]

    graph: Optional[AgentTaskGraph] = None
    memory: Optional[FlowMemory] = FlowMemory(storage=InMemoryStorage())
    agents: Optional[List[Agent]] = []

    def build_chain(self, G: AgentTaskGraph):

        self.executor.set_execution_chain(list(G.topological_sort()))

    '''add {node_id: Agent(node_attr)} to each graph node'''
    def build_agents_on_graph(self, G: AgentTaskGraph):
        nx.set_node_attributes(G, {node_id: self.agent_cls(id=node_id, node_attr=NodeAttr(**attr)) for node_id, attr in G.nodes(data=True)}, name='agent')
        
    def build(self, G: AgentTaskGraph):
        self.build_agents_on_graph(G)
        self.graph = G
        if self.executor.is_chain:
            self.build_chain(G)
    
    def run(self):
        return self.executor.run(self.graph, self.memory)
    
    # TODO: run stream

    def build_and_run(self):
        self.build()
        return self.run()

    def pprint_flow_order(self):
        print(self.executor.get_execution_chain_str())
    '''
    for pydantic, resolve AgentTaskGraph compatiblity issue
    '''
    model_config = ConfigDict(arbitrary_types_allowed=True)