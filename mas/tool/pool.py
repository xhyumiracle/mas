from __future__ import annotations
import logging
from typing import Callable
from mas.agent.base import Agent
from mas.pool import Pool
from mas.pool.registry import RegistryContext
from mas.utils.path import relative_parent_to_root

logger = logging.getLogger(__name__)

class ToolPool(Pool[Callable]):
    _context: RegistryContext[ToolPool] = RegistryContext()

    @staticmethod
    def initialize() -> ToolPool:
        pool = ToolPool()
        
        ''' set this instance to global registry context and Agent class '''

        ToolPool._context.set(pool)
        Agent.set_tool_pool(pool)

        ''' autoload builtin tools '''
        
        pool.autoload()

        logger.info(f"ToolPool.initialize: Loaded {pool.count()} tools")


        return pool

    def autoload(self, dir: str = None, module_name_prefix: str = None): # "mas.tool.tools"
        tool_dir = relative_parent_to_root(__file__, "tools") if dir is None else dir
        super().autoload(tool_dir, module_name_prefix)
    
    @classmethod
    def register(cls, name: str, description: str = "") -> Callable[[Callable], Callable]:
        """
        Decorator to register a tool function into the active ToolPool context.

        Usage:
            @ToolPool.register(name="tool_name", description="desc")
            def my_tool(...):
                ...
        """
        def decorator(func: Callable):
            instance = cls._context.get()
            instance.add(name=name, obj=func, description=description)
            return func
        return decorator