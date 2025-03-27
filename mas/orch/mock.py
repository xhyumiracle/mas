from dataclasses import dataclass
from mas.graph.agent_task_graph import AgentTaskGraph
from mas.orch.base import Orchestrator
from mas.orch.parser.yaml_parser import Parser
from mas.orch.parser.yaml_parser import YamlParser

@dataclass
class MockOrch(Orchestrator):
    parser:Parser = YamlParser()
    
    def load(self, graph_cfg_path: str) -> AgentTaskGraph:
        graph = self.parser.parse_from_path(graph_cfg_path)
        return AgentTaskGraph(graph)
    
    ''' only a mock implementation '''
    def generate_by_message(self, user_message, historical_messages) -> AgentTaskGraph:
        return self.load(graph_cfg_path="tests/data/graph.0.yaml")
