from agno.tools.website import WebsiteTools 
from mas.tool.pool import ToolPool

@ToolPool.register(
    name="read_url",
    description="reading website url content, return: Relevant documents from the website."
)
def read_url(url: str) -> str:
    return WebsiteTools().read_url(url)

# didn't use WebsiteTools().add_website_to_knowledge_base