from mas.memory.flowmemory import FlowMemory
from mas.storage.mem import InMemoryStorage

def test_memory_inmemory():
    memory = FlowMemory(storage=InMemoryStorage())
    memory.add_entry(caller=1, callee=2, label="label1", data={"x": 1})
    memory.add_entry(caller=2, callee=3, label="label2", data={"y": 2})
    assert memory.get_entries_by_caller(1, mask=["callee", "label"]) == [{"callee": 2, "label": "label1"}]
    assert memory.get_entries_by_callee(2, mask=["caller", "label"]) == [{"caller": 1, "label": "label1"}]
    assert memory.get_data(1, 2, "label1") == {"x": 1}