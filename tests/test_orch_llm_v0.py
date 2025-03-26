from mas.model.pool import ModelPool
from mas.orch.llm_v0 import LLMOrch
from mas.tool.pool import ToolPool

def test_llm_orch():
    user_msg = "Read my csv file that contails people's names and a descriptions. Select an appropriate birthday present for each of them, and generate a anime picture for each. Then suggest 3-5 links for birthday presents from online shopping platforms that ship within the US and save the presents names, prices, and the corresponding links to the same csv file. Pay attention that each present should be below $50."

    planner = LLMOrch(
        user_request=user_msg,
        base_model="gpt-4o",  # default
    )

    graph = planner.generate_by_messages()
    graph.pprint()
