from dataclasses import dataclass
from typing import List, Literal, Optional

NodeId=int

@dataclass
class NodeAttr:
    name: str
    prompt: str
    profile: str
    model: str
    input_formats: List[Literal["text", "image", "video", "audio"]]
    output_formats: List[Literal["text", "image", "video", "audio"]]
    tools: Optional[List[str]]=None

@dataclass
class EdgeAttr:
    action: Optional[str]=None