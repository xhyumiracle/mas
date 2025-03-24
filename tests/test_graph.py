from dataclasses import asdict
from mas.graph.agent_task_graph import AgentTaskGraph, NodeAttr
import networkx as nx

def test_add_node_edge():
    G=nx.MultiDiGraph()
    graph = AgentTaskGraph(G)
    node_a = NodeAttr(name="A", prompt="task A", profile="profile A", model="model A", input_formats=["input A"], output_formats=["output A"], tools=["tool A"])
    node_b = NodeAttr(name="B", prompt="task B", profile="profile B", model="model B", input_formats=["input B"], output_formats=["output B"], tools=["tool B"])
    graph.add_node_typed(1, node_a)
    graph.add_node_typed(2, node_b)
    graph.add_nodes_from([(3, node_a), (4, node_b)])
    graph.add_edge(1, 2)
    graph.add_edge(2, 3)
    print(graph.edges())
    print(graph.in_edges(2))
    print(graph.out_edges(1))

    assert graph.nodes[1] == asdict(node_a)
    assert graph.nodes[2] == asdict(node_b)
