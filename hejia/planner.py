import time
import logging
from dotenv import load_dotenv
from openai import OpenAI
import os
from typing import List, Dict, Literal
from pydantic import BaseModel
from collections import deque
import sys
import os

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

TASK_PLANNER_SYSTEM_PROMPT = '''You are a task planner for a multi-agent system (MAS). Your goal is to decompose a complex user-defined task into a directed acyclic graph (DAG), where:
- Each node represents a semantically consistent subtask that will later be assigned to independent expert AI agents;
- Each edge represents a dependency, indicating that one task must be completed before another task can be started.

When decomposing tasks, strictly follow the following principles:

1. Expert granularity: Design each subtask as if it were assigned to a human expert in a collaborative environment. Each subtask should conform to human understanding of efficient teamwork.

2. Occam's razor: Decompose only where necessary to achieve parallel, modular execution. Avoid unnecessary complexity or fragmentation.

3. Language mirroring: Your output must be in the same language as the user's original query. If the user asks in Chinese, answer entirely in Chinese; if the user asks in English, answer in English.

4. Don't execute, just plan: Don't try to solve the task. Your role is limited to building and coordinating the task.'''


load_dotenv()

class DAGNode(BaseModel):
    id: int
    subproblem: str
    input_modality: Literal["text", "image", "video", "audio","file"]
    output_modality: Literal["text", "image", "video", "audio","file"]


class DAGEdge(BaseModel):
    from_id: int
    to_id: int

class SubproblemDAG(BaseModel):
    nodes: List[DAGNode]
    edges: List[DAGEdge]

class TaskGraph:
    """
    TaskGraph is responsible for decomposing complex tasks into subtasks
    using a language model-based approach.
    """

    def __init__(self):
        # Read API key and base URL from environment variables
        oai_api_key = os.getenv('OAI_API_KEY')
        oai_base_url = os.getenv('OAI_BASE_URL')
        self.client_oai = OpenAI(base_url=oai_base_url, api_key=oai_api_key)

    def build_task_graph_oai(self, question: str, difficulty_level: Literal["easy", "medium", "hard"]) -> SubproblemDAG:
        """
        Uses GPT-4 API to decompose a complex question into a Directed Acyclic Graph (DAG) of subtasks.

        Args:
            question (str): The complex task that needs to be decomposed.

        Returns:
            SubproblemDAG: A DAG representation of subtasks.
        """
        if difficulty_level == "easy":
            #如果问题简单，直接返回原问题节点
            return SubproblemDAG(nodes=[DAGNode(id=0, subproblem=question, input_modality="text", output_modality="text")], edges=[])
        else:
            #如果问题中等，使用gpt-4o-2024-08-06模型生成任务图
            messages = [
                {
                    "role": "system",
                    "content": TASK_PLANNER_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": question
                }
            ]

            max_retries = 5
            for attempt in range(max_retries):
                try:
                    response_oai = self.client_oai.beta.chat.completions.parse(
                        model="gpt-4o-2024-08-06",
                        messages=messages,
                        response_format=SubproblemDAG
                    )
                    dag_result = response_oai.choices[0].message.parsed  # Extract structured DAG
                    
                    # 模态一致性检查
                    try:
                        self.validate_modalities(dag_result)
                        print(f"✅ 模态一致性检查通过 (尝试次数 {attempt + 1})")
                        return dag_result  # 返回有效的 DAG
                    except ValueError as e:
                        print(f"❌ 模态不匹配 (尝试次数 {attempt + 1}): {e}")
                        continue  # 重新生成 DAG

                except Exception as e:
                    logging.warning(f"Request failed: {e}. Retrying ({attempt + 1}/{max_retries})...")
                    time.sleep(0.2 ** attempt)  # Exponential backoff for retries

            raise RuntimeError("Maximum retry attempts reached. Unable to obtain a valid response.")



    def validate_modalities(self, dag: SubproblemDAG) -> None:
        """
        Ensure that the output modality of each node matches the input modality of its dependent nodes.
        Raises ValueError if a mismatch is found.
        """
        node_map = {node.id: node for node in dag.nodes}
        
        for edge in dag.edges:
            from_node = node_map[edge.from_id]
            to_node = node_map[edge.to_id]

            if from_node.output_modality != to_node.input_modality:
                raise ValueError(f"模态不匹配: {from_node.subproblem} ({from_node.output_modality}) → "
                                 f"{to_node.subproblem} ({to_node.input_modality})")


    def topological_sort(self, dag: SubproblemDAG) -> List[str]:
        """
        Perform topological sorting on the given DAG and return a list of sorted subproblem strings.

        Args:
            dag (SubproblemDAG): The DAG representation of subtasks.

        Returns:
            List[str]: A list of subproblem descriptions in topological order.
        """
        # Step 1: Build adjacency list and in-degree map
        adj_list: Dict[int, List[int]] = {node.id: [] for node in dag.nodes}
        in_degree: Dict[int, int] = {node.id: 0 for node in dag.nodes}
        
        for edge in dag.edges:
            adj_list[edge.from_id].append(edge.to_id)
            in_degree[edge.to_id] += 1

        # Step 2: Topological sorting using Kahn's algorithm
        queue = deque([node.id for node in dag.nodes if in_degree[node.id] == 0])
        sorted_subproblems = []

        node_map = {node.id: node.subproblem for node in dag.nodes}

        while queue:
            node_id = queue.popleft()
            sorted_subproblems.append(node_map[node_id])  # Append problem statement
            
            for neighbor in adj_list[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(sorted_subproblems) != len(dag.nodes):
            raise ValueError("Cycle detected in the DAG, topological sorting failed!")

        return sorted_subproblems

    def to_mermaid(self, dag: SubproblemDAG) -> str:
        """
        Convert the given DAG into Mermaid.js syntax.
        """
        mermaid_str = "graph TD\n"
        
        # node_map = {node.id: f"{node.id}[{node.subproblem} ({node.input_modality} → {node.output_modality})]" 
        node_map = {node.id: f"{node.id}[{node.subproblem}]"
                    for node in dag.nodes}

        for edge in dag.edges:
            from_node = node_map[edge.from_id]
            to_node = node_map[edge.to_id]
            mermaid_str += f"  {from_node} --> {to_node}\n"

        return mermaid_str
