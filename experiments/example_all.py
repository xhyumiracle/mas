import asyncio

from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)

from mas.orch import Orchestrator, MockOrch
from mas.orch.parser import YamlParser
from mas.curator import ModelCurator, ToolCurator
from mas.flow import AgentTaskFlow, PocketflowExecutor
from mas.agent import Agent, MockAgent, AgnoAgent
from mas.tool import ToolPool
from mas.model import ModelPool
from mas.message import Message

logger = logging.getLogger(__name__)

async def run():
    """
    Example MAS: one-time answering
    """

    ''' Load model pool & tool pool '''

    # Loading tools
    tool_pool = ToolPool.initialize()
    print(f"""Loaded {tool_pool.count()} tools""")

    # Loading models
    model_pool = ModelPool.initialize()
    print(f"""Loaded {model_pool.count()} models""")
    Agent.set_model_pool(model_pool)
    Agent.set_tool_pool(tool_pool)

    ''' Initialize agent task graph builder '''

    orch: Orchestrator = MockOrch(
        parser=YamlParser(),
        model_pool=model_pool,
        tool_pool=tool_pool
    )

    ''' Generate agent task graph & Agents '''

    agent_task_graph = orch.generate(query="Write a story in George R.R. Martin's style")

    print("-----------1.Agent Task Graph----------")
    
    agent_task_graph.pprint()
    # agent_task_graph.plot()


    print("-----------2.Curations----------")

    ''' Initialize curators '''

    curators = [ToolCurator(pool=tool_pool), ModelCurator(pool=model_pool)]
    for curator in curators:
        agent_task_graph = curator.curate(agent_task_graph)

    print("Curation done")
    agent_task_graph.pprint()
    
    print("-----------3.Execution Flow----------")

    flow = AgentTaskFlow(
        # agent_cls=AgnoAgent,
        agent_cls=MockAgent,
        executor=PocketflowExecutor(is_chain=True),
        model_pool=model_pool,
        tool_pool=tool_pool
    )
    flow.build(agent_task_graph)

    ''' Print the flow order '''

    flow.pprint_flow_order()

    print("-----------4.Run Tasks----------")

    response_message: Message = flow.run() #TODO: not sure format
    response_message.pprint()

if __name__ == "__main__":
    asyncio.run(run())