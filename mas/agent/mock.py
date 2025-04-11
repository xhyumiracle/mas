from __future__ import annotations

from typing import Optional, Sequence
from mas.graph import NodeAttr
from mas.agent import Agent
from mas.message import Message, Part
class MockAgent(Agent):
    def __init__(self, id, node_attr: NodeAttr):
        super().__init__(id)
        
        self.name = node_attr.name
        self.prompt = node_attr.prompt
        self.profile = node_attr.profile
        self.model = node_attr.model
        self.input_formats = node_attr.input_formats
        self.output_formats = node_attr.output_formats
        self.tools = node_attr.tools

    async def _run(
        self,
        goal: Message,
        observations: Optional[Sequence[Message]],
    ) -> Message:
        return Message(role="assistant", parts=[Part(text=f"Hello, I am Agent[id={self.id}]), my goal is: {goal}")])