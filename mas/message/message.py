from dataclasses import dataclass
import json
from typing import List, Dict, Sequence, Optional, Union, Any
from pydantic import BaseModel
from agno.media import Audio, File, Image, Video

class Message(BaseModel):
    # system, user, assistant, or tool
    role: str
    # The contents of the message
    content: Optional[Union[List[Any], str]] = None
    # The func def of the tool calls
    tool_calls: Optional[List[Dict[str, Any]]] = None
    # Additional modalities
    audios: Optional[Sequence[Audio]] = None
    images: Optional[Sequence[Image]] = None
    videos: Optional[Sequence[Video]] = None
    files: Optional[Sequence[File]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Returns the message as a dictionary."""
        message_dict = {
            "role": self.role,
            "content": self.content,
            "tool_calls": self.tool_calls,
        }
        # Filter out None and empty collections
        message_dict = {
            k: v for k, v in message_dict.items() if v is not None and not (isinstance(v, (list, dict)) and len(v) == 0)
        }

        # Convert media objects to dictionaries
        if self.images:
            message_dict["images"] = [img.to_dict() for img in self.images]
        if self.audios:
            message_dict["audios"] = [aud.to_dict() for aud in self.audios]
        if self.videos:
            message_dict["videos"] = [vid.to_dict() for vid in self.videos]
        
        return message_dict
    
    def pprint(self):
        print(json.dumps(self.to_dict(), indent=2))
        
Messages = Optional[List[Union[Dict, Message]]]

def pprint_messages(messages: Messages) -> None:
    """Pretty print the Messages object."""
    if messages is None:
        print("No messages to display.")
    else:
        print("\n=======Messages=====\n")
        print(json.dumps([m.to_dict() for m in messages], indent=2))
        print("=======End=======\n")