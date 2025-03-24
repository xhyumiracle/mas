from dataclasses import dataclass
from typing import Type
from mas.agent.mock import MockAgent
from mas.orch import Orchestrator, MockOrch
from mas.orch.parser import Parser
from mas.flow.agent_task_flow import AgentTaskFlow
from mas.flow.executor.pocketflow import PocketflowExecutor
from mas.agent import Agent
from mas.agent.agno import AgnoAgent
from mas.tool import ToolPool, TOOLS
from mas.model import ModelPool, MODELS
from mas.message import Message
from mas.flow import FlowExecutor

@dataclass
class MasFactory:
    cls_Orch: Type[Orchestrator]
    cls_Parser: Type[Parser]
    cls_Agent: Type[Agent]
    cls_Executor: Type[FlowExecutor]
    tool_map: dict
    model_map: dict
    executor_is_chain: bool

    def build(self):
        ''' Load model pool & tool pool '''

        # Loading tools
        tool_pool = ToolPool(tool_map=self.tool_map)
        print(f"""Loaded {tool_pool.count()} tools""")

        # Loading models
        model_pool = ModelPool(model_map=self.model_map)
        print(f"""Loaded {model_pool.count()} models""")

        Agent.set_model_pool(model_pool)
        Agent.set_tool_pool(tool_pool)

        ''' Initialize agent task graph builder '''

        self.orch = self.cls_Orch(
            parser=self.cls_Parser(),
            model_pool=model_pool,
            tool_pool=tool_pool
        )

        ''' Initialize flow executor '''

        self.flow = AgentTaskFlow(
            agent_cls=self.cls_Agent,
            executor=self.cls_Executor(is_chain=self.executor_is_chain),
            model_pool=model_pool,
            tool_pool=tool_pool
        )

    def run(self, query: str):
        ''' Generate agent task graph & Agents '''

        agent_task_graph = self.orch.generate(query=query)

        print("-----------1.Agent Task Graph----------")
        
        agent_task_graph.pprint()
        # agent_task_graph.plot()

        print("-----------2.Execution Flow----------")

        self.flow.build(agent_task_graph)

        ''' Print the flow order '''

        self.flow.pprint_flow_order()

        print("-----------3.Run Tasks----------")

        response_message: Message = self.flow.run() #TODO: not sure format
        print("-----------Final Answer----------")
        response_message.pprint()