
from agno.models.google.gemini import Gemini
from mas.model.pool import ModelPool

@ModelPool.register(name="gemini", description="Gemini")
class Gemini(Gemini):
    def __init__(self):
        super().__init__(id="gemini-2.0-flash")
