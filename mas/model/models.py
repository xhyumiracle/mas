from agno.models.openai import OpenAIChat
from agno.models.google import Gemini

MODELS = {
    "gpt-4o": OpenAIChat(id="gpt-4o"),
    "gpt-3.5-turbo": OpenAIChat(id="gpt-3.5-turbo"),
    "gemini": Gemini(),
}