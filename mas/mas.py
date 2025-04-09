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
            cls_Agent=self.cls_Agent,
            executor=self.cls_Executor(),
        )

    def run(self, query: Union[str, Message]) -> Message:

        logger.info("\n----------------1.Agent Task Graph---------------\n")

        ''' Generate the task graph '''

        task_graph = self.orch.generate(query)

        task_graph.pprint()
        # agent_task_graph.plot()

        logger.info("\n----------------2.Curations---------------\n")

        agent_task_graph = task_graph
        for curator  in self.curators:
            agent_task_graph = curator.curate(agent_task_graph)

        agent_task_graph.pprint()

        logger.info("\n----------------3.Run Tasks---------------\n")

        self.flow.build(agent_task_graph)

        for response in self.flow.run():
            response.pprint()
            latest_response = response
        
        logger.info("\n----------------Final Answer---------------\n")
        latest_response.pprint()
        return latest_response