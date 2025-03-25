from abc import ABC
from dataclasses import dataclass
from typing import TypeVar, Generic, List, Dict

T = TypeVar('T')  # Generic type variable

@dataclass
class Pool(ABC, Generic[T]):
    map: Dict[str, T]

    def get_map(self) -> Dict[str, T]:
        return self.map
    
    def get(self, key: str) -> T:
        return self.map[key]
    
    def get_keys(self) -> List[str]:
        return self.map.keys()
    
    def count(self) -> int:
        return len(self.map)