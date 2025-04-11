from dataclasses import dataclass
from mas.graph.task_graph import TaskGraph
from mas.orch.base import Orchestrator
from mas.orch.parser import YamlParser

@dataclass
class MockOrch(Orchestrator):
    
    def load(self, graph_cfg_path: str) -> TaskGraph:
        parser = YamlParser()
        graph = parser.parse_from_path(graph_cfg_path)
        return TaskGraph(graph)
    
    ''' only a mock implementation '''
    def generate_by_message(self, user_message, historical_messages) -> TaskGraph:
        return self.load(graph_cfg_path="tests/data/graph.0.yaml")
