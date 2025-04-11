import logging
from dataclasses import dataclass
from typing import List, Type, Union
from mas.curator.base import Curator
from mas.orch import Orchestrator
from mas.message import Message
from mas.executor import GraphExecutor
logger = logging.getLogger(__name__)

@dataclass
class MasFactory:
    cls_Orch: Type[Orchestrator]
    cls_Executor: Type[GraphExecutor]
    cls_Curator: Type[Curator]

    def build(self):
        ''' Initialize orchestrator, i.e. the agent task graph builder '''

        self.orch = self.cls_Orch()

        ''' Initialize curators '''

        self.curator = self.cls_Curator()

    async def run(self, query: Union[str, Message]) -> Message:

        logger.info("\n----------------1.Task Graph---------------\n")

        ''' Generate the task graph '''

        task_graph = self.orch.generate(query)

        task_graph.pprint()
        # agent_task_graph.plot()

        logger.info("\n----------------2.Agent Graph---------------\n")

        agent_graph = self.curator.curate(task_graph)

        agent_graph.pprint()

        logger.info("\n----------------3.Execution---------------\n")

        # self.flow.build(agent_graph)
        
        async for response in self.cls_Executor(agent_graph).run():
            response.pprint()
            latest_response = response
        
        logger.info("\n----------------Final Answer---------------\n")
        latest_response.pprint()
        return latest_response