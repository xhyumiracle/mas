# model/models.py
from typing import List, Dict
from agno.models.base import Model

class ModelPool:
    def __init__(self, model_map: Dict[str, Model]):
        self.model_map = model_map

    def get_model_map(self) -> List[Model]:
        return self.model_map
    
    def get_model(self, model_name: str) -> Model:
        return self.model_map[model_name]
    
    def get_model_names(self) -> List[str]:
        return self.model_map.keys()
    
    def count(self) -> int:
        return len(self.model_map)
        
# # Singleton instance
# _model_pool_instance = None

# def get_model_pool(model_map=None) -> ModelPool:
#     global _model_pool_instance
#     if _model_pool_instance is None:
#         if model_map is None:
#             raise ValueError("First time initialization requires model_map")
#         _model_pool_instance = ModelPool(model_map=model_map)
#     return _model_pool_instance