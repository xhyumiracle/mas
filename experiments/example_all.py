import asyncio

from dotenv import load_dotenv
from mas.executor.sequential import SequentialExecutor
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)

from mas.orch import Orchestrator, MockOrch
from mas.curator import MockCurator, ToolCurator
from mas.executor import AgentTaskFlow
from mas.agent import Agent, MockAgent, AgnoAgent
from mas.message import Message

logger = logging.getLogger(__name__)

def generate_mermaid_from_agent_graph(agent_graph):
    # Start the mermaid graph definition
    mermaid_code = "graph LR\n"
    
    # Add nodes with prompt content instead of style
    for node_id, node_data in agent_graph.items():
        if isinstance(node_data, dict):  # Make sure it's a node definition
            node_name = node_data.get('name', f'Node{node_id}')
            node_prompt = node_data.get('prompt', '')
            
            # Truncate prompt if too long for display
            if len(node_prompt) > 100:
                display_prompt = node_prompt[:97] + "..."
            else:
                display_prompt = node_prompt
                
            # Replace newlines with \n for mermaid
            display_prompt = display_prompt.replace('\n', '\\n')
            
            mermaid_code += f'    {node_id}["{node_id}: {node_name}\\n{display_prompt}"] '
            mermaid_code += "\n"
    
    # Add edges
    edges_info = []
    # Try to find edges in the format shown in your example
    for line in str(agent_graph).split('\n'):
        if line.startswith('[(') and ')]' in line:
            edges_text = line.strip()
            # Parse edges from the format [(1, 2, {'label': None})]
            edges_info = eval(edges_text)
            break
    
    # Add the edges to the mermaid code
    for edge in edges_info:
        if len(edge) >= 2:  # Make sure we have at least source and target
            source, target = edge[0], edge[1]
            mermaid_code += f"    {source} --> {target}\n"
    
    return mermaid_code

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

    print("-----------2.Curations----------")

    ''' Initialize curators '''

    curators = [ToolCurator(), MockCurator()]
    agent_task_graph = task_graph
    for curator in curators:
        agent_task_graph = curator.curate(agent_task_graph)

    print("Curation done")
    agent_task_graph.pprint()
    a = agent_task_graph.generate_mermaid_code()
    print(a)
    
    print("-----------3.Run Tasks----------")

    flow = AgentTaskFlow(
        executor=SequentialExecutor(),
    )
    flow.build(agent_task_graph)

    async for response in flow.run():
        print(response.content)
        response.pprint()

if __name__ == "__main__":
    asyncio.run(run())