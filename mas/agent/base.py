from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Sequence, Optional, Union
from agno.models.base import Model
from agno.tools import Toolkit

from mas.message import Message
from mas.graph.types import NodeId
from mas.model import ModelPool
from mas.tool import ToolPool

# enforce setting id
@dataclass
class Agent(ABC):
    id: NodeId
    _model_pool: ModelPool = None  # Class variable, shared across subclasses
    _tool_pool: ToolPool = None  # Class variable, shared across subclasses

    @classmethod
    def set_model_pool(cls, model_pool: ModelPool):
        cls._model_pool = model_pool

    @classmethod
    def set_tool_pool(cls, tool_pool: ToolPool):
        cls._tool_pool = tool_pool

    @classmethod
    def get_model_pool(cls) -> ModelPool:
        if cls._model_pool is None:
            raise ValueError("ModelPool not set. Call set_model_pool first.")
        return cls._model_pool
    
    @classmethod
    def get_tool_pool(cls) -> ToolPool:
        if cls._tool_pool is None:
            raise ValueError("ToolPool not set. Call set_tool_pool first.")
        return cls._tool_pool
    
    @classmethod
    def to_model(cls, model_str) -> Model:
        return cls.get_model_pool().get(model_str)
    
    @classmethod
    def to_tools(cls, tool_str_list: List[str]) -> Optional[List[Toolkit]]:
        if tool_str_list is None:
            return None
        return [cls.get_tool_pool().get(tool_str) for tool_str in tool_str_list]
    
    @abstractmethod
    def run_messages(self, messages: Sequence[Union[Dict, Message]]) -> Message:
        raise NotImplementedError
    
    def run(
        self,
        message: Optional[Union[str, List, Dict, Message]] = None,
        *,
        messages: Optional[Sequence[Union[Dict, Message]]] = [],
        # stream: Literal[False] = False,
        # audios: Optional[Sequence[Audio]] = None,
        # images: Optional[Sequence[Image]] = None,
        # videos: Optional[Sequence[Video]] = None,
        # files: Optional[Sequence[File]] = None,
    ) -> Message:
        if messages is None:
            messages = []

        # append message
        if message is not None:
            messages.append(message)

        return self.run_messages(messages=messages)
