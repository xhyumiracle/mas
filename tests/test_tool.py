from mas.tool import ToolPool
from mas.graph.types import NodeAttr

def test_to_tool():
    from mas.agent import MockAgent

    ToolPool().get_global() # load builtin tools
    agent = MockAgent(id=1, node_attr=NodeAttr(name="test", prompt="test", profile="test", model="gpt-4o", tools=["duckduckgo"], input_formats=["text"], output_formats=["text"]))
    print(agent.to_tools(["duckduckgo"]))