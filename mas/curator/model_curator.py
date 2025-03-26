import logging
from mas.curator.base import Curator
from mas.graph.agent_task_graph import AgentTaskGraph

logger = logging.getLogger(__name__)

class ModelCurator(Curator):
    def curate_model(self, model: str) -> str:
        # TODO: implement curation logic
        return model
    
    def curate(self, G: AgentTaskGraph) -> AgentTaskGraph:
        logger.info("Curating models... skipped")
        # for _, attr in G.nodes(data=True):
        #     self.curate_model(attr["model"])
        return G