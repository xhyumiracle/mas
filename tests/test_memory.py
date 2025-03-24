from mas.memory.memory import FlowMemory
from mas.storage.mem import InMemoryStorage

def test_memory_inmemory():
    memory = FlowMemory(storage=InMemoryStorage())
    memory.add_entry(caller="A", callee="B", action="action1", data={"x": 1})
    memory.add_entry(caller="B", callee="C", action="action2", data={"y": 2})
    assert memory.get_entries_by_caller("A") == [("B", "action1")]
    assert memory.get_entries_by_callee("B") == [("A", "action1")]
    assert memory.get_data("A", "B", "action1") == {"x": 1}
    