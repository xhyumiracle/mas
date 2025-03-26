from __future__ import annotations
import logging
from typing import Callable
from agno.models.base import Model
from mas.agent.base import Agent
from mas.pool import Pool
from mas.pool.registry import RegistryContext
from mas.utils.path import relative_parent_to_root

logger = logging.getLogger(__name__)

class ModelPool(Pool[Model]):
    _context: RegistryContext[ModelPool] = RegistryContext()

    @staticmethod
    def initialize() -> ModelPool:
        pool = ModelPool()
        
        ''' set this instance to global registry context and Agent class '''

        ModelPool._context.set(pool)
        Agent.set_model_pool(pool)

        ''' autoload builtin models '''
        
        pool.autoload()

        logger.info(f"ToolPool.initialize: Loaded {pool.count()} tools")

        return pool

    def autoload(self, dir: str = None, module_name_prefix: str = None): # "mas.model.models"
        model_dir = relative_parent_to_root(__file__, "models") if dir is None else dir
        super().autoload(model_dir, module_name_prefix)
    
    @classmethod
    def register(cls, name: str, description: str = "") -> Callable[[Model], Model]:
        """
        Decorator to register a tool function into the active ToolPool context.

        Usage:
            @ModelPool.register(name="model_name", description="my own model")
            model_name = MyModel(...)
        """
        def decorator(model_cls: Model):
            ctx = cls._context.get()
            ctx.add(name=name, obj=model_cls, description=description)
            return model_cls
        return decorator