from typing import Dict, Optional, Iterator
from mas.message import File
import logging
import re
logger = logging.getLogger(__name__)

FILEMAP_PROTOCOL_PREFIX = "filemap://"

#TODO: use Storage instead of dict
class FileMap:
    """A mapping of file identifiers to file objects."""
    
    def __init__(self):
        self._files: Dict[str, File] = {}
        self._name_counts: Dict[str, int] = {}  # Track how many times each base name is used
        
    def add(self, file: File) -> str:
        """Add a file to the map.
        
        If a file with the same name already exists, a number suffix will be added
        to the new file's name (e.g., 'file.txt' -> 'file(1).txt').
        """
        base_name = file.name
        if base_name in self._files:
            # Get the current count for this base name
            count = self._name_counts.get(base_name, 1)
            # Split name and extension
            name_parts = base_name.rsplit('.', 1)
            if len(name_parts) == 2:
                name, ext = name_parts
                new_name = f"{name}({count}).{ext}"
            else:
                new_name = f"{base_name}({count})"
            # Update the file's name
            file.name = new_name
            # Increment the count
            self._name_counts[base_name] = count + 1
            logger.warning(f"File name '{base_name}' already exists, using '{new_name}' instead")
        
        self._files[file.name] = file
        # Initialize count if this is the first time we see this base name
        if base_name not in self._name_counts:
            self._name_counts[base_name] = 1
        
        return self.to_uri(file.name)
            
    def get_by_name(self, name: str) -> Optional[File]:
        """Get a file by its name."""
        file = self._files.get(name)
        if file is None:
            raise ValueError(f"File {name} not found")
        return file
    
    def get_by_uri(self, uri: str) -> Optional[File]:
        """Get a file by its URI."""
        if not self.is_protocol_uri(uri):
            raise ValueError(f"Invalid URI: {uri}")
        file = self._files.get(uri.replace(FILEMAP_PROTOCOL_PREFIX, ""))
        if file is None:
            raise ValueError(f"File {uri} not found")
        return file
    
    def remove(self, name: str) -> None:
        """Remove a file by its name."""
        if name in self._files:
            del self._files[name]
            # Update the count for the base name
            base_name = name.split('(')[0]  # Remove any suffix
            if base_name in self._name_counts:
                self._name_counts[base_name] -= 1
                if self._name_counts[base_name] == 0:
                    del self._name_counts[base_name]
                    
    def clear(self) -> None:
        """Clear all files from the map."""
        self._files.clear()
        self._name_counts.clear()
    
    def is_protocol_uri(self, uri: str) -> bool:
        """Check if a file exists in the map."""
        return uri.startswith(FILEMAP_PROTOCOL_PREFIX)
    
    def to_uri(self, name: str) -> str:
        """Get the URI of a file."""
        return f"{FILEMAP_PROTOCOL_PREFIX}{name}"
    
    @staticmethod
    def to_placeholder(uri: str) -> str:
        """Wrap a uri to a placeholder."""
        return f"<file>{uri}</file>"
    
    @staticmethod
    def from_placeholder(placeholder: str) -> Optional[str]:
        """Unwrap a placeholder back to uri."""
        match = re.search(r'^<file>(.*?)</file>$', placeholder.strip())
        if match is None:
            raise ValueError(f"Invalid placeholder: {placeholder}")
        return match.group(1) 
    
    def wrap(self, file: File) -> str:
        """Add a file and wrap its uri in a placeholder."""
        return self.to_placeholder(self.add(file))
    
    def unwrap(self, placeholder: str) -> Optional[File]:
        """Unwrap a placeholder back to the original file."""
        uri = self.from_placeholder(placeholder)
        return self.get_by_uri(uri)
    
    def __contains__(self, name: str) -> bool:
        """Check if a file exists in the map."""
        return name in self._files
        
    def __len__(self) -> int:
        """Get the number of files in the map."""
        return len(self._files)
        
    def __iter__(self) -> Iterator[File]:
        """Iterate over all files in the map."""
        return iter(self._files.values()) 