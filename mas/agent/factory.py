from mas.agent.base import Agent
from mas.agent.mock import MockAgent
from mas.agent.llm import LLMAgent
from mas.graph.types import NodeAttr
from mas.model.models import get_model_instance
from mas.tool.tools import get_callable_tools

def create_agent(agent_type: str, attr: NodeAttr, **kwargs) -> Agent:
    """
    Create an agent based on the agent_type specified in NodeAttr.
    
    Args:
        id: The unique identifier for the agent
        attr: NodeAttr containing agent configuration
        
    Returns:
        An instance of the appropriate Agent subclass
        
    Raises:
        ValueError: If agent_type is not supported
    """
    
    if agent_type == "llm":
        return LLMAgent(
            id=attr.id,
            input_modalities=attr.input_modalities,
            output_modalities=attr.output_modalities,
            profile=kwargs.get("profile", "You are a helpful assistant."),
            model=get_model_instance(kwargs.get("model", "gpt-4o")),
            tools=get_callable_tools(kwargs.get("tools", [])),
        )
    elif agent_type == "browseruse":
        # return BrowserAgent(
        # )
        pass
    elif agent_type == "mock": # for testing
        return MockAgent(
            node_attr=attr
        )
    else:
        raise ValueError(f"Unsupported agent type: {agent_type}") 