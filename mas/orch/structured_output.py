from pydantic import BaseModel
from openai import OpenAI
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

class Agent(BaseModel):
    id: int
    name: str
    profile: str
    prompt: str

class Workflow(BaseModel):
    agents: List[Agent]
    edges: List[Tuple[int, int]]

sys_msg = '''You are an AI designed to create a multi-agent workflow to address the user's task by breaking it down into discrete, logical steps, each handled by a specialized AI agent. 
Your goal is to generate a structured output compatible with OpenAI's structured output model for GPT-4o. Represent the workflow as a directed acyclic graph (a tree), where nodes are agents performing unique tasks and edges show the flow of information between them. 
Ensure critical data flows to the appropriate agents at the right time, with the final agent’s output directly answering the user’s request. 
Prioritize simplicity and efficiency by minimizing the number of agents and steps while ensuring accurate, high-quality results.
Define each agent with:
  - id: Agent's index (in the correct order starting with 1)
  - name: Short name reflecting the agent’s role
  - profile: System prompt specifying the agent’s role and precise behavior
  - prompt: Clear, detailed task instruction(s) for the agent to complete its task 
Define an edge from node a to node b with [a,b].
'''

completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": "Design a multi-agent system for automating research paper summarization."},
    ],
    response_format=Workflow,
)

workflow = completion.choices[0].message.parsed
print(workflow.model_dump_json(indent=2))
