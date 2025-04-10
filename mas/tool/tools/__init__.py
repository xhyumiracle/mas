from typing import Dict, Callable, Literal, Sequence, Union
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.arxiv import ArxivTools
from agno.tools.youtube import YouTubeTools
from agno.tools.dalle import DalleTools
from agno.tools.website import WebsiteTools
from agno.tools.file import FileTools
from mas.tool.tools.youtubedownload import YouTubeDownloadTool
from mas.utils.tool import convert_agno
from mas.tool.tools.wikipedia import WikipediaTool
from mas.tool.tools.mock import MockTextToTextTool, MockTextToImageTool, MockImagesToVideoTool, MockImagesToAudioTool, MockAddAudioToVideoTool
from mas.tool.tools.googlesearch import GoogleSearchTool
from mas.tool.tools.urlreader import URLReaderTool
# from .urlreader import url_reader
# from .browseruse import browser_use
# from .crawleetool import crawlee_tool

ToolDefType = Dict[Literal["function", "description"], Union[Callable, str]]
ToolSetType = Dict[Literal["tools", "description"], Union[ToolDefType, str]]

TOOLS: Dict[str, Union[ToolDefType, ToolSetType]] = {}

TOOLS = (
    TOOLS 
    | MockTextToTextTool().to_dict()
    | MockTextToImageTool().to_dict()
    | MockImagesToVideoTool().to_dict()
    | MockImagesToAudioTool().to_dict()
    | MockAddAudioToVideoTool().to_dict()

    | YouTubeDownloadTool().to_dict()
    | GoogleSearchTool().to_dict()
    | URLReaderTool().to_dict()
    # | WikipediaTool().to_dict()
    | convert_agno(DuckDuckGoTools())
    | convert_agno(ArxivTools(), new_description="Search arXiv for a query and return the top articles.")
    # | convert_agno(YouTubeTools())
    | convert_agno(DalleTools(), new_description="Generate an image based on a text prompt.")
    # | convert_agno(WebsiteTools())
    # | convert_agno(FileTools())
)

"""
test tools in this way:
`pytest tests/tool/test_tool.py::test_googlesearch_tool -s`
"""

def get_callable_tools(tool_set: Union[str, Sequence[str]]) -> Sequence[Callable]:
    def _one_set(tool_set: str) -> Sequence[Callable]:
        if tool_set not in TOOLS:
            raise ValueError(f"Tool set {tool_set} not found")
        return [tool["function"] for tool in TOOLS[tool_set]["tools"].values()]
    
    if isinstance(tool_set, str):
        return _one_set(tool_set)
    elif isinstance(tool_set, Sequence):
        return [tool for tool_set in tool_set for tool in _one_set(tool_set)]