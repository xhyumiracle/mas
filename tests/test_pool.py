from mas.model.pool import ModelPool
from mas.tool import ToolPool
from agno.media import File
from agno.models.message import Message
from dotenv import load_dotenv
load_dotenv()

def test_tool_pool():
    tool_pool = ToolPool().get_global()
    tool_pool.autoload(dir="tests_artifacts/tools")
    print("Loaded tools:", tool_pool.list())
    print("Search result:", tool_pool.get("test_tool")("hi"))

def test_model_pool():
    model_pool = ModelPool().get_global()
    model_pool.autoload(dir="tests_artifacts/models")
    print("Loaded models:", model_pool.list())
    print("Test Model:", model_pool.get("test_openai"))
    # _agno_run(model_pool.get("test_model"))

def _agno_run():
    import json
    from agno.agent import Agent, RunResponse
    from agno.models.openai import OpenAIChat
    from agno.tools.duckduckgo import DuckDuckGoTools

    agent = Agent(
        model=OpenAIChat(id="gpt-4o"),
        
        description="You are an enthusiastic news reporter with a flair for storytelling!",
        tools=[DuckDuckGoTools()],
        show_tool_calls=True,
        markdown=True
    )

    # agent.print_response("What's happening in New York?", stream=True)
    response: RunResponse = agent.run("What's happening in New York?")

    def pprint_messages(messages) -> None:
        """Pretty print the Messages object."""
        if messages is None:
            print("No messages to display.")
        else:
            print("\n=======Messages=====\n")
            print(json.dumps([m.to_dict() for m in messages], indent=2))
            print("=======End=======\n")

    pprint_messages(response.messages)

'''
modelpool = ModelPool.get_global()
model_class = modelpool.get(name="gpt-4o")
model = model_class()
'''
model = ModelPool.get("gpt-4o")
# modelpool.get(name="gpt-4o") call is returning the TestModel class rather than an instance of TestModel


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
model.invoke(messages)
