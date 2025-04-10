from typing import Any, Callable
from mas.message.types import File
from mas.message import Message, Part

def convert_files_in_structure(data: Any, converter: Callable[[File], Any]) -> Any:
    """Process all File instances in any nested structure and return a new structure.
    
    Args:
        data: Any nested structure that may contain File instances
        converter: Function to process each File instance and return a new value
        
    Returns:
        A new structure with all File instances replaced by their processed values
    """
    if isinstance(data, File):
        return converter(data)
    elif isinstance(data, Message):
        return Message(role=data.role, parts=convert_files_in_structure(data.parts, converter))
    elif isinstance(data, Part):
        new_part = data.model_copy()
        if new_part.file_data is not None:
            new_part.file_data = converter(new_part.file_data)
        return new_part
    elif isinstance(data, (list, tuple)):
        return type(data)(convert_files_in_structure(item, converter) for item in data)
    elif isinstance(data, dict):
        return {k: convert_files_in_structure(v, converter) for k, v in data.items()}
    else:
        return data
    