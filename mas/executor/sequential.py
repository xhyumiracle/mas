import logging
from typing import List, AsyncIterator
from mas.agent.base import Agent
from mas.agent.llm import LLMAgent
from mas.memory.flowmemory import FlowMemory
from mas.message import Message, Part
from mas.graph import TaskGraph
from mas.executor.base import GraphExecutor

logger = logging.getLogger(__name__)

class SequentialExecutor(GraphExecutor):

    async def run(self) -> AsyncIterator[Message]:
        """Execute the flow step by step, yielding each result."""
        sequential_order = list(self.graph.topological_sort())

        '''
        shared memory
        '''
        shared = {
            "graph": self.graph,
            "memory": self.memory,
            "filemap": self.filemap
        }

        for node_id in sequential_order:
            agent = self.graph.nodes[node_id]["agent"]
            task = self.graph.nodes[node_id]["task"]
            observations = self.prep_obsverations(node_id, shared)

            if isinstance(agent, LLMAgent): # LLMAgent need shared filemap before run
                agent.set_filemap(self.filemap)

            response = await self.exec(node_id, agent, task, observations, shared)
            yield response
    
    @staticmethod
    def prep_obsverations(node_id, shared_memory) -> List[Message]:
        mem: FlowMemory = shared_memory["memory"]
        graph: TaskGraph = shared_memory["graph"]
        
        """create the input messages: [predecessor user task, predecessor output] + current task """

        observations = []
        for pred in graph.predecessors(node_id):
            _pred_data = mem.get_data(pred, node_id, "default")
            pred_user_prompt = _pred_data["caller_user_prompt"]
            pred_output_message = _pred_data["caller_output_message"]
            observations.append(Message(role="user", parts=[Part(text=pred_user_prompt)]))
            observations.append(pred_output_message)
        
        return observations

    @staticmethod
    async def exec(node_id, agent: Agent, task: str, observations: List[Message], shared_memory):

        """ execute the task by given agent """
        logger.info(f"---------Running Agent[id={node_id}]")

        task_result = await agent.run(goal=task, observations=observations)
        
        """ result """
        logger.info(f"---------Agent[id={node_id}] complete")
        
        """ save to shared memory """
        successors = list(shared_memory["graph"].successors(node_id))
        
        if not any(successors):
            logger.debug('no successors, im the last node, writting results')
            shared_memory["final_output_message"] = task_result

        for succ in successors:
            shared_memory["memory"].add_entry(caller=node_id, callee=succ, label="default", data={"caller_user_prompt": task, "caller_output_message": task_result})
        
        return task_result