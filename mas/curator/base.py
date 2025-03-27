from dataclasses import dataclass
from mas.graph.agent_task_graph import AgentTaskGraph

@dataclass
class Curator:
    def curate(self, G: AgentTaskGraph) -> AgentTaskGraph:
        raise NotImplementedError