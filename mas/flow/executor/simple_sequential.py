import logging
from mas.flow.executor.base import FlowExecutor
from mas.memory.memory import FlowMemory
from mas.message import Message
from mas.graph import AgentTaskGraph

logger = logging.getLogger(__name__)

class SimpleSequentialExecutor(FlowExecutor):

    def run(self, graph: AgentTaskGraph, memory: FlowMemory) -> Message:
        self.sequential_order = list(graph.topological_sort())

        for node_id in self.sequential_order:
            agent = graph.nodes[node_id]["agent"]
            request = Message(role="user", content=f"Hi Agent[id={node_id}]")
            response = agent.run(message=request)
            request.pprint()
            response.pprint()
        logger.info("Sequential order executed successfully")
        return response
    
    def get_execution_order_str(self):
        return '->'.join([str(i) for i in self.sequential_order])