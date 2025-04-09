import logging
from typing import List
from mas.agent.base import Agent
from mas.flow.executor.base import FlowExecutor
from mas.memory.memory import FlowMemory
from mas.message import Message
from mas.graph import AgentTaskGraph
from mas.message.message import pprint_messages

logger = logging.getLogger(__name__)

class SequentialExecutor(FlowExecutor):

    def run(self, graph: AgentTaskGraph, memory: FlowMemory) -> Message:
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
            request = prep_request(node_id, prompt, shared)
            # pprint_messages(request)
            response = exec(node_id, agent, request, prompt, shared)
            # response.pprint()
            yield response
        
        # return response

    # retry_prompt = "Please adjust your output based on the feedback from the reviewer."

def prep_request(node_id, prompt, shared_memory) -> List[Message]:
    mem: FlowMemory = shared_memory["memory"]
    graph: AgentTaskGraph = shared_memory["graph"]
    
    """create the input messages: [predecessor user prompt, predecessor output] + current user prompt """

    messages = []
    for pred in graph.predecessors(node_id):
        _pred_data = mem.get_data(pred, node_id, "default")
        pred_user_prompt = _pred_data["caller_user_prompt"]
        pred_output_message = _pred_data["caller_output_message"]
        messages.append(Message(role="user", content=pred_user_prompt))
        messages.append(pred_output_message)
    
    # add the current user prompt to the last message, to help the agent understand the context
    messages.append(Message(role="user", content=prompt))

    return messages

def exec(node_id, agent: Agent, messages, prompt, shared_memory):

    """ execute the task by given agent """
    logger.info(f"Running Agent[id={node_id}] with input:")
    pprint_messages(messages)

    task_result = agent.run(messages=messages)
    
    """ result """
    logger.info(f"Agent[id={node_id}] complete with response:")
    pprint_messages([task_result])
    
    """ save to shared memory """
    successors = list(shared_memory["graph"].successors(node_id))
    
    if not any(successors):
        logger.debug('no successors, im the last node, writting results')
        shared_memory["final_output_message"] = task_result

    for succ in successors:
        shared_memory["memory"].add_entry(caller=node_id, callee=succ, action="default", data={"caller_user_prompt": prompt, "caller_output_message": task_result})
    
    return task_result