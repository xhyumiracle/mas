from agno.tools.arxiv import ArxivTools
from mas.tool.pool import ToolPool

ToolPool.register(
    name="arxiv",
    description="Arxiv API to browse research papers"
)(ArxivTools())