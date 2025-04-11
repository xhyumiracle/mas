from typing import List, Tuple
from mas.graph.task_graph import TaskGraph, EdgeAttr, NodeAttr, NodeId
from mas.orch.parser import Parser
import json

class JsonParser(Parser):
    def parse_from_path(self, filename: str) -> TaskGraph:
        """Parse a JSON file from a given path into an AgentTaskGraph."""
        with open(filename, 'r') as file:
            data = json.load(file)
            if not data:
                raise ValueError(f"Failed to load JSON from {filename} or file is empty")
            return self.parse_from_string(data)
    
    def parse_from_string(self, str) -> TaskGraph:
        '''parse from json data to AgentTaskGraph'''
        dic = json.loads(str) # dic (the output of the llm) was a string, turn it into dict
        return self.parse_from_jsonobj(dic)

    def parse_from_jsonobj(self, dic) -> TaskGraph:
        node_attr_dict = {NodeId(agent['id']): self.to_node_attr(agent) for agent in dic['agents']}
        nodes = [(node_id, node_attr_dict[node_id]) for node_id in node_attr_dict.keys()]
        edges = self.to_edges(dic['edges'])
        
        return TaskGraph(nodes=nodes, edges=edges)

    def to_node_attr(self, agent_json: dict) -> NodeAttr:
        return NodeAttr(
            # no id since it's in dict
            name=agent_json['name'],
            task=agent_json['task'],
            profile=agent_json['profile'],
            model=agent_json['model'],
            input_modalities=agent_json.get('input', ['text']),
            output_modalities=agent_json.get('output', ['text']),
            tools=agent_json.get('tools', [])
        )

    def to_edges(self, edges) -> List[Tuple[NodeId, NodeId, EdgeAttr]]:
        edge_list = []
        for edge in edges: 
            edge.append(EdgeAttr(label=None))
            edge_list.append(edge)
        
        # if type_str in ['loop', 'bidirectional']: # v1: DAG + loop
        #     edges.append(node_dict[to], node_dict[fr], key='reject')
        #     edges.append(node_dict[to], node_dict[fr], key='approve')
        #     if type_str == 'bidirectional': #TODO: is this stable?
        #         edges.append(node_dict[fr], node_dict[to], key='default') # type can be None
        # else: # v0: DAG only
            # edges.append(node_dict[fr], node_dict[to], key=type_str)
        return edge_list

if __name__ == "__main__":
    parser = JsonParser()
    graph = parser.parse_from_path('planner_output.json')
    print(graph)
