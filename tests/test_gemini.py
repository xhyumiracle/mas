import requests, os
from agno.agent import Agent
from agno.media import Audio
from agno.models.google import Gemini
from mas.model.pool import ModelPool
from dotenv import load_dotenv
load_dotenv()

model = ModelPool.get("gemini")

agent = Agent(
    model=model,
    markdown=True,
)

url = "https://agno-public.s3.us-east-1.amazonaws.com/demo_data/QA-01.mp3"


agent.print_response(
    "What is this audio about?",
    audio=[Audio(url=url)],
    stream=True,
)
