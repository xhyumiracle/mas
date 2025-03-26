from agno.tools.duckduckgo import DuckDuckGoTools
from mas.tool.pool import ToolPool

@ToolPool.register(
    name="duckduckgo_search",
    description="web search through duckduckgo"
)
def duckduckgo_search(query: str, max_results: int = 5) -> str:
    return DuckDuckGoTools().duckduckgo_search(query, max_results)


@ToolPool.register(
    name="duckduckgo_news",
    description="news search function through duckduckgo"
)
def duckduckgo_news(query: str, max_results: int = 5) -> str:
    return DuckDuckGoTools().duckduckgo_news(query, max_results)