from dataclasses import dataclass
from typing import List, Literal, Optional

NodeId=int

@dataclass
class NodeAttr:
    name: str
    input_formats: List[Literal["text", "image", "video", "audio"]]
    output_formats: List[Literal["text", "image", "video", "audio"]]
    prompt: str
    # optional depends on agent_type
    # although only used by llm agent, can keep required to ensure stability
    profile: str
    model: str
    tools: Optional[List[str]]=None
    agent_type: Literal["llm", "mock"]="llm"

@dataclass
class EdgeAttr:
    action: Optional[str]=None