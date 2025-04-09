import asyncio

from dotenv import load_dotenv
from mas.flow.executor.sequential import SequentialExecutor
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)

from mas.orch import Orchestrator, MockOrch
from mas.curator import ModelCurator, ToolCurator
from mas.flow import AgentTaskFlow
from mas.agent import Agent, MockAgent, AgnoAgent
from mas.message import Message

logger = logging.getLogger(__name__)

async def run():
    """
    Example MAS: one-time answering
    """

    ''' Initialize agent task graph builder '''

    orch: Orchestrator = MockOrch()

    ''' Generate agent task graph & Agents '''

    task_graph = orch.generate(query="Write a story in George R.R. Martin's style")

    print("-----------1.Task Graph----------")
    
    task_graph.pprint()
    # agent_task_graph.plot()

    print("-----------2.Curations----------")

    ''' Initialize curators '''

    curators = [ToolCurator(), ModelCurator()]
    agent_task_graph = task_graph
    for curator in curators:
        agent_task_graph = curator.curate(agent_task_graph)

    print("Curation done")
    agent_task_graph.pprint()
    
    print("-----------3.Run Tasks----------")

    flow = AgentTaskFlow(
        # agent_cls=AgnoAgent,
        cls_Agent=MockAgent,
        executor=SequentialExecutor(),
    )
    flow.build(agent_task_graph)

    for response in flow.run():
        response.pprint()

if __name__ == "__main__":
    asyncio.run(run())