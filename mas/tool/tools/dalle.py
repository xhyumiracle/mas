from agno.tools.dalle import DalleTools
from mas.tool.pool import ToolPool

ToolPool.register(
    name="dalle",
    description="Generate images from prompt using DALL-E-3"
)(DalleTools())