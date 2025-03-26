from agno.tools.wikipedia import WikipediaTools
from mas.tool.pool import ToolPool

@ToolPool.register(
    name="search_wikipedia",
    description="xxx"
)
def search_wikipedia(query: str) -> str:
    return WikipediaTools().search_wikipedia(query)
