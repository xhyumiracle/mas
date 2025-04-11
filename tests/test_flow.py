import asyncio
from mas.flow.agent_task_flow import AgentTaskFlow
from mas.flow.executor.sequential import SequentialExecutor
from mas.orch.parser import YamlParser

def build_graph_from_yaml():
    parser = YamlParser()
    graph = parser.parse_from_path('tests/data/graph.1.yaml')
    return graph

def test_SequentialExecutor():
    flow = AgentTaskFlow(
        executor=SequentialExecutor(),
    )
    flow.build(build_graph_from_yaml())
    asyncio.run(flow.run_to_completion())
