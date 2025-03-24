from abc import ABC, abstractmethod
import networkx as nx

from mas.graph import AgentTaskGraph

class Parser(ABC):
    @abstractmethod
    def parse_from_path(self, filename) -> AgentTaskGraph:
        raise NotImplementedError
    
    @abstractmethod
    def parse_from_string(self, config) -> AgentTaskGraph:
        raise NotImplementedError
    
    def parse(self, config) -> AgentTaskGraph:
        return self.parse_from_string(config)