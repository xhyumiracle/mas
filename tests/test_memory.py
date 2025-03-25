from mas.memory.memory import FlowMemory
from mas.storage.mem import InMemoryStorage

def test_memory_inmemory():
    memory = FlowMemory(storage=InMemoryStorage())
    memory.add_entry(caller=1, callee=2, action="action1", data={"x": 1})
    memory.add_entry(caller=2, callee=3, action="action2", data={"y": 2})
    assert memory.get_entries_by_caller(1, mask=["callee", "action"]) == [{"callee": 2, "action": "action1"}]
    assert memory.get_entries_by_callee(2, mask=["caller", "action"]) == [{"caller": 1, "action": "action1"}]
    assert memory.get_data(1, 2, "action1") == {"x": 1}