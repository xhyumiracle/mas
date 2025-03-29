from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv
load_dotenv()

#pip install browser-use
#playwright install chromium
async def main():
    agent = Agent(
        #task="Go to https://orcid.org/0000-0003-0396-0333, count the number of pre-2024 works the person did",
        task = '''Add animation to the slides at https://docs.google.com/presentation/d/10iqi7qBQbKJQ3Evw0heJhiHFjhQosSN6z3yefBPRrZc/edit?usp=sharing Add a transition to all the slides, then make each text appear paragraph by paragraph, after the previous animation. 
        To do this you must first click on each paragraph of text (excluding titles), then choose add animation and check the by paragpraph box. If prompted to sign in, use hollaiwood2025@gmail.com with apssword Hollaiwood1234
        ''',
        llm=ChatOpenAI(model="gpt-4o"),
    )
    await agent.run()

asyncio.run(main())