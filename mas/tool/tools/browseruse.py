from mas.tool.pool import ToolPool
import asyncio
from langchain_openai import ChatOpenAI
from browser_use import Agent

@ToolPool.register(
    name="browser-use",
    description="LLM agent that automatically navigates websites and performs tasks"
)



async def browseruse(query: str, max_results: int = 5) -> str:
    task = "Add animation to the slides at https://docs.google.com/presentation/d/10iqi7qBQbKJQ3Evw0heJhiHFjhQosSN6z3yefBPRrZc/edit?usp=sharing Add a transition to all the slides, then make each text appear paragraph by paragraph, slowly after the previous animation."
    agent = Agent(
        #task="Go to https://orcid.org/0000-0003-0396-0333, count the number of pre-2024 works the person did",
        task = task,
        llm=ChatOpenAI(model="gpt-4o"),
    )
    await agent.run()

    