import logging
from typing import List
from mas.curator.base import Curator
from mas.graph.task_graph import TaskGraph
from mas.graph.types import NodeAttr
from mas.agent.factory import create_agent
import networkx as nx

from mas.tool.tools import TOOLS

logger = logging.getLogger(__name__)

class MockCurator(Curator):
    
    def curate(self, G: TaskGraph) -> TaskGraph:
        logger.info("Curating...")

        agents = {}
        for node_id, attr in G.nodes(data=True):
            agent_type = self._select_agent_type(attr)

            args = {}
            if agent_type == "llm":
                args["model"] = self._select_model(attr)
                args["tools"] = self._select_tools(attr)
            
            agents[node_id] = create_agent(agent_type, attr=NodeAttr(**attr), **args)
        
        # set agents to each node in the graph
        nx.set_node_attributes(G, agents, name='agent')
    
        return G
    
    def _select_agent_type(self, attr: NodeAttr) -> str:
        # do something
        return "llm"
    
    def _select_model(self, attr: NodeAttr) -> str:
        # do something
        return "gpt-4o"
    
    def _select_tools(self, attr: NodeAttr) -> List[str]:
        # do something
        all_tools = list(TOOLS.keys())
        return all_tools