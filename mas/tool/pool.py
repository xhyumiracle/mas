from typing import List, Dict
from agno.tools import Toolkit

class ToolPool:
    def __init__(self, tool_map: Dict[str, Toolkit]):
        self.tool_map = tool_map

    def get_tool_map(self) -> List[Toolkit]:
        return self.tool_map
    
    def get_tool(self, tool_name: str) -> Toolkit:
        return self.tool_map[tool_name]
    
    def get_tool_names(self) -> List[str]:
        return self.tool_map.keys()
    
    def count(self) -> int:
        return len(self.tool_map)


# # Singleton instance
# _tool_pool_instance = None

# def get_tool_pool(tool_map=None) -> ToolPool:
#     global _tool_pool_instance
#     if _tool_pool_instance is None:
#         if tool_map is None:
#             raise ValueError("First time initialization requires tool_map")
#         _tool_pool_instance = ToolPool(tool_map=tool_map)
#     return _tool_pool_instance