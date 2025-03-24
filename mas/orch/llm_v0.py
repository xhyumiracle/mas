
from dataclasses import dataclass
from typing import Any
from mas.orch.base import Orchestrator

@dataclass
class LLMOrch(Orchestrator):
    user_request: str
    base_model: Any

    # dev note: no need for __init__ since we're using dataclass

    # def generate_by_messages(self, messages) -> AgentTaskGraph:
    #     self.call_llm(...)
    #     pass

    # def call_llm(self):
    #     pass