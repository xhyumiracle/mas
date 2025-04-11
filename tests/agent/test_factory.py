import asyncio
from mas.agent.factory import create_agent
from mas.graph.types import NodeAttr
from mas.memory.filemap import FileMap
from mas.message import Message
def test_create_agent_basic():
    """Test basic agent creation with GPT-4 and simple tools."""
    # Create a basic node attributes
    node_attr = NodeAttr(
        id=1,
        input_modalities=["text"],
        output_modalities=["text"],
        task="You are a helpful assistant.",
    )

    args = {
        "profile": "You are a test agent.",
        "model": "gpt-4o",
        "tools": ["mock_text_to_text", "google_search"],  # Using simple tools for testing
    }

    
    # Create the agent
    agent = create_agent("llm", attr=node_attr, **args)
    
    # Basic assertions
    assert agent is not None
    assert agent.id == 1
    
    # Test agent can process a simple message
    response = asyncio.run(agent.run("Hello, what's the weather in Tokyo?"))
    print("----------response", response)
    assert response is not None
    assert isinstance(response, Message) 