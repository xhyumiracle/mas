from agno.tools.website import WebsiteTools 
from mas.tool.pool import ToolPool

ToolPool.register(
    name="read_url",
    description="reading website url content, return: Relevant documents from the website."
)(WebsiteTools())