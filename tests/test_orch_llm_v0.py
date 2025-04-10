from mas.orch.llm_v0 import LLMOrch

def test_llm_orch():
    # user_msg = "Read my csv file that contails people's names and a descriptions. Select an appropriate birthday present for each of them, and generate a anime picture for each. Then suggest 3-5 links for birthday presents from online shopping platforms that ship within the US and save the presents names, prices, and the corresponding links to the same csv file. Pay attention that each present should be below $50."
    user_msg = "generate an image, make an audio based on it, and create a movie based on image and audio"
    planner = LLMOrch(
        base_model="gpt-4o",  # default
    )
    graph = planner.generate(user_msg)
    graph.pprint()