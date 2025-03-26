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

logger = logging.getLogger(__name__)

@dataclass
class MasFactory:
    cls_Orch: Type[Orchestrator]
    cls_Agent: Type[Agent]
    cls_Executor: Type[FlowExecutor]
    cls_Curators: Dict[Literal["tool", "model"], Type[Curator]] = field(default_factory=dict)
    cls_Parser: Optional[Type[Parser]] = None
    model_pool: ModelPool = ModelPool.initialize()
    tool_pool: ToolPool = ToolPool.initialize()
    executor_is_chain: bool = True

    def build(self):
        ''' Initialize orchestrator, i.e. the agent task graph builder '''

        kwargs = {"parser": self.cls_Parser()} if self.cls_Parser is not None else {}

        self.orch = self.cls_Orch(
            # parser=self.cls_Parser(),
            model_pool=self.model_pool,
            tool_pool=self.tool_pool,
            **kwargs
        )

        ''' Initialize curators '''

        pools = {"tool": self.tool_pool, "model": self.model_pool}
        self.curators = [_C(pool=pools.get(key)) for key, _C in self.cls_Curators.items()]

        ''' Initialize flow executor '''

        self.flow = AgentTaskFlow(
            agent_cls=self.cls_Agent,
            executor=self.cls_Executor(is_chain=self.executor_is_chain),
        )

    def run(self, query: str):
        ''' Generate agent task graph & Agents '''

        agent_task_graph = self.orch.generate(query=query)

        print("\n----------------1.Agent Task Graph---------------\n")
        
        for curator  in self.curators:
            agent_task_graph = curator.curate(agent_task_graph)

        agent_task_graph.pprint()
        # agent_task_graph.plot()

        print("\n----------------2.Curations---------------\n")

        for curator  in self.curators:
            agent_task_graph = curator.curate(agent_task_graph)

        agent_task_graph.pprint()

        print("\n----------------3.Execution Flow---------------\n")

        self.flow.build(agent_task_graph)

        ''' Print the flow order '''

        self.flow.pprint_flow_order()

        print("\n----------------4.Run Tasks---------------\n")

        response_message: Message = self.flow.run() #TODO: not sure format
        print("\n----------------Final Answer---------------\n")
        response_message.pprint()