from mas.tool.pool import ToolPool

@ToolPool.register(
    name="test_tool",
    description="A simple test tool."
)
def test_tool(arg: str) -> str:
    return f"Test tool: arg - {arg}"