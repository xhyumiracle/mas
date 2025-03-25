
from typing import List
import logging
from mas.curator.base import Curator
from mas.graph.agent_task_graph import AgentTaskGraph


class ToolCurator(Curator):
    def curate_tools(self, tools: List[str]) -> List[str]:
        # TODO: implement curation logic
        return tools
    
    def curate(self, G: AgentTaskGraph) -> AgentTaskGraph:
        logging.info("Curating tools... skipped")
        # for _, attr in G.nodes(data=True):
        #     self.curate_tools(attr["tools"])
        return G