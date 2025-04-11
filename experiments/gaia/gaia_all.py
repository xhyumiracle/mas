import asyncio
from dotenv import load_dotenv
from data.dataset import read_gaia_json
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)

from mas.orch.planner import Planner
from mas.curator.mock import MockCurator
from mas.executor import SequentialExecutor
import json
logger = logging.getLogger(__name__)

async def run():
    # Loading data
    gaia_data = read_gaia_json()
    if not gaia_data:
        logger.error("Failed to load GAIA data")
        return
    
    # Initialize orchestrator with current question
    orch = Planner()

    # Initialize curators once
    curator = MockCurator()
    
    # Process each question
    results = []

    for index, item in enumerate(gaia_data):
        query = item['Question']
        print(f"\n====== Processing Question {index+1}/{len(gaia_data)} ======")
        print(f"Question: {query}")
        
        # Generate agent task graph
        task_graph = orch.generate(query=query)
        print("-----------1.Task Graph----------")
        task_graph.pprint()
        
        # Apply curations
        print("-----------2.Agent Graph----------")
        agent_graph = curator.curate(task_graph)
        print("Curation done")
        agent_graph.pprint()
        
        # Execute flow
        print("-----------3.Run Tasks----------")
        response_message = await SequentialExecutor(agent_graph).run_to_completion()
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