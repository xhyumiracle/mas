from agno.tools.youtube import YouTubeTools
from mas.tool.pool import ToolPool

ToolPool.register(
    name="youtube",
    description="Get information on a YouTube video, such as author, transcript, and video timestamps."
)(YouTubeTools())