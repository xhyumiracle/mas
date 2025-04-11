from mas.orch.planner import Planner

def test_planner():
    planner = Planner()
    task_graph = planner.generate("I want to build a website", [])
    task_graph.pprint()

