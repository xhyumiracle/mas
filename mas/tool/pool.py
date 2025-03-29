from __future__ import annotations
import logging
from typing import Callable, Optional, Union, Any
from mas.agent.base import Agent
from mas.pool import Pool
from mas.utils.path import relative_parent_to_root

logger = logging.getLogger(__name__)

ToolType = Union[Callable, Any]

class ToolPool(Pool[ToolType]):
    _global: Optional[ToolPool] = None

    @classmethod
    def initialize(cls, load_builtin=True, ext_dir: str = None) -> ToolPool:
        pool = ToolPool()
        
        ''' set this instance to global registry context and Agent class '''

        cls._global = pool
        Agent.set_tool_pool(pool)

        ''' autoload builtin tools '''
        
        
        if load_builtin:
            pool.autoload()
            logger.info(f"ToolPool.initialize: Loaded {pool.count()} builtin tools")

        ''' autoload external models '''

        if ext_dir is not None:
            pool.autoload(dir=ext_dir)
            logger.info(f"ToolPool.initialize: Loaded {pool.count()} external tools")

        return pool

    def autoload(self, dir: str = None, module_name_prefix: str = None): # "mas.tool.tools"
        tool_dir = relative_parent_to_root(__file__, "tools") if dir is None else dir
        super().autoload(tool_dir, module_name_prefix)
    
    @classmethod
    def register(cls, name: str, description: str = "") -> Callable[[ToolType], ToolType]:
        """
        Decorator to register a tool function / instance into the global ToolPool instace.

        Usage:
            @ToolPool.register(name="tool_name", description="desc")
            def my_tool(...):
                ...
            or
            ToolPool.register(name="tool_name", description="desc")(MyToolClass(...))
        """
        def decorator(obj: ToolType):
            cls._global.add(name=name, obj=obj, description=description)
            return obj
        return decorator
    
    @classmethod
    def set_global(cls, instance: ToolPool):
        cls._global = instance

    @classmethod
    def get_global(cls) -> ToolPool:
        if cls._global is None:
            logger.info("ToolPool._global is not initialized, initialize now")
            ToolPool.initialize()
        return cls._global