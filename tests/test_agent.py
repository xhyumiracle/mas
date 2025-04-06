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
crawlee2 = toolpool.get(name='crawlee-singleloop')

#res = google_search('current weather in San Francisco')
#print(res)


agent = Agent(
    model=model,
    markdown=True,
    instructions='You are a helpful assistant that completes tasks given by the user and output the best possible results. You will make the best use of available tools and try until you reach a satisfactory answer.',
    tools=[crawlee2],
    show_tool_calls=True
)

# agent.print_response("Search for differences between openai responses API and chat completions API. Read and summarize the websites you found. For each url, tell me if you were able to access it, and if yes, what you read from it.")
agent.print_response("Search for differences between openai responses API and chat completions API. Show me python code that highlights the differences.")

