import re
from typing import Dict, Optional, Tuple
from inspect import getdoc
from agno.tools import Toolkit

def normalize_whitespace(text: str) -> str:
    """Replace multiple spaces with a single space."""
    return re.sub(r'\s+', ' ', text)

def parse_docstring(doc: Optional[str]) -> Tuple[str, str]:
    """Parse docstring into description and instructions parts."""
    if not doc:
        return "", ""
    parts = doc.strip().split("\n", 1)
    return normalize_whitespace(parts[0].strip()), normalize_whitespace(parts[1].strip()) if len(parts) > 1 else ""

def convert_agno(agno_toolkit: Toolkit, new_name: str = None, new_description: str = None) -> Dict[str, callable]:
    return {
        new_name or agno_toolkit.name: {
            "description": new_description or parse_docstring(agno_toolkit.__doc__)[0],
            "tools": {
                func_name: {
                    "function": func.entrypoint,
                    "description": description,
                    # "instructions": instructions,
                }
                for func_name, func in agno_toolkit.functions.items()
                for description, instructions in [parse_docstring(getdoc(func.entrypoint))]
            }
        }
    }