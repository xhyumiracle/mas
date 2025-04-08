from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv
load_dotenv()
from browser_use import BrowserConfig
from browser_use.browser.browser import Browser


config = BrowserConfig(
    headless=True,
)

async def main():
    agent = Agent(
        browser=Browser(config=config),
        task="比较gpt4和gpt4o的性能",
        llm=ChatOpenAI(model="gpt-4o"),
    )
    await agent.run()

asyncio.run(main())