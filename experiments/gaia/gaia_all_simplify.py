import asyncio
from dotenv import load_dotenv
from data.dataset import read_gaia_json
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)

from mas.mas import MasFactory
from mas.orch.planner import Planner
from mas.executor import SequentialExecutor
from mas.curator.mock import MockCurator
import json

logger = logging.getLogger(__name__)

async def run():
    # Loading data
    gaia_data = read_gaia_json()
    if not gaia_data:
        logger.error("Failed to load GAIA data")
        return
    mas = MasFactory(
        cls_Orch=Planner,
        cls_Executor=SequentialExecutor,
        cls_Curator=MockCurator,
    )
    mas.build()
    # Process each question
    results = []
    
    for index, item in enumerate(gaia_data):
        query = item['Question']
        print(f"\n====== Processing Question {index+1}/{len(gaia_data)} ======")
        print(f"Question: {query}")
        
        response_message = mas.run(query)

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