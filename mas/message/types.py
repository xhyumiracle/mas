from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Any, Optional, Union, ClassVar
import re
import json

class File(BaseModel):
    """
    Represents a file reference used in messages (e.g. image, video, csv).
    Each file has a unique name identifier and URI for locating it, along with metadata
    about its type, size, and other properties.
    """
    name: str = Field(..., description="Human-readable filename, used as unique identifier")
    mime_type: Optional[str] = Field(None, description="MIME type of the file")
    uri: Optional[str] = Field(None, description="URI path to locate this file")
    content: Optional[Union[bytes, Any]] = Field(None, description="Raw content of the file (bytes or object)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional file metadata")

    placeholder_pattern: ClassVar[str] = r"<file>(.*?)</file>"

    def __init__(self, **data):
        super().__init__(**data)
        # If name is not provided, generate one based on mime_type
        if not data.get('name'):
            ext = self.mime_type.split('/')[-1]
            self.name = f"file.{ext}"

    def format(self) -> str:
        """Format the file information."""
        info = f"name={self.name}, mime_type={self.mime_type}"
        if self.uri:
            info += f", uri={self.uri}"
        if self.content:
            info += f", content_size={len(self.content) if isinstance(self.content, bytes) else 'object'}"
        if self.metadata:
            info += f", metadata={self.metadata}"
        return f"[File] {info}"
    
    def is_filemap(self) -> bool:
        return self.uri and self.uri.startswith("filemap://")
    
    # def placeholder(self, name: str = None, uri: str = None, mime_type: str = None) -> str:
    #     """Convert to a JSON-formatted placeholder string."""
    #     data = {
    #         "name": name if name else self.name,
    #         "uri": uri if uri else self.uri,
    #         "mime_type": mime_type if mime_type else self.mime_type
    #     }
    #     return f"<file>{json.dumps(data)}</file>"
    
    # @staticmethod
    # def placeholder_with_uri(uri: str) -> str:
    #     """Convert to a JSON-formatted placeholder string with a specific URI."""
    #     data = {
    #         "uri": uri,
    #     }
    #     return f"<file>{json.dumps(data)}</file>"
    # @classmethod)
    # def from_placeholder(cls, placeholder: str) -> "File":
    #     """Convert a JSON-formatted placeholder string to a File object."""
    #     # Extract JSON content between <file> tags
    #     match = re.search(cls.placeholder_pattern, placeholder)
    #     if not match:
    #         raise ValueError(f"Invalid file placeholder format, expected {cls(name='x', uri='y', mime_type='z').placeholder()} but got {placeholder}")
            
    #     try:
    #         data = json.loads(match.group(1))
    #         return cls(
    #             name=data.get("name"),
    #             uri=data.get("uri"),
    #             mime_type=data.get("mime_type")
    #         )
    #     except json.JSONDecodeError:
    #         raise ValueError(f"Invalid JSON in file placeholder: {placeholder}")

class Image(File):
    """
    Represents an image file.
    """
    def format(self) -> str:
        """Format the image information."""
        return super().format().replace("[File]", "[Image]")

class Video(File):
    """
    Represents a video file.
    """
    def format(self) -> str:
        """Format the video information."""
        return super().format().replace("[File]", "[Video]")

class Audio(File):
    """
    Represents an audio file.
    """
    def format(self) -> str:
        """Format the audio information."""
        return super().format().replace("[File]", "[Audio]")

class ToolCall(BaseModel):
    """
    Represents a single tool call in a conversation.
    Tool calls are used to invoke external functions or services with specific arguments.
    """
    name: str = Field(..., description="Name of the tool to call")
    arguments: Dict[str, Any] = Field(..., description="Arguments for the tool call")
    id: Optional[str] = Field(None, description="Unique identifier for tracking this call")

    def format(self) -> str:
        """Format the tool call information."""
        info = f"name={self.name}, arguments={self.arguments}"
        if self.id:
            info += f", id={self.id}"
        return info

class ToolResult(BaseModel):
    """
    Represents the result of a tool call.
    """
    content: str = Field(..., description="Result content from the tool call")
    name: Optional[str] = Field(None, description="Name of the tool that was called")
    tool_call_id: Optional[str] = Field(None, description="ID of the tool call this result corresponds to")

    def format(self) -> str:
        """Format the tool result information."""
        info = f"content={self.content}"
        if self.name:
            info = f"name={self.name}, " + info
        if self.tool_call_id:
            info += f", tool_call_id={self.tool_call_id}"
        return info

# Type aliases for better type hints
ToolCallOrDict = Union[ToolCall, Dict[str, Any]]
ToolCalls = List[ToolCallOrDict]


class Part(BaseModel):
    """
    A content block within a Message.

    Fields:
        text: Optional text block.
        file_data: Optional file reference (image, video, etc).
        tool_call: Optional tool call.
        tool_result: Optional tool result.
        metadata: Optional block-level info (e.g. timestamp, thought-type).
    """
    text: Optional[str] = Field(None, description="Text content of the part")
    file_data: Optional[File] = Field(None, description="File reference if this part contains a file")
    tool_call: Optional[ToolCall] = Field(None, description="Tool call in this part")
    tool_result: Optional[ToolResult] = Field(None, description="Tool result in this part")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for this part")

    def format(self) -> str:
        if self.text:
            return f"[Text] {self.text}"
        if self.tool_call:
            return f"[ToolCall] {self.tool_call.format()}"
        if self.tool_result:
            return f"[ToolResult] {self.tool_result.format()}"
        if self.file_data:
            return self.file_data.format()
        # if self.inline_data: # don't know what this is, can remove
        #     return f"[InlineData] {self.inline_data.get('mime_type', '?')} ({len(self.inline_data.get('data', ''))}B)"
        return "[EmptyPart]"

class Message(BaseModel):
    """
    Represents a structured message exchanged between agents/tools/models.

    Fields:
        role: Who produced this message (user, assistant, tool, system).
        parts: Ordered list of content parts (text, files, tool calls).
    """
    role: Literal["user", "assistant", "tool", "system"] = Field(..., description="The role of the message sender")
    parts: List[Part] = Field(default_factory=list, description="List of message parts")
    
    def get_tool_calls(self) -> List[ToolCall]:
        """Get all tool calls from the message parts."""
        return [p.tool_call for p in self.parts if p.tool_call is not None]

    def format(self) -> str:
        header = f"Message(role={self.role}, parts={len(self.parts)})"
        body = "\n".join([f"  - {p.format()}" for p in self.parts])
        return f"{header}\n{body}"
    
    def pprint(self):
        print(self.format())