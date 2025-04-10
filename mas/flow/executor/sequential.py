import logging
from typing import List
from mas.agent.base import Agent
from mas.flow.executor.base import FlowExecutor
from mas.memory.flowmemory import FlowMemory
from mas.message import Message, Part
from mas.graph import AgentTaskGraph

logger = logging.getLogger(__name__)

class SequentialExecutor(FlowExecutor):

    async def run(self, graph: AgentTaskGraph, memory: FlowMemory) -> Message:
        self.sequential_order = list(graph.topological_sort())

        '''
        shared memory
        '''
        shared = {
            "graph": graph,
            "memory": memory
        }

        for node_id in self.sequential_order:
            agent = graph.nodes[node_id]["agent"]
            prompt = graph.nodes[node_id]["prompt"]
            goal, observations = prep_request(node_id, prompt, shared)
            # pprint_messages(request)
            response = await exec(node_id, agent, goal, observations, prompt, shared)
        
        return response

    # retry_prompt = "Please adjust your output based on the feedback from the reviewer."

def prep_request(node_id, prompt, shared_memory) -> List[Message]:
    mem: FlowMemory = shared_memory["memory"]
    graph: AgentTaskGraph = shared_memory["graph"]
    
    """create the input messages: [predecessor user prompt, predecessor output] + current user prompt """

    observations = []
    for pred in graph.predecessors(node_id):
        _pred_data = mem.get_data(pred, node_id, "default")
        pred_user_prompt = _pred_data["caller_user_prompt"]
        pred_output_message = _pred_data["caller_output_message"]
        observations.append(Message(role="user", parts=[Part(text=pred_user_prompt)]))
        observations.append(pred_output_message)
    
    # add the current user prompt to the last message, to help the agent understand the context
    
    goal = Message(role="user", parts=[Part(text=prompt)])

    return goal, observations

async def exec(node_id, agent: Agent, goal: Message, observations: List[Message], prompt: str, shared_memory):

    """ execute the task by given agent """
    logger.info(f"---------Running Agent[id={node_id}]")

    task_result = await agent.run(goal=goal, observations=observations)
    
    """ result """
    logger.info(f"---------Agent[id={node_id}] complete")
    
    """ save to shared memory """
    successors = list(shared_memory["graph"].successors(node_id))
    
    if not any(successors):
        logger.debug('no successors, im the last node, writting results')
        shared_memory["final_output_message"] = task_result

    for succ in successors:
        shared_memory["memory"].add_entry(caller=node_id, callee=succ, action="default", data={"caller_user_prompt": prompt, "caller_output_message": task_result})
    
    return task_result