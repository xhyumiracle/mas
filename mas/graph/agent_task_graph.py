import logging
from dataclasses import asdict
from typing import Tuple, Iterable, List
import networkx as nx

from mas.errors.graph_error import InvalidNodeError, ModalityMismatchError
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

    def _validate_edges(self):
        # check if node id in all edges are valid
        for fr, to in self.edges():
            if fr not in self.nodes:
                raise InvalidNodeError(f"Node {fr} in edge [{fr} -> {to}] not found in graph")
            if to not in self.nodes:
                raise InvalidNodeError(f"Node {to} in edge [{fr} -> {to}] not found in graph")
    
    def _validate_modalities(self):
        for node in self.nodes:
            predecessors = list(self.predecessors(node))
            if predecessors:
                predecessor_output_modalities = set(
                    format
                    for predecessor in predecessors
                    for format in self.get_node_attr(predecessor).output_formats
                )
                print("--------- predecessor_output_modalities", predecessor_output_modalities)
                print("----------my input modalities", set(self.get_node_attr(node).input_formats))
                if predecessor_output_modalities != set(self.get_node_attr(node).input_formats):
                    raise ModalityMismatchError(f"Input modalities of node {node} do not match the output modalities of its predecessors")
    
    def validate(self):
        self._validate_edges()
        self._validate_modalities()

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

    def generate_mermaid_code(self, direction="TD"):
        """
        Generate a Mermaid diagram representation of the agent task graph.
        
        Returns:
            str: Mermaid diagram code
        """
        mermaid_code = f"graph {direction}\n"
        
        # Add nodes with their properties
        for node_id in self.nodes():
            node_attr = self.get_node_attr(node_id)
            node_name = getattr(node_attr, 'name', f'Node{node_id}')
            node_prompt = getattr(node_attr, 'prompt', '')
            
            # Format the prompt text for display - replace newlines with \n
            display_prompt = node_prompt.replace('\n', '\\n')
            
            # Create node definition
            mermaid_code += f'    {node_id}["{node_id}: {node_name}\\n{display_prompt}"]\n'
        
        # Add edges
        for u, v, data in self.edges(data=True):
            # Check if there's an action attribute in the edge data
            action = data.get('action', None)
            if action:
                # If there's an action, include it in the edge label
                mermaid_code += f'    {u} -->|"{action}"| {v}\n'
            else:
                # Otherwise, just create a simple edge
                mermaid_code += f'    {u} --> {v}\n'
        
        return mermaid_code