from dataclasses import dataclass
from mas.graph.agent_task_graph import AgentTaskGraph
from mas.pool import Pool

@dataclass
class Curator:
    pool: Pool

    def curate(self, G: AgentTaskGraph) -> AgentTaskGraph:
        raise NotImplementedError