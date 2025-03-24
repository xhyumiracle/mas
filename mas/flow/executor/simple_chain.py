from dataclasses import dataclass
from mas.flow.executor.base import FlowExecutor
from mas.memory.memory import FlowMemory
from mas.message import Message
from mas.graph import AgentTaskGraph

class SimpleChainExecutor(FlowExecutor):

    def run(self, graph: AgentTaskGraph, memory: FlowMemory) -> Message:
        for node_id in self.execution_chain:
            agent = graph.nodes[node_id]["agent"]
            request = Message(role="user", content=f"Hi Agent[id={node_id}]")
            response = agent.run(message=request)
            request.pprint()
            response.pprint()
        print("Chain executed successfully")
        return response