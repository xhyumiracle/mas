import asyncio

from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)

from mas.orch import Orchestrator, MockOrch
from mas.curator import ModelCurator, ToolCurator
from mas.flow import AgentTaskFlow, PocketflowExecutor
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

    agent_task_graph = orch.generate(query="Write a story in George R.R. Martin's style")

    print("-----------1.Agent Task Graph----------")
    
    agent_task_graph.pprint()
    # agent_task_graph.plot()


    print("-----------2.Curations----------")

    ''' Initialize curators '''

    curators = [ToolCurator(), ModelCurator()]
    for curator in curators:
        agent_task_graph = curator.curate(agent_task_graph)

    print("Curation done")
    agent_task_graph.pprint()
    
    print("-----------3.Execution Flow----------")

    flow = AgentTaskFlow(
        # agent_cls=AgnoAgent,
        cls_Agent=MockAgent,
        executor=PocketflowExecutor(),
    )
    flow.build(agent_task_graph)

    ''' Print the flow order '''

    flow.pprint_flow_order()

    print("-----------4.Run Tasks----------")

    response_message: Message = flow.run() #TODO: not sure format
    response_message.pprint()

if __name__ == "__main__":
    asyncio.run(run())