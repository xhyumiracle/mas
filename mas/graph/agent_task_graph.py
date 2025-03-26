import logging
from dataclasses import asdict
from typing import Tuple, Iterable, List
import networkx as nx

from mas.graph.types import EdgeAttr, NodeAttr, NodeId

logger = logging.getLogger(__name__)

'''
Graph:
v0: 
1. DAG, (Multi)DiGraph
1. each node out_action: only 1 out_arc
2. each node in_action: N>=0 in_arcs

v1: 
1. DCG
2. each node each out_action: M>=0 out_arcs
'''
class AgentTaskGraph(nx.DiGraph):
    
    def __init__(self, graph: nx.DiGraph=nx.MultiDiGraph(), nodes: List[Tuple[NodeId, NodeAttr]]=[], edges: List[Tuple[NodeId, NodeId, str]]=[]):
        super().__init__(graph)
        self.add_nodes_from_typed(nodes)
        self.add_edges_from_typed(edges)
        self.validate()

    def _validate_v0(self):
        pass
    
    def _validate_modalities(self):
        # for each edge, check if the from output modality <= to input modality
        for fr, to in self.edges():
            _fr_modality = set(self.get_node_attr(fr).output_formats)
            _to_modality = set(self.get_node_attr(to).input_formats)
            if not _fr_modality.issubset(_to_modality):
                logger.error(f"Modalities do not match: {fr} -> {to}")
                # raise Exception("Modalities do not match")
    
    #TODO use @validator?
    def validate(self):
        self._validate_modalities()
        self._validate_v0()

    def topological_sort(self):
        return nx.topological_sort(self)
    
    def get_node_attr(self, node_id: NodeId) -> NodeAttr:
        attr_dict = self.nodes[node_id]
        return NodeAttr(**attr_dict)
    
    ''' Graph Growing Functions '''

    def add_node_typed(self, node_for_adding: NodeId, attr: NodeAttr):
        attr_dict = asdict(attr)
        return super().add_node(node_for_adding, **attr_dict)
    
    def add_edge_typed(self, u_of_edge: NodeId, v_of_edge: NodeId, attr: EdgeAttr):
        attr_dict = asdict(attr)
        return super().add_edge(u_of_edge, v_of_edge, **attr_dict)
    
    def add_nodes_from_typed(self, nodes_for_adding: Iterable[Tuple[NodeId, NodeAttr]], **attr):
        return super().add_nodes_from([(node_id, asdict(node_attr)) for node_id, node_attr in nodes_for_adding], **attr)
        
    def add_edges_from_typed(self, ebunch_to_add: Iterable[Tuple[NodeId, NodeId, EdgeAttr]], **attr):
        return super().add_edges_from([(fr, to, asdict(edge_attr)) for fr, to, edge_attr in ebunch_to_add], **attr)

    ''' Original functions, for type hint only '''

    def in_edges(self, node):
        return super().in_edges(node)
    
    def out_edges(self, node):
        return super().out_edges(node)

    def pprint(self):
        import pprint
        
        pp = pprint.PrettyPrinter(indent=2)

        logger.info("Nodes:")
        logger.info(pp.pformat(dict(self.nodes(data=True))))

        logger.info("\nEdges:")
        logger.info(pp.pformat(list(self.edges(data=True))))

    def plot(self):
        import matplotlib.pyplot as plt
        nx.draw(self, with_labels=True)
        plt.show()