from __future__ import annotations

from typing import Optional, Sequence
from mas.graph.types import NodeAttr
from mas.agent import Agent
from mas.message import Message, Part
class MockAgent(Agent):
    def __init__(self, node_attr: NodeAttr):
        super().__init__(id=node_attr.id,
                         input_modalities=node_attr.input_modalities,
                         output_modalities=node_attr.output_modalities)

    async def _run(
        self,
        goal: Message,
        observations: Optional[Sequence[Message]],
    ) -> Message:
        return Message(role="assistant", parts=[Part(text=f"Hello, I am Agent[id={self.id}]), my goal is: {goal}")])