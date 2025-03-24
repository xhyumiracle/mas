from mas.agent.agno import AgnoAgent
from mas.agent.base import Agent
from mas.agent.mock import MockAgent
from mas.flow.agent_task_flow import AgentTaskFlow
from mas.flow.executor.pocketflow import PocketflowExecutor
from mas.flow.executor.simple_chain import SimpleChainExecutor
from mas.orch.parser.yaml import YamlParser
from mas.tool import ToolPool, TOOLS
from mas.model import ModelPool, MODELS

def build_graph_from_yaml():
    parser = YamlParser()
    graph = parser.parse_from_path('tests/data/graph.0.yaml')
    return graph

def test_SimpleChainFlow():
    flow = AgentTaskFlow(
        agent_cls=MockAgent,
        executor=SimpleChainExecutor(is_chain=True),
    )
    flow.build(build_graph_from_yaml())
    flow.run()

def test_PocketFlowChainFlow():

    tool_pool = ToolPool(tool_map=TOOLS)
    model_pool = ModelPool(model_map=MODELS)
    Agent.set_model_pool(model_pool)
    Agent.set_tool_pool(tool_pool)

    flow = AgentTaskFlow(
        agent_cls=AgnoAgent,
        executor=PocketflowExecutor(is_chain=True),
        is_chain=True
    )
    flow.build(build_graph_from_yaml())
    flow.run()