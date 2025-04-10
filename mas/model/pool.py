from __future__ import annotations
import logging
from typing import Callable, Optional, Type
from typing_extensions import deprecated
from agno.models.base import Model
from mas.agent.base import Agent
from mas.pool import Pool
from mas.utils.path import relative_parent_to_root

logger = logging.getLogger(__name__)

ModelType = Type[Model]

@deprecated("use direct import instead")
class ModelPool(Pool[ModelType]):
    _global: Optional["ModelPool"] = None

    @classmethod
    def initialize(cls, load_builtin=True, ext_dir: str = None) -> ModelPool:
        if cls._global is not None:
            return cls._global
        
        pool = cls()
        
        ''' set this instance to global registry context and Agent class '''
        cls._global = pool

        ''' autoload builtin models '''
        
        if load_builtin:
            pool.autoload()
            logger.info(f"ModelPool.initialize: Loaded {pool.count()} builtin models")

        ''' autoload external models '''

        if ext_dir is not None:
            pool.autoload(dir=ext_dir)
            logger.info(f"ModelPool.initialize: Loaded {pool.count()} external models")

        return pool

    def autoload(self, dir: str = None, module_name_prefix: str = None):
        model_dir = relative_parent_to_root(__file__, "models") if dir is None else dir
        logger.debug(f"Autoloading models from: {model_dir}")
        super().autoload(model_dir, module_name_prefix)
        logger.debug(f"After autoload, model count: {self.count()}")
    
    @classmethod
    def register(cls, name: str, description: str = "") -> Callable[[ModelType], ModelType]:
        """
        Decorator to register a model class into the global ModelPool instace.

        Usage:
            @ModelPool.register(name="model_name", description="my own model")
            model_name = MyModel(...)
        """
        def decorator(model_cls: ModelType):
            cls._global.add(name=name, obj=model_cls, description=description)
            return model_cls
        return decorator
    
    @classmethod
    def set_global(cls, instance: ModelPool):
        cls._global = instance

    @classmethod
    def get_global(cls) -> ModelPool:
        if cls._global is None:
            logger.info("ModelPool._global is not initialized, initializing now")
            ModelPool.initialize()  # This will set cls._global
        return cls._global
    
    @classmethod
    def get_model(cls, name):
        pool = cls.get_global()
        model_class = Pool.get(pool, name)  # Explicitly call Pool.get()
        if model_class is None:
            raise ValueError(f"No model found with name '{name}'")
        return model_class()
    # model = ModelPool.get("gpt-4o")