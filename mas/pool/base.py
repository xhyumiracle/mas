import importlib
import os
import logging
from abc import ABC
from typing import Dict, Generic, List, TypeVar, TypedDict

logger = logging.getLogger(__name__)
T = TypeVar('T')  # Generic type variable

class Entry(TypedDict):
    object: T
    description: str

import os

def path_to_module(path: str) -> str:
    """
    Convert a filesystem path to a Python package module path.

    Args:
        path: relative or absolute path like 'mas/tool/builtin'
        base: optional base directory to strip from path (e.g., project root)

    Returns:
        str: module import path like 'mas.tool.builtin'
    """
    return path.replace(os.path.sep, '.').rstrip('.py')

class Pool(ABC, Generic[T]):
    def __init__(self):
        self._registry: Dict[str, Entry] = {}

    def add(self, name: str, obj: T, description: str = ""):
        if name in self._registry:
            raise ValueError(f"Item '{name}' is already added.")
        self._registry[name] = Entry(object=obj, description=description)

    def get(self, name: str) -> T:
        if name not in self._registry:
            raise ValueError(f"Item '{name}' is not found in pool.")
        return self._registry[name]["object"]

    def describe(self, name: str) -> str:
        if name not in self._registry:
            raise ValueError(f"Item '{name}' is not found in pool.")
        return self._registry[name]["description"]

    def list(self) -> List[str]:
        return list(self._registry.keys())

    def all(self) -> Dict[str, T]:
        return {name: meta["object"] for name, meta in self._registry.items()}

    def all_names_and_descriptions(self) -> Dict[str, str]:
        return {name: meta["description"] for name, meta in self._registry.items()}

    def all_names(self) -> List[str]:
        return self.list()

    def all_descriptions(self) -> List[str]:
        return [meta["description"] for meta in self._registry.values()]

    def all_objects(self) -> List[T]:
        return [meta["object"] for meta in self._registry.values()]

    def count(self) -> int:
        return len(self._registry)
    
    def autoload(self, dir: str, module_name_prefix: str = None):
        ''' convert dir to module name prefix, e.g. mas/pool -> mas.pool '''
        if module_name_prefix is None:
            module_name_prefix = path_to_module(dir)
        logger.debug(f"Pool.autoload: dir from \"{dir}\" with model prefix \"{module_name_prefix}\"")
        
        for fname in os.listdir(dir):
            if fname.endswith(".py") and not fname.startswith("_"):
                module_name = f"{module_name_prefix.strip('.')}.{fname[:-3]}"
                importlib.import_module(module_name)
                logger.debug(f"Pool.autoload: Autoloaded {module_name}")
