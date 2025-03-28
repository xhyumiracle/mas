
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Union

import agno.agent as agno_agent

from mas.agent.base import Agent
from mas.message import Message
from mas.graph.types import NodeAttr, NodeId

@dataclass
class AgnoAgent(Agent):
    def __init__(self, id, node_attr: NodeAttr):
        super().__init__(id)
        self.agent = agno_agent.Agent(
            agent_id=str(id),
            name=node_attr.name,
            description=node_attr.profile,
            model=self.to_model(node_attr.model),
            tools=self.to_tools(node_attr.tools),
            # introduction=node_attr.profile,
            # add_history_to_messages=True,
            # num_history_responses=3,
        )

    def to_agno_message(self, m: Union[Dict, Message]) -> agno_agent.Message:
        return agno_agent.Message(
            role=m.role,
            content=m.content[0] if isinstance(m.content, list) else m.content,
            tool_calls=m.tool_calls, 
            audio=m.audios, # agno use audio not audios
            images=m.images, 
            videos=m.videos, 
            files=m.files
        )
    
    def from_agno_message(self, m: Union[Dict, agno_agent.Message]) -> Message:
        return Message(
            role=m.role,
            content=m.content,
            tool_calls=m.tool_calls, 
            audios=m.audio, # agno use audio not audios
            images=m.images, 
            videos=m.videos, 
            files=m.files
            # Other fields remain the same
        )
    
    def to_agno_messages(self, messages: Sequence[Union[Dict, Message]]) -> Sequence[Union[Dict, agno_agent.Message]]:
        return [self.to_agno_message(m) for m in messages]
    
    def from_agno_messages(self, messages: Sequence[Union[Dict, agno_agent.Message]]) -> Sequence[Union[Dict, Message]]:
        return [self.from_agno_message(m) for m in messages]
    
    def run_messages(self, messages: Sequence[Union[Dict, Message]]) -> Message:
        response: agno_agent.RunResponse = self.agent.run(messages=self.to_agno_messages(messages))
        return self.from_agno_messages(response.messages)[-1]

