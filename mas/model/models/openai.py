from agno.models.openai import OpenAIChat
from mas.model.pool import ModelPool

@ModelPool.register(name="gpt-4o", description="OpenAI GPT-4O")
class GPT4O(OpenAIChat):
    def __init__(self):
        super().__init__(id="gpt-4o")


@ModelPool.register(name="gpt-3.5-turbo", description="OpenAI GPT-3.5-Turbo")
class GPT35Turbo(OpenAIChat):
    def __init__(self):
        super().__init__(id="gpt-3.5-turbo")
