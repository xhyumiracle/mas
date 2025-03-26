from dataclasses import dataclass
from typing import Sequence, Optional
from mas.message import Message
from mas.graph.agent_task_graph import AgentTaskGraph
from abc import ABC, abstractmethod

from mas.model.pool import ModelPool
from mas.tool.pool import ToolPool

@dataclass(kw_only=True)
class Orchestrator(ABC): 
    ''' load builtin models and tools by default '''
    model_pool: ModelPool = ModelPool.initialize()
    tool_pool: ToolPool = ToolPool.initialize()
    
    def generate(
        self, 
        query: Optional[str] = None, 
        *, 
        message: Optional[Message] = None,
        messages: Optional[Sequence[Message]]=[]
    ) -> AgentTaskGraph:        
        if messages is None:
            messages = []

        # append message
        if message is not None:
            messages.append(message)
        
        # append query to the last
        if query is not None:
            messages.append(Message(role="user", content=query))
        
        if messages is None:
            return None
        
        return self.generate_by_messages(messages)
    
    @abstractmethod
    def generate_by_messages(self, messages: Sequence[Message]) -> AgentTaskGraph:
        raise NotImplementedError