from agno.models.openai import OpenAIChat

from mas.model.pool import ModelPool

@ModelPool.register(name="test_openai", description="A simple test model wrapping OpenAIChat.")
class TestModel(OpenAIChat):
    def __init__(self):
        super().__init__(id="gpt-4o")
