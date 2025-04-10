from mas.tool.tools import TOOLS
from mas.tool.tools.youtubedownload import YouTubeDownloadTool
from mas.tool.tools.mock import MockTool

def test_duckduckgo_tool():
    """Test DuckDuckGo tool definition in TOOLS."""
    # Get the tool definition
    tool_def = TOOLS.get("duckduckgo").get("tools").get("duckduckgo_search")
    assert tool_def is not None, "DuckDuckGo tool not found in TOOLS"
    
    # Check required fields
    assert "function" in tool_def, "Tool definition missing function"
    assert "description" in tool_def, "Tool definition missing description"
    
    # run the tool
    print("tool_def", tool_def["function"]("usa"))
    
    # Print tool definition for inspection
    print("\nDuckDuckGo Tool Definition:")
    print(f"Description: {tool_def['description']}")
    print(f"Function: {tool_def['function'].__name__}")

def test_mock_tool():
    """Test mock tool definition in TOOLS."""
    # Get the tool definition
    toolkit_def = TOOLS.get("mock")
    assert toolkit_def is not None, "mock tool not found in TOOLS"
    
    # Check required fields
    assert "tools" in toolkit_def, "Tool definition missing function"
    assert "description" in toolkit_def, "Tool definition missing description"
    
    # Verify function matches
    assert toolkit_def["tools"]["mock_test"]["function"] == MockTool.mock_test, "Function does not match"
    
    # run the tool
    result = toolkit_def["tools"]["mock_test"]["function"]("Python programming language")
    print("\nmock Tool Result:")
    print(result)
    
    # Print tool definition for inspection
    print("\nmock Tool Definition:")
    print(f"Description: {toolkit_def['description']}")
    print(f"Function: {toolkit_def['tools']['mock_test']['function'].__name__}")

def test_googlesearch_tool():
    """Test GoogleSearch tool definition in TOOLS."""
    # Get the tool definition
    tool_def = TOOLS.get("google_search").get("tools").get("google_search")
    assert tool_def is not None, "GoogleSearch tool not found in TOOLS" 

    # run the tool
    result = tool_def["function"]("Python programming language")
    print("\nGoogleSearch Tool Result:")
    print(result)
    
    
    
def test():
    import pprint
    pprint.pprint(TOOLS)
    