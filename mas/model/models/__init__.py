from mas.model.base import Model
from .openai import GPT4o

MODELS = {
    "gpt-4o": {
        "class": GPT4o,
        "description": "OpenAI GPT-4o"
    }
}

def get_model_instance(model_name: str) -> Model:
    return MODELS[model_name]["class"]()