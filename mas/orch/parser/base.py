from abc import ABC, abstractmethod
import networkx as nx

from mas.graph import TaskGraph

class Parser(ABC):
    @abstractmethod
    def parse_from_path(self, filename) -> TaskGraph:
        raise NotImplementedError
    
    @abstractmethod
    def parse_from_string(self, config) -> TaskGraph:
        raise NotImplementedError
    
    def parse(self, config) -> TaskGraph:
        return self.parse_from_string(config)