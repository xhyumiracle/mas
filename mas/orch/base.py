from dataclasses import dataclass, field
from typing import Sequence, Optional, Union
from mas.message import Message
from mas.graph.agent_task_graph import AgentTaskGraph
from abc import ABC, abstractmethod

from mas.model.pool import ModelPool
from mas.tool.pool import ToolPool

@dataclass(kw_only=True)
class Orchestrator(ABC): 
    ''' load builtin models and tools by default '''
    model_pool: ModelPool = field(default_factory=ModelPool.get_global)
    tool_pool: ToolPool = field(default_factory=ToolPool.get_global)
    
    def generate(
        self, 
        query: Union[str, Message],
        historical_messages: Optional[Sequence[Message]]=[]
    ) -> AgentTaskGraph:
        # assemble query to message
        user_message = query if type(query) == Message else Message(role="user", content=query) 
        return self.generate_by_message(user_message, historical_messages)
    
    @abstractmethod
    def generate_by_message(
        self,
        user_message: Message,
        historical_messages: Optional[Sequence[Message]]=[]
    ) -> AgentTaskGraph:
        raise NotImplementedError