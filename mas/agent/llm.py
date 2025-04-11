import re
import inspect
from typing import Callable, List, Dict, Sequence, Optional, Any
from dataclasses import dataclass
import logging

from mas.agent.base import IterativeAgent
from mas.memory.filemap import FILEMAP_PROTOCOL_PREFIX, FileMap
from mas.message import Message, Part
from mas.message.types import File, ToolCall, ToolResult
from mas.model.base import Model
from mas.model.models.openai import GPT4o
from mas.utils.file import convert_files_in_structure

logger = logging.getLogger(__name__)

@dataclass
class LLMAgent(IterativeAgent):
    def __init__(
        self, 
        id: int,
        input_modalities=["text"],
        output_modalities=["text"],
        *,
        model: Model = GPT4o(),
        profile: Optional[str] = "You are a helpful assistant.",
        tools: Optional[List[callable]] = None,
    ):
        super().__init__(
            id=id,
            input_modalities=input_modalities,
            output_modalities=output_modalities
        )
        self.filemap = None # need to set later
        # self.profile = profile
        # self.tools = tools
        self.model = model
        self.tool_map = self._create_tool_dict(tools)
        self.system_msg = Message(role="system", parts=[
            Part(text=profile),
            Part(text=f"""<instruction>
When referencing any file (including {FILEMAP_PROTOCOL_PREFIX} URIs) in your response, you MUST follow these rules:

1. ALWAYS use the exact format: <file>{FILEMAP_PROTOCOL_PREFIX}your_file_uri</file>
2. NEVER use any other format like markdown image syntax ![text](uri) or direct URIs
3. The file reference MUST be wrapped in <file> tags
4. The uri parameter MUST be explicitly specified
5. This applies to ALL file references, regardless of file type or context

Example correct usage:
<file>{FILEMAP_PROTOCOL_PREFIX}_.jpg</file>

Example incorrect usage (DO NOT USE):
![Scene 3]({FILEMAP_PROTOCOL_PREFIX}_.jpg)
{FILEMAP_PROTOCOL_PREFIX}_.jpg
</instruction>""")])

        try:
            self.tool_definitions = self.model.create_tool_definitions(self._create_wrap_tools(tools))
        except NotImplementedError:
            self.tool_definitions = None
            logger.warning(f"Model {model.__class__.__name__} doesn't support tool calling")
    
    def set_filemap(self, filemap: FileMap):
        self.filemap = filemap
    
    async def run_messages(self, messages: Sequence[Message]) -> Message:
        """Core LLM interaction logic that processes a sequence of messages.
        
        Args:
            messages: Sequence of messages to process
        
        Returns:
            Response message from the LLM with tool call results
        """
        # Start with the initial messages
        current_messages = list(messages)
        
        while True:
            # Get response from model
            response = await self.model.run(current_messages, tool_definitions=self.tool_definitions)
            
            # If no tool calls, this is the final response
            if not any(part.tool_call for part in response.parts):
                return response
            
            # Collect all tool calls
            tool_calls = [part.tool_call for part in response.parts if part.tool_call]
            
            # Execute tool calls and get response
            tool_response = self._execute_tool_calls(tool_calls, self.tool_map, self.filemap)
            
            # Add both the assistant's message and tool response to conversation
            current_messages.append(response)
            current_messages.append(tool_response)

    async def act(self, goal: Message, observations: Sequence[Message]) -> Message:
        """Take an action by running the LLM on current observations and goal.
        
        Args:
            goal: The goal to achieve
            observations: Current observations/history
            
        Returns:
            The result of the action
        """
        
        logger.info(" > Observations:")
        [logger.info(message.format()) for message in observations]
        logger.info(" > System Message:")
        logger.info(self.system_msg.format())
        logger.info(" > Goal:")
        logger.info(goal.format())
        logger.info(" > Available tools:")
        logger.info("\n".join([tool_def["name"] for tool_def in self.tool_definitions]))
        
        messages = observations + [self.system_msg, goal]

        messages = [self._to_filemap_ref_message(msg) for msg in messages]
        
        result = await self.run_messages(messages)
        
        # convert result message parts to file objects
        result = self._from_filemap_ref_message(result)

        logger.info(" > Result:")
        logger.info(result.format())

        return result
        
    async def evaluate(self, goal: Message, observations: Sequence[Message]) -> bool:
        """Evaluate if the goal has been achieved.
        
        Args:
            goal: The goal to achieve
            observations: Current observations/history
            
        Returns:
            True if goal is achieved, False otherwise
        """
        # For now, we'll just return True
        # TODO: Implement proper goal evaluation using LLM
        return True


    @staticmethod
    def _create_tool_dict(tools: List[Callable]) -> Dict[str, Callable]:
        return {func.__name__: func for func in tools}

    @staticmethod
    def _create_wrap_tools(tools: List[Callable]) -> List[Callable]:
        """Convert function objects to tool definitions using OpenAI's format_tool_to_openai_function.
        
        Args:
            tools: List of tool function objects
            
        Returns:
            List of tool definitions in OpenAI format
        """
        
        wrapper_functions = []
        for func in tools:
            # Get the original signature
            original_sig = inspect.signature(func)
            
            # Skip _filemap parameter as it's internal
            parameters = {
                name: param
                for name, param in original_sig.parameters.items()
                if name != "_filemap"
            }
            
            # Create a wrapper function without _filemap parameter
            def wrapper(**kwargs):
                return func(**kwargs)
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            wrapper.__signature__ = inspect.Signature(
                parameters=list(parameters.values()),
                return_annotation=original_sig.return_annotation
            )
            wrapper_functions.append(wrapper)
        
        return wrapper_functions

    @staticmethod
    def _execute_tool_calls(tool_calls: List[ToolCall], tool_map: Dict[str, callable], filemap: FileMap) -> Message:
        """
        Execute multiple tool calls and return a tool response message.

        Args:
            tool_calls: List of tool calls to execute

        Returns:
            Message containing tool results
        """
        #TODO: enable tool return File objects, use convert_files_in_structure
        
        parts = []
        for tool_call in tool_calls:
            if not tool_call.name:
                raise ValueError("Tool name is required")

            logger.info(f" > Calling tool: {tool_call.name} with args: {tool_call.arguments}")

            try:
                tool = tool_map[tool_call.name]
            except KeyError:
                raise ValueError(f"Tool {tool_call.name} not found")


            args = tool_call.arguments.copy()
            sig = inspect.signature(tool)
            if '_filemap' in sig.parameters:
                args['_filemap'] = filemap
                
            try:
                result = tool(**{**args})
            except Exception as e:
                raise RuntimeError(f"Error executing tool {tool_call.name}: {str(e)}")

            parts.append(Part(tool_result=ToolResult(
                tool_call_id=tool_call.id,
                name=tool_call.name,
                content=str(result)
            )))
        
        return Message(role="tool", parts=parts)

    def _to_filemap_ref_message(self, msg: Message) -> Message:
        """Convert all File objects in a Message to FileMap formatted uris.
        
        Args:
            msg: Message to convert
            
        Returns:
            Message with all File objects converted to references
        """
        processed_parts = []
        for part in msg.parts:
            processed_parts.append(self._to_filemap_ref_part(part))
        return Message(role=msg.role, parts=processed_parts)
    
    def _from_filemap_ref_message(self, msg: Message) -> Message:
        """
        Convert all FileMap formatted uris in a Message back to File objects. 
        May split into multiple parts
        
        Args:
            msg: Message to convert
            
        Returns:
            Message with all FileMap formatted uris converted back to File objects
        """
        processed_parts = []
        for part in msg.parts:
            if part.text and "<file>" in part.text:
                processed_parts.extend(self._from_filemap_ref_part(part))
            else:
                processed_parts.append(part)
        return Message(role=msg.role, parts=processed_parts)
    
    def _to_filemap_ref_part(self, part: Part) -> Part:
        if part.file_data is not None and isinstance(part.file_data, File):
            return Part(text=self.filemap.wrap(part.file_data))
        return part
    
    def _from_filemap_ref_part(self, part: Part) -> List[Part]:
        # may contain multiple files, convert "aaa <file>name=xxx, uri=xxx, mime_type=xxx</file> ccc" to [Part(text="aaa "), Part(file_data=File(...)), Part(text="ccc")]
        parts = []
        text = part.text
        
        # Find all file references
        matches = list(re.finditer(File.placeholder_pattern, text))
        if not matches:
            return [part]
        
        # Split text by file references
        last_end = 0
        for match in matches:
            # Add text before file reference
            if match.start() > last_end:
                parts.append(Part(text=text[last_end:match.start()]))
            
            # Add file reference as File object
            file_placeholder = match.group(0)

            file = self.filemap.unwrap(file_placeholder)
            if file is None:
                raise ValueError(f"File {file_placeholder} not found in Filemap")
            
            parts.append(Part(file_data=file))
            
            last_end = match.end()
        
        # Add remaining text
        if last_end < len(text):
            parts.append(Part(text=text[last_end:]))
        
        # If no parts were created (e.g., text was just a file reference), return empty text part
        if not parts:
            parts.append(Part(text=""))
        
        return parts
