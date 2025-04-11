from dataclasses import asdict
from mas.graph import TaskGraph, NodeAttr, EdgeAttr
import networkx as nx

def test_add_node_edge():
    G=nx.MultiDiGraph()
    graph = TaskGraph(G)
    node_a = NodeAttr(name="A", task="task A", profile="profile A", model="model A", input_modalities=["input A"], output_modalities=["output A"], tools=["tool A"])
    node_b = NodeAttr(name="B", task="task B", profile="profile B", model="model B", input_modalities=["input B"], output_modalities=["output B"], tools=["tool B"])
    graph.add_node_typed(1, node_a)
    graph.add_node_typed(2, node_b)
    graph.add_nodes_from_typed([(3, node_a), (4, node_b)])
    graph.add_edge(1, 2)
    graph.add_edge(2, 3)
    edge_attr = EdgeAttr(label="test")
    graph.add_edges_from_typed([(1, 3, edge_attr), (3, 4, edge_attr)])
    print(graph.edges())
    print(graph.in_edges(2))
    print(graph.out_edges(1))

    assert graph.nodes[1] == asdict(node_a)
    assert graph.nodes[2] == asdict(node_b)
    assert graph.edges[1, 2] == {}
    assert graph.edges[1, 3] == asdict(edge_attr)
