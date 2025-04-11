import asyncio
from mas.agent.factory import create_agent
from mas.graph.types import NodeAttr
from mas.memory.filemap import FileMap
from mas.message import Message
def test_create_agent_basic():
    """Test basic agent creation with GPT-4 and simple tools."""
    # Create a basic node attributes
    node_attr = NodeAttr(
        name="test_agent",
        input_formats=["text"],
        output_formats=["text"],
        prompt="You are a helpful assistant.",
        profile="You are a test agent.",
        model="gpt-4o",
        tools=["mock_text_to_text", "google_search"],  # Using simple tools for testing
        agent_type="llm"
    )

    filemap = FileMap()
    
    # Create the agent
    agent = create_agent(id=123, attr=node_attr, filemap=filemap)
    
    # Basic assertions
    assert agent is not None
    assert agent.name == "test_agent"
    
    # Test agent can process a simple message
    response = asyncio.run(agent.run("Hello, what's the weather in Tokyo?"))
    print("----------response", response)
    assert response is not None
    assert isinstance(response, Message) 