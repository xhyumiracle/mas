import pytest
from typing import List

from mas.model.models.openai import Openai
from mas.message import Message, Part, File, ToolCall
import json


@pytest.fixture
def model():
    return Openai(id="gpt-4o")

def test_text_message(model):
    """Test basic text message formatting."""
    msg = Message(role="user", parts=[Part(text="hi")])
    result = model._format_message(msg)
    print('-------------------',result)
    assert len(result) == 1
    assert result[0] == {
        "role": "user",
        "content": "hi"
    }

def test_file_message(model):
    """Test message with image file content."""
    msg = Message(
        role="user",
        parts=[Part(file_data=File(
            name="test.jpg",
            content=b"test",
            mime_type="image/jpeg"
        ))]
    )
    result = model._format_message(msg)
    
    assert len(result) == 1
    assert result[0]["role"] == "user"
    assert result[0]["content"][0]["type"] == "image_url"
    assert "data:image/jpeg;base64" in result[0]["content"][0]["image_url"]["url"]

def test_non_image_file_message(model):
    """Test message with supported non-image file content."""
    msg = Message(
        role="user",
        parts=[Part(file_data=File(
            name="test.txt",
            content=b"test",
            mime_type="text/plain"
        ))]
    )
    result = model._format_message(msg)
    
    assert len(result) == 1
    assert result[0]["role"] == "user"
    assert result[0]["content"][0]["type"] == "file_url"
    assert "data:text/plain;base64" in result[0]["content"][0]["file_url"]["url"]

def test_unsupported_file_message(model):
    """Test message with unsupported file content should be skipped."""
    msg = Message(
        role="user",
        parts=[Part(file_data=File(
            name="test.xyz",
            content=b"test",
            mime_type="application/xyz"
        ))]
    )
    result = model._format_message(msg)
    
    assert len(result) == 1
    assert result[0]["role"] == "user"
    assert "content" not in result[0]  # No content because unsupported file was skipped


def test_tool_response_message(model):
    """Test formatting a tool response message."""
    msg = Message(
        role="tool",
        parts=[Part(tool_calls=[
            ToolCall(
                id="call1",
                name="test",
                arguments={"param": "value"},
                result="tool result"
            )
        ])]
    )
    result = model._format_message(msg)
    
    assert len(result) == 1
    assert result[0] == {
        "role": "tool",
        "tool_call_id": "call1",
        "content": "tool result"
    }

def test_model_run_with_tool_call(model):
    """Test model run with tool call and response."""
    
    # Run model with messages
    messages = [
        Message(role="user", parts=[Part(text="please call the test tool with param 123")])
    ]
    tool_definitions = [{
        "name": "test",
        "description": "Test tool",
        "parameters": {
            "type": "object",
            "properties": {
                "param": {"type": "integer"}
            }
        }
    }]
    
    response = model.run(messages, tool_definitions)
    # Verify response
    assert response.role == "assistant"
    assert len(response.parts) == 1
    assert response.parts[0].tool_calls[0].name == "test"
    assert response.parts[0].tool_calls[0].arguments == {"param": 123}

def test_multiple_tool_responses(model):
    """Test formatting a message with multiple tool responses."""
    msg = Message(
        role="tool",
        parts=[
            Part(tool_calls=[
                ToolCall(id="call1", name="test1", arguments={}, result="result1"),
                ToolCall(id="call2", name="test2", arguments={}, result="result2")
            ])
        ]
    )
    result = model._format_message(msg)
    
    assert len(result) == 2
    assert result[0] == {
        "role": "tool",
        "tool_call_id": "call1",
        "content": "result1"
    }
    assert result[1] == {
        "role": "tool",
        "tool_call_id": "call2",
        "content": "result2"
    }

def test_format_message_with_tool_calls():
    tool_call = ToolCall(
        name="test",
        arguments={"param": 123}
    )
    message = Message(
        role="assistant",
        parts=[Part(tool_call=tool_call)]
    )
    result = model._format_message(message)
    assert result["role"] == "assistant"
    assert result["tool_calls"][0]["function"]["name"] == "test"
    assert "param" in result["tool_calls"][0]["function"]["arguments"]

def test_parse_response_with_tool_calls():
    response = {
        "choices": [{
            "message": {
                "role": "assistant",
                "tool_calls": [{
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "test",
                        "arguments": json.dumps({"param": 123})
                    }
                }]
            }
        }]
    }
    response = model._parse_response(response)
    assert response.role == "assistant"
    assert response.parts[0].tool_call.name == "test"
    assert response.parts[0].tool_call.arguments == {"param": 123}

def test_create_tool_definitions(model):
    """Test creating tool definitions from Python functions."""
    def test_tool(text: str, image_list: List[str]) -> str:
        """Test tool that takes a text and a list of images."""
        return "test result"
    
    tool_defs = model.create_tool_definitions([test_tool])
    
    # Print the actual tool definition for debugging
    print("\nActual tool definition:")
    print(json.dumps(tool_defs[0], indent=2))
    
    assert len(tool_defs) == 1
    tool_def = tool_defs[0]
    assert tool_def["name"] == "test_tool"
    assert tool_def["description"] == "Test tool that takes a text and a list of images."
    assert tool_def["parameters"]["type"] == "object"
    assert "text" in tool_def["parameters"]["properties"]
    assert "image_list" in tool_def["parameters"]["properties"]
    assert tool_def["parameters"]["properties"]["image_list"]["type"] == "array"
    assert tool_def["parameters"]["properties"]["image_list"]["items"]["type"] == "string" 