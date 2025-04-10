from unittest.mock import Mock
import asyncio

from mas.agent.base import Agent, IterativeAgent
from mas.agent.llm import LLMAgent
from mas.message import Message, Part
from mas.message.types import File, ToolCall, ToolResult
from mas.memory.filemap import FileMap
from mas.model.models.openai import GPT4o, Openai
from typing import List, Dict, Any
import pytest

from dotenv import load_dotenv
load_dotenv()

def test_llm_agent_with_tools():
    """Test LLMAgent with tool integration."""
    def mock_tool(text: str) -> str:
        return f"Processed: {text}"
    
    agent = LLMAgent(
        name="test_agent",
        model=GPT4o(),
        tools=[mock_tool],
        filemap=FileMap()
    )
    
    response = asyncio.run(agent.run_messages([
        Message(role="user", parts=[Part(text="Use mock_tool with text='test'")])
    ]))
    
    assert response.role == "assistant"
    assert "Processed: test" in response.parts[0].text


def test_llm_agent_file_conversion():
    """Test file reference conversion in LLMAgent."""
    result_file = File(name="result.jpg", mime_type="image/jpeg", content=[])
    result_file2 = File(name="result2.jpg", mime_type="image/jpeg", content=[])
    def mock_tool(file_uri: str, _filemap: FileMap) -> List[str]:
        result = result_file
        result2 = result_file2
        return [_filemap.add(result), _filemap.add(result2)]
    
    llm_agent = LLMAgent(
        name="test_agent",
        model=GPT4o(),
        tools=[mock_tool],
        filemap=FileMap()
    )

    # Test file reference conversion
    message = Message(
        role="user",
        parts=[
            Part(text="Here is the input file: "),
            Part(file_data=File(name="input.txt", mime_type="text/plain", uri="filemap://input.txt")),
            Part(text="please call mock_tool over it")
        ]
    )
    
    # Test act method
    result = asyncio.run(llm_agent.act(message, []))
    print("Result:\n", result.format())

    assert isinstance(result, Message)
    assert result.role == "assistant"
    assert len(result.parts) > 0
    assert result_file in [part.file_data for part in result.parts if part.file_data]
    assert result_file2 in [part.file_data for part in result.parts if part.file_data]
