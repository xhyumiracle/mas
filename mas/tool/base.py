from typing import Dict, Callable, List
from pydantic import BaseModel
from mas.utils.tool import parse_docstring

class Toolkit(BaseModel):
    name: str
    description: str
    tools: List[Callable]
    
    def to_dict(self) -> Dict:
        return {
            self.name: {
                "description": self.description,
                "tools": {
                    tool.__name__: {
                        "description": parse_docstring(tool.__doc__)[0], # or self.description,
                        "function": tool
                    }
                    for tool in self.tools
                }
            }
        }