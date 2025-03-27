from mas.model.pool import ModelPool
from mas.tool import ToolPool

def test_tool_pool():
    tool_pool = ToolPool().initialize(load_builtin=True, ext_dir="tests_artifacts/tools")
    print("Loaded tools:", tool_pool.list())
    print("Search result:", tool_pool.get("test_tool")("hi"))

def test_model_pool():
    model_pool = ModelPool().initialize(load_builtin=True, ext_dir="tests_artifacts/models")
    print("Loaded models:", model_pool.list())
    print("Test Model:", model_pool.get("test_openai"))
    # _agno_run(model_pool.get("test_model"))

def _agno_run(model_cls):
    import json
    from agno.agent import Agent, RunResponse
    from agno.models.openai import OpenAIChat
    from agno.tools.duckduckgo import DuckDuckGoTools

    agent = Agent(
        # model=OpenAIChat(id="gpt-4o"),
        model=model_cls(),
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