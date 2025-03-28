import logging
from typing import List
from mas.agent import Agent
from mas.message import Message, pprint_messages
from mas.memory.memory import FlowMemory
from mas.graph.agent_task_graph import AgentTaskGraph
from mas.flow import FlowExecutor
from pocketflow import Node, BatchNode, Flow

logger = logging.getLogger(__name__)

class PocketflowExecutor(FlowExecutor):

    def run(self, graph: AgentTaskGraph, memory: FlowMemory) -> Message:

        if not self.is_chain:
            raise Exception("PocketflowExecutor currently only supports chain execution")
        '''
        shared memory
        '''
        shared = {
            "graph": graph,
            "memory": memory
        }

        '''
        create agents and nodes
        '''
        # nodes = {}
        # for id in graph.nodes.keys():
        #     node_attr = graph.get_node_attr(id)
        #     # agent = MockAgent(id=id, node_attr=node_attr)
        #     agent = AgnoAgent(id=id, node_attr=node_attr)
        #     nodes[id] = FlowNode(agent, node_attr.prompt, node_attr.input_formats, node_attr.output_formats)
        nodes = {
            node_id: FlowNode(attr["agent"], attr["prompt"], attr["input_formats"], attr["output_formats"])
            for node_id, attr in graph.nodes(data=True)
        }
        
        '''
        assemble the flow, compatible with any iterator
        '''
        start_node = None
        previous_id = -1
        for id in self.execution_chain:
            if previous_id == -1:
                start_node = nodes[id]
            else:
                nodes[previous_id] >> nodes[id]
            previous_id = id
        '''
        run the flow
        '''
        flow = Flow(start=start_node)
        flow.run(shared)

        return shared["final_output_message"]
        

class FlowNode(Node):
    # retry_prompt = "Please adjust your output based on the feedback from the reviewer."

    def __init__(self, agent: Agent, default_prompt: str, input_formats: List[str], output_formats: List[str]):
        super().__init__()
        self.agent = agent
        self.default_prompt = default_prompt
        self.input_formats = input_formats
        self.output_formats = output_formats

    def prep(self, shared):
        mem: FlowMemory = shared["memory"]
        graph: AgentTaskGraph = shared["graph"]
        
        '''
        create the input messages: [predecessor user prompt, predecessor output] + current user prompt
        '''
        messages = []
        for pred in graph.predecessors(self.agent.id):
            _pred_data = mem.get_data(pred, self.agent.id, "default")
            pred_user_prompt = _pred_data["caller_user_prompt"]
            pred_output_message = _pred_data["caller_output_message"]
            messages.append(Message(role="user", content=pred_user_prompt))
            messages.append(pred_output_message)
        
        # add the current user prompt to the last message, to help the agent understand the context
        messages.append(Message(role="user", content=self.default_prompt))

        return messages
    
        # if not self.condition(shared):
        #     return None
        # task = None
        # if action == 'reject': # if action is reject, re-run the task based on (the non-loop outputs + reject feedback)
        #     task = self.retry_task + shared["execution"]["data"][myid][caller][action]
        # else: # assemble inputs #TODO(flow): multi action to same target
        #     task = self.default_prompt + "\n\n<context>\n"
        #     for _caller, _action in in_arcs:
        #         if _action != 'reject':
        #             task += "Agent"+_caller+":\n"
        #             task += shared["execution"]["data"][myid][_caller][_action]

        #TODO if action is approve, use my last output as the input for my succcessors
    
    def exec(self, messages):

        logger.info(f"Running Agent[id={self.agent.id}] with input:")
        pprint_messages(messages)

        response_message = self.agent.run(messages=messages)
        
        logger.info(f"Agent[id={self.agent.id}] complete with response:")
        pprint_messages([response_message])
        
        return response_message

    def post(self, shared, prep_res, exec_res: Message):
        # set execution
        action = "default"
        successors = list(shared["graph"].successors(self.agent.id))
        
        if not any(successors):
            logger.debug('no successors, im the last node, writting results')
            shared["final_output_message"] = exec_res

        for succ in successors:
            shared["memory"].add_entry(caller=self.agent.id, callee=succ, action=action, data={"caller_user_prompt": self.default_prompt, "caller_output_message": exec_res})
        
        return action
    
    # def condition(self, shared):
    #     myid = self.agent.agent_id
    #     # get my latest caller info
    #     callers_info = shared["execution"]["callers"][myid]
    #     callers = [x[0] for x in callers_info]
    #     actions = [x[1] for x in callers_info]
    #     if callers_info:
    #         caller, action = callers[-1], actions[-1]
        
    #     # if no caller, i'm the start node, run default task
    #     if caller is None:
    #         return True
        
    #     # skip if any non-loop predecessor hasn't finish
    #     in_arcs = shared["graph"]["in_arcs"][myid]
    #     for in_arc in in_arcs:
    #         if in_arc not in callers:
    #             return False

#TODO: ReviewerNode