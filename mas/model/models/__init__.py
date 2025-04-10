from mas.model.base import Model
from .openai import GPT4o

MODELS = {
    "gpt-4o": {
        "class": GPT4o,
        "description": "GPT-4o is the latest and most powerful model from OpenAI, offering advanced language understanding and generation capabilities."
    }
}

def get_model_instance(model_name: str) -> Model:
    return MODELS[model_name]["class"]()