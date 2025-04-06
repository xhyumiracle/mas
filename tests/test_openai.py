from mas.model.pool import ModelPool
from mas.tool import ToolPool
from agno.media import File
from agno.models.message import Message
from dotenv import load_dotenv
load_dotenv()


from agno.agent import Agent
from agno.media import Audio
from agno.models.google import Gemini
from agno.tools.googlesearch import GoogleSearchTools
from mas.model.pool import ModelPool
from mas.tool.pool import ToolPool
from dotenv import load_dotenv
load_dotenv()



modelpool = ModelPool.get_global()
GPT4o = modelpool.get(name="openai") # return the model class GPT4o(OpenAIChat)
model = GPT4o() # create an instance of that class

toolpool = ToolPool.get_global()
google_search = toolpool.get(name='google_search')
urlreader = toolpool.get(name='urlreader')

#res = google_search('current weather in San Francisco')
#print(res)


agent = Agent(
    model=model,
    markdown=True,
    instructions='You are a helpful assistant that completes tasks given by the user and output the best possible results. You will make the best use of available tools and try until you reach a satisfactory answer.',
    tools=[urlreader, google_search],
    show_tool_calls=True
)

agent.print_response("What's the current weather in San Francisco? Search for as many entries as you need to find the correct answer.")






'''#this works
model = ModelPool.get_model("gpt-4o")

test_files = [
    File(filepath="/Users/xin/Downloads/gaia benchmark.pdf"),  # File from local path
    File(url="https://www.frouah.com/finance%20notes/Black%20Scholes%20PDE.pdf"),  # File from URL
]
messages = [
    Message(role="system", content="You are a helpful assistant that can read PDFs"),
    Message(
        role="user",
        content="Summarize the content of the pdfs",
        files=test_files
        )
]
model.invoke()
'''

