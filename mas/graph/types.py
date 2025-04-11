from dataclasses import dataclass
from typing import List, Literal, Optional
from mas.agent.base import Agent

NodeId=int

@dataclass
class NodeAttr:
    id: NodeId
    task: str
    input_modalities: List[Literal["text", "image", "video", "audio"]]
    output_modalities: List[Literal["text", "image", "video", "audio"]]
    # profile: str
    # model: str
    # tools: Optional[List[str]]=None
    # agent_type: Literal["llm", "mock"]="llm"
    # set in step 2 curation
    agent: Optional[Agent]=None

@dataclass
class EdgeAttr:
    label: Optional[str]=None