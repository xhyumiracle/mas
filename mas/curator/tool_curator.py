
from typing import List
import logging
from mas.curator.base import Curator
from mas.graph.agent_task_graph import AgentTaskGraph

logger = logging.getLogger(__name__)

class ToolCurator(Curator):
    def remove_duplicated(self, tools: List[str]) -> List[str]:
        return list(set(tools))

    def curate_tools(self, tools: List[str]) -> List[str]:
        _tools = self.remove_duplicated(tools)
        return _tools
    
    def curate(self, G: AgentTaskGraph) -> AgentTaskGraph:
        logger.info("Curating tools... skipped")
        for _, attr in G.nodes(data=True):
            self.curate_tools(attr["tools"])
        return G