
from agno.models.google.gemini import Gemini
from mas.model.pool import ModelPool

@ModelPool.register(name="gemini", description="Gemini")
class TestModel(Gemini):
    pass
