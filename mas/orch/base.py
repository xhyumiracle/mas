from dataclasses import dataclass, field
from typing import Sequence, Optional, Union
from mas.message import Message, Part
from mas.graph.task_graph import TaskGraph
from abc import ABC, abstractmethod

@dataclass(kw_only=True)
class Orchestrator(ABC): 
    
    def generate(
        self, 
        query: Union[str, Message],
        historical_messages: Optional[Sequence[Message]]=[]
    ) -> TaskGraph:
        # assemble query to message
        user_message = query if type(query) == Message else Message(role="user", parts=[Part(text=query)]) 
        return self.generate_by_message(user_message, historical_messages)
    
    @abstractmethod
    def generate_by_message(
        self,
        user_message: Message,
        historical_messages: Optional[Sequence[Message]]=[]
    ) -> TaskGraph:
        raise NotImplementedError