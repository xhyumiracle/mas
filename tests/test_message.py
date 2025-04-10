from mas.message import Message, Part
from mas.message.types import File, Image, Video, Audio, ToolCall

def test_message_basic():
    # Test basic text message
    m = Message(
        role="user",
        parts=[Part(text="Hello, world!")]
    )
    print(m.format())
    assert m.role == "user"
    assert len(m.parts) == 1
    assert m.parts[0].text == "Hello, world!"
    assert "Hello, world!" in m.format()

def test_message_with_file():
    # Test message with a file
    file = File(
        id="file1",
        uri="https://example.com/file.txt",
        mime_type="text/plain",
        name="test.txt"
    )
    print(file.placeholder())
    m = Message(
        role="user",
        parts=[Part(file_data=file)]
    )
    print(m.format())
    assert m.role == "user"
    assert len(m.parts) == 1
    assert m.parts[0].file_data == file
    assert "file.txt" in m.format()

def test_message_with_image():
    # Test message with an image
    image = Image(
        id="img1",
        uri="https://example.com/image.jpg",
        mime_type="image/jpeg",
        name="test.jpg"
    )
    m = Message(
        role="user",
        parts=[Part(file_data=image)]
    )
    print(m.format())
    assert m.role == "user"
    assert len(m.parts) == 1
    assert m.parts[0].file_data == image
    assert "image.jpg" in m.format()

def test_message_with_multiple_parts():
    # Test message with multiple parts
    text_part = Part(text="Here are some files:")
    file = File(
        id="file1",
        uri="https://example.com/file.txt",
        mime_type="text/plain",
        name="test.txt"
    )
    file_part = Part(file_data=file)
    
    m = Message(
        role="user",
        parts=[text_part, file_part]
    )
    print(m.format())
    assert m.role == "user"
    assert len(m.parts) == 2
    assert m.parts[0] == text_part
    assert m.parts[1] == file_part
    assert "Here are some files" in m.format()
    assert "test.txt" in m.format()

def test_message_with_tool_calls():
    tool_call = ToolCall(
        name="test_tool",
        arguments={"param": "value"}
    )
    m = Message(
        role="assistant",
        parts=[Part(tool_call=tool_call)]
    )
    assert m.role == "assistant"
    assert len(m.parts) == 1
    assert m.parts[0].tool_call == tool_call


