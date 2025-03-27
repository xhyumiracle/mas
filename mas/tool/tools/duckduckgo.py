from agno.tools.duckduckgo import DuckDuckGoTools
from mas.tool.pool import ToolPool

ToolPool.register(
    name="duckduckgo",
    description="web search through duckduckgo"
)(DuckDuckGoTools())