from mas.utils.file import convert_files_in_structure
from mas.message.types import File
from mas.message import Message, Part
import pytest

def test_convert_files_in_nested_structure():
    """Test converting files in nested structures."""
    def replace_file(file: File) -> File:
        return File(name=f"processed_{file.name}", mime_type=file.mime_type)
    
    # Test data with nested structure
    data = {
        "files": [
            File(name="test1.txt", mime_type="text/plain"),
            File(name="test2.txt", mime_type="text/plain")
        ],
        "nested": {
            "doc": File(name="doc.txt", mime_type="text/plain")
        }
    }
    
    # Convert files
    result = convert_files_in_structure(data, replace_file)
    
    # Verify result
    assert result["files"][0].name == "processed_test1.txt"
    assert result["files"][1].name == "processed_test2.txt"
    assert result["nested"]["doc"].name == "processed_doc.txt"
    
    # Verify original data is unchanged
    assert data["files"][0].name == "test1.txt"
    assert data["nested"]["doc"].name == "doc.txt"

def test_convert_files_in_messages():
    """Test converting files in Message and Part objects."""
    def replace_file(file: File) -> File:
        return File(name=f"processed_{file.name}", mime_type=file.mime_type)
    
    # Test data with messages
    messages = [
        Message(
            role="user",
            parts=[
                Part(text="Hello"),
                Part(file_data=File(name="test.txt", mime_type="text/plain")),
                Part(tool_call=None)
            ]
        ),
        Message(
            role="assistant",
            parts=[
                Part(file_data=File(name="response.txt", mime_type="text/plain"))
            ]
        )
    ]
    
    # Convert files
    result = convert_files_in_structure(messages, replace_file)
    
    # Verify result
    assert result[0].role == "user"
    assert result[0].parts[0].text == "Hello"
    assert result[0].parts[1].file_data.name == "processed_test.txt"
    assert result[1].parts[0].file_data.name == "processed_response.txt"
    
    # Verify original data is unchanged
    assert messages[0].parts[1].file_data.name == "test.txt"
    assert messages[1].parts[0].file_data.name == "response.txt"

# def test_file_placeholder():
#     """Test converting file placeholders to File objects."""
#     # Test with different attribute orders
#     placeholder1 = '<file>{"name": "test.txt", "uri": "filemap://test.txt", "mime_type": "text/plain"}</file>'
#     placeholder2 = '<file>{"uri": "filemap://test.txt", "mime_type": "text/plain", "name": "test.txt"}</file>'
#     placeholder3 = '<file>{"mime_type": "text/plain", "name": "test.txt", "uri": "filemap://test.txt"}</file>'
    
#     # Test with missing optional attributes
#     placeholder4 = '<file>{"name": "test.txt", "uri": "filemap://test.txt"}</file>'
    
#     # Test with values containing spaces
#     placeholder5 = '<file>{"name": "test file.txt", "uri": "filemap://test file.txt", "mime_type": "text/plain"}</file>'
    
#     # Test with invalid format
#     placeholder6 = "<file>invalid_format</file>"
#     placeholder7 = "<file>{invalid json}</file>"
    
#     # Test valid placeholders
#     file1 = File.from_placeholder(placeholder1)
#     file2 = File.from_placeholder(placeholder2)
#     file3 = File.from_placeholder(placeholder3)
#     file4 = File.from_placeholder(placeholder4)
#     file5 = File.from_placeholder(placeholder5)
    
#     assert file1.name == "test.txt"
#     assert file1.uri == "filemap://test.txt"
#     assert file1.mime_type == "text/plain"
    
#     assert file2.name == "test.txt"
#     assert file2.uri == "filemap://test.txt"
#     assert file2.mime_type == "text/plain"
    
#     assert file3.name == "test.txt"
#     assert file3.uri == "filemap://test.txt"
#     assert file3.mime_type == "text/plain"
    
#     assert file4.name == "test.txt"
#     assert file4.uri == "filemap://test.txt"
#     assert file4.mime_type is None
    
#     assert file5.name == "test file.txt"
#     assert file5.uri == "filemap://test file.txt"
#     assert file5.mime_type == "text/plain"
    
#     # Test invalid placeholders
#     with pytest.raises(ValueError):
#         File.from_placeholder(placeholder6)
#     with pytest.raises(ValueError):
#         File.from_placeholder(placeholder7)