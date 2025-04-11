import logging
from dataclasses import dataclass
import os
from pydantic import BaseModel
from openai import OpenAI
from mas.graph.task_graph import TaskGraph
from mas.orch import Orchestrator
from dotenv import load_dotenv
from typing import List, Dict, Literal, Tuple
import time
from collections import deque
from typing import List
from mas.graph.types import NodeAttr, EdgeAttr, NodeId
from mas.graph.task_graph import TaskGraph
from mas.model.models.openai import Openai


load_dotenv()

logger = logging.getLogger(__name__)

class DAGNode(BaseModel):
    id: int
    subproblem: str
    input_modalities: List[Literal["text", "image", "video", "audio", "file"]]
    output_modalities: List[Literal["text", "image", "video", "audio", "file"]]

class DAGEdge(BaseModel):
    from_id: int
    to_id: int

class TaskDAG(BaseModel):
    nodes: List[DAGNode]
    edges: List[DAGEdge]


@dataclass
class Planner(Orchestrator):
    def __init__(self, base_model: str = 'gpt-4o-2024-08-06'):
        oai_api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=oai_api_key)
        self.base_model = base_model

    def generate_by_message(self, user_message, historical_messages) -> TaskGraph:
        """Generate an AgentTaskGraph from a sequence of messages."""
        
        ''' Retry logic '''
        messages = [
            {
                "role": "system",
                "content": "You are an expert in breaking down tasks into Directed Acyclic Graphs (DAGs) with modality constraints. "
                           "Each subproblem must have a unique integer ID, a short description, an input modality, and an output modality. "
                           "ONLY use text modality unless the user explicitly mentions another modality."
                           "Ensure that an edge (Y -> X) only exists if Y's output modality matches X's input modality."
            },
            *Openai.format_message(user_message),

        ]

        max_retries = 5
        for attempt in range(max_retries):
            try:
                response_oai = self.client.beta.chat.completions.parse(
                    model=self.base_model,
                    messages=messages,
                    response_format=TaskDAG
                )
                dag_result = response_oai.choices[0].message.parsed  # Extract structured DAG
                print("agent_task_graph", dag_result)

                agent_task_graph = self.convert_to_task_graph(dag_result)
                # 模态一致性检查
                try:
                    # 假设graph是一个AgentTaskGraph的实例
                    agent_task_graph.validate()
                    print("验证成功")
                    return agent_task_graph
                except Exception as e:
                    print(f"验证失败: {e}")

            except Exception as e:
                logging.warning(f"Request failed: {e}. Retrying ({attempt + 1}/{max_retries})...")
                time.sleep(0.2 ** attempt)  # Exponential backoff for retries
        
    def convert_to_task_graph(self, task_dag: TaskDAG) -> TaskGraph:
        # Step 1: 转换节点
        typed_nodes: List[Tuple[NodeId, NodeAttr]] = []
        print("------------task_dag", task_dag)
        for node in task_dag.nodes:
            node_id = node.id
            node_attr = NodeAttr(
                id=node_id,
                task=node.subproblem,
                input_modalities=node.input_modalities,
                output_modalities=node.output_modalities
            )
            typed_nodes.append((node_id, node_attr))
        
        # Step 2: 转换边
        typed_edges: List[Tuple[NodeId, NodeId, EdgeAttr]] = []
        for edge in task_dag.edges:
            edge_attr = EdgeAttr(label=None)  # 可自定义逻辑
            typed_edges.append((edge.from_id, edge.to_id, edge_attr))
        
        # Step 3: 构造 AgentTaskGraph
        agent_graph = TaskGraph(
            nodes=typed_nodes,
            edges=typed_edges
        )

        return agent_graph
    


        



