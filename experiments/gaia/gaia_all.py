import asyncio
from dotenv import load_dotenv
from data.dataset import read_gaia_json
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)

from mas.orch import LLMOrch
from mas.curator import ModelCurator, ToolCurator
from mas.flow import AgentTaskFlow, PocketflowExecutor
from mas.agent import Agent, MockAgent, AgnoAgent
from mas.message import Message
import json
logger = logging.getLogger(__name__)

async def run():
    # Loading data
    gaia_data = read_gaia_json()
    if not gaia_data:
        logger.error("Failed to load GAIA data")
        return
    
    # Initialize curators once
    curators = [ToolCurator(), ModelCurator()]
    
    # Process each question
    results = []
    
    # Initialize orchestrator with current question
    orch = LLMOrch(
        model_pool=model_pool,
        tool_pool=tool_pool
    )

    for index, item in enumerate(gaia_data):
        query = item['Question']
        print(f"\n====== Processing Question {index+1}/{len(gaia_data)} ======")
        print(f"Question: {query}")
        
        orch.generate(query=query)
        
        # Generate agent task graph
        agent_task_graph = orch.generate_by_message()
        print("-----------1.Agent Task Graph----------")
        agent_task_graph.pprint()
        
        # Apply curations
        print("-----------2.Curations----------")
        for curator in curators:
            agent_task_graph = curator.curate(agent_task_graph)
        print("Curation done")
        agent_task_graph.pprint()
        
        # Build execution flow
        print("-----------3.Execution Flow----------")
        flow = AgentTaskFlow(
            cls_Agent=AgnoAgent,
            executor=PocketflowExecutor(),
        )
        flow.build(agent_task_graph)
        flow.pprint_flow_order()
        
        # Execute flow
        print("-----------4.Run Tasks----------")
        response_message = flow.run()
        response_message.pprint()
        
        # Save result
        results.append({
            "question": query,
            "response": response_message.to_dict() if hasattr(response_message, 'to_dict') else str(response_message)
        })
    
    # Save all results to a file
    with open("gaia_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nProcessed {len(results)} questions. Results saved to gaia_results.json")

if __name__ == "__main__":
    asyncio.run(run())