import logging
from dataclasses import dataclass, field
from typing import Dict, Literal, Optional, Type
from mas.curator.base import Curator
from mas.orch import Orchestrator
from mas.orch.parser import Parser
from mas.flow import AgentTaskFlow
from mas.agent import Agent
from mas.tool import ToolPool
from mas.model import ModelPool
from mas.message import Message
from mas.flow import FlowExecutor

@dataclass
class MasFactory:
    tool_map: Dict
    model_map: Dict
    cls_Orch: Type[Orchestrator]
    cls_Agent: Type[Agent]
    cls_Executor: Type[FlowExecutor]
    cls_Curators: Dict[Literal["tool", "model"], Type[Curator]] = field(default_factory=dict)
    cls_Parser: Optional[Type[Parser]] = None
    executor_is_chain: bool = True

    def build(self):
        ''' Load model pool & tool pool '''

        # Loading tools
        tool_pool = ToolPool(map=self.tool_map)
        logging.info(f"""Loaded {tool_pool.count()} tools""")

        # Loading models
        model_pool = ModelPool(map=self.model_map)
        logging.info(f"""Loaded {model_pool.count()} models""")

        Agent.set_model_pool(model_pool)
        Agent.set_tool_pool(tool_pool)

        ''' Initialize agent task graph builder '''

        kwargs = {"parser": self.cls_Parser()} if self.cls_Parser is not None else {}

        self.orch = self.cls_Orch(
            # parser=self.cls_Parser(),
            model_pool=model_pool,
            tool_pool=tool_pool,
            **kwargs
        )

        ''' Initialize curators '''

        pools = {"tool": tool_pool, "model": model_pool}
        self.curators = [_C(pool=pools.get(key)) for key, _C in self.cls_Curators.items()]

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
        
        for curator  in self.curators:
            agent_task_graph = curator.curate(agent_task_graph)

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