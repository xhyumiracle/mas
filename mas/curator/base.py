from dataclasses import dataclass
from abc import ABC, abstractmethod
from mas.graph.task_graph import TaskGraph

@dataclass
class Curator(ABC):
    @abstractmethod
    def curate(self, G: TaskGraph) -> TaskGraph:
        raise NotImplementedError