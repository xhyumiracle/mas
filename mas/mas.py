import logging
from dataclasses import dataclass, field
from typing import List, Type, Union
from mas.curator.base import Curator
from mas.orch import Orchestrator
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
    cls_Curators: List[Type[Curator]]
    model_pool: ModelPool = field(default_factory=ModelPool.get_global)
    tool_pool: ToolPool = field(default_factory=ToolPool.get_global)
    executor_is_chain: bool = True

    def build(self):
        ''' Initialize orchestrator, i.e. the agent task graph builder '''

        self.orch = self.cls_Orch(
            model_pool=self.model_pool,
            tool_pool=self.tool_pool,
        )

        ''' Initialize curators '''

        self.curators = [_C() for _C in self.cls_Curators]

        ''' Initialize flow executor '''

        self.flow = AgentTaskFlow(
            agent_cls=self.cls_Agent,
            executor=self.cls_Executor(is_chain=self.executor_is_chain),
        )

    def run(self, query: Union[str, Message]) -> Message:
        ''' Generate agent task graph & Agents '''

        agent_task_graph = self.orch.generate(query)

        logger.info("\n----------------1.Agent Task Graph---------------\n")
        
        for curator  in self.curators:
            agent_task_graph = curator.curate(agent_task_graph)

        agent_task_graph.pprint()
        # agent_task_graph.plot()

        logger.info("\n----------------2.Curations---------------\n")

        for curator  in self.curators:
            agent_task_graph = curator.curate(agent_task_graph)

        agent_task_graph.pprint()

        logger.info("\n----------------3.Execution Flow---------------\n")

        self.flow.build(agent_task_graph)

        ''' Print the flow order '''

        self.flow.pprint_flow_order()

        logger.info("\n----------------4.Run Tasks---------------\n")

        response_message: Message = self.flow.run() #TODO: not sure format
        logger.info("\n----------------Final Answer---------------\n")
        response_message.pprint()
        return response_message