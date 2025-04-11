from typing import List, Tuple
from mas.graph.task_graph import TaskGraph, EdgeAttr, NodeAttr, NodeId
from mas.orch.parser import Parser
import yaml

class YamlParser(Parser):
    def parse_from_path(self, filename: str) -> TaskGraph:
        """Parse a YAML file from a given path into an AgentTaskGraph."""
        with open(filename, 'r') as file:
            data = yaml.safe_load(file)
            if not data:
                raise ValueError(f"Failed to load YAML from {filename} or file is empty")
            return self.parse_from_string(data)
    
    def parse_from_string(self, yaml) -> TaskGraph:
        '''parse from yaml string to AgentTaskGraph'''
        node_attr_dict = { NodeId(agent_yaml['id']): self.to_node_attr(agent_yaml) for agent_yaml in yaml['agents'] }
        edges_list = [self.to_edges(edge_yaml) for edge_yaml in yaml['edges']]

        nodes = [(node_id, node_attr_dict[node_id]) for node_id in node_attr_dict.keys()]
        edges = [x for edge_list in edges_list for x in edge_list] # flatten
        
        return TaskGraph(nodes=nodes, edges=edges)

    def to_node_attr(self, agent_yaml) -> NodeAttr:
        return NodeAttr(
            # no id since it's in dict
            name=agent_yaml['name'],
            task=agent_yaml['task'],
            profile=agent_yaml['profile'],
            model=agent_yaml['model'],
            input_modalities=agent_yaml.get('input', ['text']),
            output_modalities=agent_yaml.get('output', ['text']),
            tools=agent_yaml.get('tools', [])
        )

    def to_edges(self, edge_raw) -> List[Tuple[NodeId, NodeId, EdgeAttr]]:
        fr, to, *rest = edge_raw
        type_str = rest[0] if rest else None
        edges = []
        edges.append([NodeId(fr), NodeId(to), EdgeAttr(label=type_str)])
        # if type_str in ['loop', 'bidirectional']: # v1: DAG + loop
        #     edges.append(node_dict[to], node_dict[fr], key='reject')
        #     edges.append(node_dict[to], node_dict[fr], key='approve')
        #     if type_str == 'bidirectional': #TODO: is this stable?
        #         edges.append(node_dict[fr], node_dict[to], key='default') # type can be None
        # else: # v0: DAG only
            # edges.append(node_dict[fr], node_dict[to], key=type_str)
        return edges

if __name__ == "__main__":
    parser = YamlParser()
    try:
        graph = parser.parse_from_path('tests/data/graph.0.yaml')
        print(graph)
    except Exception as e:
        print(f"Error parsing YAML: {e}")