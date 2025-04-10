from mas.memory.filemap import FileMap
from mas.message.types import File
import pytest

def test_filemap_basic_operations():
    """Test basic FileMap operations."""
    filemap = FileMap()
    
    # Test adding a file
    file1 = File(name="test.txt", mime_type="text/plain", uri="http://example.com/test.txt")
    filemap.add(file1)
    assert file1.name in filemap
    assert filemap.get_by_name(file1.name) == file1
    
    # Test adding another file with different name
    file2 = File(name="test2.txt", mime_type="text/plain", uri="http://example.com/test2.txt")
    filemap.add(file2)
    assert file2.name in filemap
    assert filemap.get_by_name(file2.name) == file2
    
    # Test removing a file
    filemap.remove(file1.name)
    assert file1.name not in filemap
    assert filemap.get_by_name(file1.name) is None
    
    # Test clearing the map
    filemap.clear()
    assert len(filemap) == 0
    assert file2.name not in filemap

def test_filemap_duplicate_names():
    """Test handling of duplicate filenames."""
    filemap = FileMap()
    
    # Add first file
    file1 = File(name="test.txt", mime_type="text/plain")
    filemap.add(file1)
    assert file1.name in filemap
    assert filemap.get_by_name(file1.name) == file1
    
    # Add second file with same name
    file2 = File(name="test.txt", mime_type="text/plain")
    filemap.add(file2)
    assert file2.name == "test(1).txt"  # Name should be modified
    assert file2.name in filemap
    assert filemap.get_by_name(file2.name) == file2
    
    # Add third file with same name
    file3 = File(name="test.txt", mime_type="text/plain")
    filemap.add(file3)
    assert file3.name == "test(2).txt"  # Name should be modified again
    assert file3.name in filemap
    assert filemap.get_by_name(file3.name) == file3
    
    # Test removing files and name reuse
    filemap.remove(file2.name)

def test_filemap_without_extensions():
    """Test handling of filenames without extensions."""
    filemap = FileMap()
    
    # Test without extension
    file1 = File(name="test", mime_type="text/plain")
    filemap.add(file1)
    
    file2 = File(name="test", mime_type="text/plain")
    filemap.add(file2)
    assert file2.name == "test(1)"  # Should not add extension
    
    # Test with multiple dots
    file3 = File(name="test.file.txt", mime_type="text/plain")
    filemap.add(file3)
    
    file4 = File(name="test.file.txt", mime_type="text/plain")
    filemap.add(file4)
    assert file4.name == "test.file(1).txt"  # Should handle multiple dots correctly 

def test_filemap_wrap_unwrap():
    """Test wrap and unwrap functionality of FileMap."""
    filemap = FileMap()
    
    # Test wrapping a file
    file1 = File(name="test.txt", mime_type="text/plain", uri="http://example.com/test.txt")
    wrapped = filemap.wrap(file1)
    assert wrapped == f"<file>{filemap.to_uri(file1.name)}</file>"
    
    # Test unwrapping a file
    unwrapped_file = filemap.unwrap(wrapped)
    assert unwrapped_file == file1
    
    # Test unwrapping with invalid format
    with pytest.raises(ValueError):
        filemap.unwrap("invalid_format")
    
    # Test unwrapping with empty content
    with pytest.raises(ValueError):
        filemap.unwrap("<file></file>")
    