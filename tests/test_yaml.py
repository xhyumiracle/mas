
from mas.orch.parser.yaml_parser import YamlParser

def test_parse_from_path():
    parser = YamlParser()
    graph = parser.parse_from_path('tests/data/graph.0.yaml')
    print(f"edges: {graph.edges}")
