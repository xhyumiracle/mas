import logging
from dataclasses import dataclass, field
from typing import List, Type, Union
from mas.curator.base import Curator
from mas.orch import Orchestrator
from mas.flow import AgentTaskFlow
from mas.message import Message
from mas.flow import FlowExecutor

logger = logging.getLogger(__name__)

@dataclass
class MasFactory:
    cls_Orch: Type[Orchestrator]
    cls_Executor: Type[FlowExecutor]
    cls_Curators: List[Type[Curator]]

    def build(self):
        ''' Initialize orchestrator, i.e. the agent task graph builder '''

        self.orch = self.cls_Orch()

        ''' Initialize curators '''

        self.curators = [_C() for _C in self.cls_Curators]

        ''' Initialize flow executor '''

        self.flow = AgentTaskFlow(
            executor=self.cls_Executor(),
        )

    async def run(self, query: Union[str, Message]) -> Message:

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

        async for response in self.flow.run():
            response.pprint()
            latest_response = response
        
        logger.info("\n----------------Final Answer---------------\n")
        latest_response.pprint()
        return latest_response