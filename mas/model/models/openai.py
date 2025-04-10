import os
import base64
import json
import logging
from openai import OpenAI
        
from typing import Dict, Any, List, Sequence, Callable
from mas.model.base import Model
from mas.message import Message, Part, File, ToolCall

logger = logging.getLogger(__name__)


class Openai(Model):
    def __init__(self, id: str):
        self.id = id
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.available_tools = None

    async def run(self, messages: List[Message], tool_definitions: List[Dict[str, Any]] = None) -> Message:
        """Run the model with the given messages and tool definitions."""
        # Convert tool definitions to OpenAI format
        if tool_definitions:
            self.available_tools = self.format_available_tools(tool_definitions)
            
        # Convert messages to OpenAI format
        openai_messages = self.format_messages(messages)
        
        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.id,
            messages=openai_messages,
            tools=self.available_tools if self.available_tools else None
        )
        
        return Openai.parse_response(response)

    @staticmethod
    def format_available_tools(tool_definitions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format tool definitions into OpenAI-compatible format.
        
        Args:
            tool_definitions: List of tool definitions in standard format
            
        Returns:
            List of tool definitions in OpenAI format
        """
        openai_tools = []
        for tool_def in tool_definitions:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool_def["name"],
                    "description": tool_def["description"],
                    "parameters": tool_def["parameters"]
                }
            }
            openai_tools.append(openai_tool)
        return openai_tools
    
    @staticmethod
    def format_messages(messages: Sequence[Message]) -> List[Dict[str, Any]]:
        """Format a sequence of messages into OpenAI-compatible format.
        
        Args:
            messages: Sequence of messages to format
            
        Returns:
            List of formatted messages for OpenAI API
        """
        formatted_messages = []
        for msg in messages:
            formatted_messages.extend(Openai.format_message(msg))
        return formatted_messages

    @staticmethod
    def format_message(message: Message) -> List[Dict[str, Any]]:
        """Format a message into OpenAI-compatible format.
        
        Args:
            message: Message to format
            
        Returns:
            List of formatted messages for OpenAI API. For tool responses with multiple parts,
            this will return multiple messages, each with its own tool_call_id.
        """
        # For tool responses, split into multiple messages if needed
        if message.role == "tool":
            formatted_messages = []
            for part in message.parts:
                if part.tool_result:
                    formatted_message = {
                        "role": "tool",
                        "content": part.tool_result.content
                    }
                    if part.tool_result.tool_call_id:
                        formatted_message["tool_call_id"] = part.tool_result.tool_call_id
                    formatted_messages.append(formatted_message)
                else:
                    raise ValueError(f"Tool message should only have tool results, found {part}")
            return formatted_messages
        
        # For other messages, format as a single message
        formatted = {
            "role": message.role,
            "content": None
        }
        
        # Handle other message types
        content = []
        tool_calls = []
        
        for part in message.parts:
            if part.text:
                content.append({"type": "text", "text": part.text})
            elif part.file_data:
                file = part.file_data
                mime_type = file.mime_type or "application/octet-stream"
                
                # Check if file type is supported by OpenAI
                supported_types = {
                    # Images
                    "image/jpeg": "image_url",
                    "image/png": "image_url",
                    "image/gif": "image_url",
                    "image/webp": "image_url",
                    # Documents
                    "application/pdf": "file_url",
                    "text/plain": "file_url",
                    "application/msword": "file_url",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "file_url",
                    "application/vnd.ms-excel": "file_url",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "file_url",
                    "application/vnd.ms-powerpoint": "file_url",
                    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "file_url",
                    # Audio
                    "audio/mpeg": "audio_url",
                    "audio/mp4": "audio_url",
                    "audio/mpga": "audio_url",
                    "audio/m4a": "audio_url",
                    "audio/wav": "audio_url",
                    "audio/webm": "audio_url"
                }
                
                content_type = supported_types.get(mime_type)
                if not content_type:
                    logger.warning(f"Skipping unsupported file type: {mime_type}")
                    continue
                    
                if file.content:
                    content = base64.b64encode(
                        file.content if isinstance(file.content, bytes) 
                        else str(file.content).encode('utf-8')
                    ).decode('utf-8')
                    content.append({
                        "type": content_type,
                        f"{content_type}": {
                            "url": f"data:{mime_type};base64,{content}"
                        }
                    })
                elif file.uri:
                    content.append({
                        "type": content_type,
                        f"{content_type}": {
                            "url": file.uri
                        }
                    })
                else:
                    logger.warning(f"Skipping file without content or URI: {file.name}")
                    continue
            elif part.tool_call:
                tool_call = {
                    "type": "function",
                    "function": {
                        "name": part.tool_call.name,
                        "arguments": json.dumps(part.tool_call.arguments)
                    }
                }
                if part.tool_call.id:
                    tool_call["id"] = part.tool_call.id
                tool_calls.append(tool_call)
        
        # Set content based on parts
        if len(content) == 1 and content[0]["type"] == "text":
            formatted["content"] = content[0]["text"]
        elif content:
            formatted["content"] = content
        if tool_calls:
            formatted["tool_calls"] = tool_calls
        
        return [formatted]

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> Message:
        """Parse OpenAI response into Message format."""
        parts = []
        
        response_message = response.choices[0].message
        
        if response_message.content:
            if isinstance(response_message.content, str):
                parts.append(Part(text=response_message.content))
            elif isinstance(response_message.content, list):
                for content in response_message.content:
                    if content["type"] == "text":
                        parts.append(Part(text=content["text"]))
                    elif content["type"] == "image_url":
                        parts.append(Part(file_data=File(
                            uri=content["image_url"]["url"],
                            mime_type="image/jpeg"  # Default to JPEG if not specified
                        )))
        
        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]  # Take the first tool call
            parts.append(Part(tool_call=ToolCall(
                id=tool_call.id,
                name=tool_call.function.name,
                arguments=json.loads(tool_call.function.arguments)
            )))
        
        return Message(role="assistant", parts=parts)
    
    def create_tool_definitions(self, tools: List[Callable]) -> List[Dict[str, Any]]:
        """Create tool definitions from a list of wrapper functions.
        
        Args:
            wrapper_functions: List of wrapper functions to create tool definitions from
            
        Returns:
            List of tool definitions in OpenAI format
        """

        # Map Python types to JSON Schema types
        type_mapping = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
            None: "null"
        }
        
        tool_definitions = []

        for func in tools:
            import inspect
            sig = inspect.signature(func)
            
            # Create tool definition
            tool_def = {
                "name": func.__name__,
                "description": func.__doc__ or f"Tool {func.__name__}",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            
            # Add parameters from function signature
            for param_name, param in sig.parameters.items():
                if param_name == "self" or param_name == "_filemap":  # Skip internal parameters
                    continue
                    
                # Handle generic types like List[str]
                param_type = param.annotation
                if hasattr(param_type, '__origin__'):
                    if param_type.__origin__ is list:
                        item_type = param_type.__args__[0]
                        tool_def["parameters"]["properties"][param_name] = {
                            "type": "array",
                            "items": {
                                "type": type_mapping.get(item_type, "string")
                            }
                        }
                    else:
                        tool_def["parameters"]["properties"][param_name] = {
                            "type": type_mapping.get(param_type.__origin__, "string")
                        }
                else:
                    # Convert Python type to JSON Schema type
                    param_type = type_mapping.get(param_type, "string") if param_type != inspect.Parameter.empty else "string"
                    param_desc = ""
                    if param.default != inspect.Parameter.empty:
                        param_desc = f" (default: {param.default})"
                        
                    tool_def["parameters"]["properties"][param_name] = {
                        "type": param_type,
                        "description": param_desc
                    }
                
                if param.default == inspect.Parameter.empty:
                    tool_def["parameters"]["required"].append(param_name)
            
            tool_definitions.append(tool_def)
        return tool_definitions

    '''for test purpose
    def invoke(self):

        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        test_files = [
            File(filepath="/Users/xin/Downloads/gaia benchmark.pdf"),  # File from local path
            File(url="https://www.frouah.com/finance%20notes/Black%20Scholes%20PDE.pdf"),  # File from URL
        ]
        messages = [
            Message(role="system", content="You are a helpful assistant that can read PDFs and search the web"),
            Message(
                role="user",
                content=[
                    {"type": "input_text", "text": "Summarize the content of the pdfs, and search the web for the most up-to-date ranking of multi-agent systems based on how they perform on the gaia bencmark."}
                ] + file_to_message(test_files)
        )
    ]
        
        response = client.responses.create(
            model="gpt-4o",
            #tools=[{"type": "web_search_preview"}],
            input=messages
        )
        print(response.output_text)

    '''

class GPT4o(Openai):
    def __init__(self, id="gpt-4o"):
        super().__init__(id=id)


# def file_to_message(files: Sequence[File]) -> List[Dict[str, Any]]:
#     """
#     Convert a sequence of File objects to OpenAI-compatible message content by uploading files.

#     Args:
#         files (Sequence[File]): Sequence of File objects to process.
#         client (OpenAI): OpenAI client instance for file uploads.

#     Returns:
#         List[Dict[str, Any]]: List of message content entries with file references.

#     Raises:
#         ValueError: If file fetching or uploading fails.
#     """
#     file_messages = []
#     client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
#     for file in files:
#         try:
#             # Step 1: Fetch file content and validate
#             if file.url:
#                 content, mime_type = file.file_url_content
#                 if not content:
#                     raise ValueError(f"Failed to fetch content from URL: {file.url}")
#                 filename = file.url.split('/')[-1]
#                 logger.info(f"Successfully fetched file from URL: {file.url}")
#             elif file.filepath:
#                 path = Path(file.filepath) if isinstance(file.filepath, str) else file.filepath
#                 if not (path.exists() and path.is_file()):
#                     raise ValueError(f"File path does not exist or is not a file: {path}")
#                 with open(path, "rb") as f:
#                     content = f.read()
#                 if not content:
#                     raise ValueError(f"File is empty: {path}")
#                 filename = path.name
#                 logger.info(f"Successfully read file from path: {path}")
#             elif file.content:
#                 if not file.content:
#                     raise ValueError("File content is empty")
#                 content = file.content if isinstance(file.content, bytes) else str(file.content).encode('utf-8')
#                 filename = "uploaded_file" + (f".{file.mime_type.split('/')[-1]}" if file.mime_type else "")
#                 logger.info("Using provided file content")
#             else:
#                 logger.warning(f"Skipping file with no url, filepath, or content: {file}")
#                 continue
# # Step 2: Upload to OpenAI and validate response
#             file_obj = {"file": (filename, content), "purpose": "user_data"}
#             response = client.files.create(**file_obj)
            
#             if not hasattr(response, 'id') or not response.id:
#                 raise ValueError(f"File upload failed, no file_id returned for {filename}")
#             file_id = response.id
#             logger.info(f"Successfully uploaded file to OpenAI, file_id: {file_id}")

#             # Add file reference to message content
#             file_messages.append({
#                 "type": "input_file",
#                 "file": {"file_id": file_id}
#             })
#         except httpx.RequestError as e:
#             logger.error(f"Failed to fetch file: {e}")
#             raise ValueError(f"Failed to fetch file: {str(e)}")
#         except Exception as e:
#             logger.error(f"Failed to process or upload file: {e}")
#             raise ValueError(f"Failed to process or upload file: {str(e)}")

#     return file_messages
