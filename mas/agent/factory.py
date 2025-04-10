from typing import Optional, Dict, Any
from mas.agent.base import Agent
# from mas.agent.browser import BrowserAgent
from mas.agent.mock import MockAgent
from mas.agent.llm import LLMAgent
from mas.graph.types import NodeAttr, NodeId
from mas.memory.filemap import FileMap
from mas.model.models import get_model_instance
from mas.tool.tools import get_callable_tools

def create_agent(id: NodeId, attr: NodeAttr, filemap: FileMap) -> Agent:
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
    agent_type = attr.agent_type or "llm"
    
    if agent_type == "llm":
        return LLMAgent(
            id=id,
            name=attr.name,
            input_modality=attr.input_formats,
            output_modality=attr.output_formats,
            model=get_model_instance(attr.model),
            profile=attr.profile,
            tools=get_callable_tools(attr.tools),
            # prompt=attr.prompt,
            filemap=filemap
        )
    elif agent_type == "browseruse":
        # return BrowserAgent(
        #     id=id,
        #     name=attr.name,
        #     prompt=attr.prompt,
        #     profile=attr.profile,
        #     model=attr.model,
        #     input_formats=attr.input_formats,
        #     output_formats=attr.output_formats,
        #     tools=attr.tools
        # )
        pass
    elif agent_type == "mock": # for testing
        return MockAgent(
            id=id,
            node_attr=attr
        )
    else:
        raise ValueError(f"Unsupported agent type: {agent_type}") 