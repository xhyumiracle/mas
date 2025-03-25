from typing import List, Tuple
from mas.graph.agent_task_graph import AgentTaskGraph, EdgeAttr, NodeAttr, NodeId
from mas.orch.parser import Parser

class YamlParser(Parser):
    def parse_from_path(self, filename) -> AgentTaskGraph:
        import yaml
        with open(filename, 'r') as file:
            return self.parse_from_string(yaml.safe_load(file))
    
    def parse_from_string(self, yaml) -> AgentTaskGraph:
        '''parse from yaml string to AgentTaskGraph'''
        node_attr_dict = { NodeId(agent_yaml['id']): self.to_node_attr(agent_yaml) for agent_yaml in yaml['agents'] }
        edges_list = [self.to_edges(edge_yaml) for edge_yaml in yaml['edges']]

        nodes = [(node_id, node_attr_dict[node_id]) for node_id in node_attr_dict.keys()]
        edges = [x for edge_list in edges_list for x in edge_list] # flatten
        
        return AgentTaskGraph(nodes=nodes, edges=edges)

    def to_node_attr(self, agent_yaml) -> NodeAttr:
        return NodeAttr(
            # no id since it's in dict
            name=agent_yaml['name'],
            prompt=agent_yaml['prompt'],
            profile=agent_yaml['profile'],
            model=agent_yaml['model'],
            input_formats=agent_yaml.get('input', ['text']),
            output_formats=agent_yaml.get('output', ['text']),
            tools=agent_yaml.get('tools')
        )

    def to_edges(self, edge_raw) -> List[Tuple[NodeId, NodeId, EdgeAttr]]:
        fr, to, *rest = edge_raw
        type_str = rest[0] if rest else None
        edges = []
        edges.append([NodeId(fr), NodeId(to), EdgeAttr(action=type_str)])
        # if type_str in ['loop', 'bidirectional']: # v1: DAG + loop
        #     edges.append(node_dict[to], node_dict[fr], key='reject')
        #     edges.append(node_dict[to], node_dict[fr], key='approve')
        #     if type_str == 'bidirectional': #TODO: is this stable?
        #         edges.append(node_dict[fr], node_dict[to], key='default') # type can be None
        # else: # v0: DAG only
            # edges.append(node_dict[fr], node_dict[to], key=type_str)
        return edges
