from agno.tools.duckduckgo import DuckDuckGoTools
from mas.tool.pool import ToolPool

ToolPool.register(
    name="duckduckgo",
    description="Web search for any common topic and knowledge, return clean text results, always a good choice"
)(DuckDuckGoTools())