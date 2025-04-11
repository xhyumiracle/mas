
def test_mock():
    from mas.curator.mock import MockCurator
    from mas.graph.task_graph import TaskGraph

    G = TaskGraph()
    G.add_node(1, id=1, task="task1", input_modalities=["text"], output_modalities=["text"])
    
    curator = MockCurator()
    G = curator.curate(G)

    assert G.nodes[1]["agent"] is not None