from mas.agent.agno import AgnoAgent
from mas.agent.base import Agent
from mas.agent.mock import MockAgent
from mas.flow.agent_task_flow import AgentTaskFlow
from mas.flow.executor.pocketflow import PocketflowExecutor
from mas.flow.executor.simple_sequential import SimpleSequentialExecutor
from mas.orch.parser import YamlParser
from mas.tool import ToolPool
from mas.model import ModelPool

def build_graph_from_yaml():
    parser = YamlParser()
    graph = parser.parse_from_path('tests/data/graph.1.yaml')
    return graph

def test_SimpleSequentialFlow():
    flow = AgentTaskFlow(
        cls_Agent=MockAgent,
        executor=SimpleSequentialExecutor(),
    )
    flow.build(build_graph_from_yaml())
    flow.run()

def test_PocketFlowChainFlow():

    ToolPool.get_global()
    ModelPool().get_global()

    flow = AgentTaskFlow(
        cls_Agent=AgnoAgent,
        executor=PocketflowExecutor()
    )
    flow.build(build_graph_from_yaml())
    flow.run()