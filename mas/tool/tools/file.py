from agno.tools.file import FileTools
from mas.tool.pool import ToolPool

ToolPool.register(
    name="file",
    description="Perform file actions such as saving, reading, or listing files in a given directory."
)(FileTools())