from pydantic import BaseModel
from openai import OpenAI
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
load_dotenv()
import yaml, json



class Agent(BaseModel):
    id: int
    name: str
    profile: str
    prompt: str
    model: List[str]
    tools: List[str]
    input: List[str]
    output: List[str]

class Workflow(BaseModel):
    agents: List[Agent]
    edges: List[List[int]]


def process_input(s):
    """Process input file or string based on its extension: json/yaml or string ready for use"""
    if s.endswith('.json'):
        with open(s, 'r') as file:
            data = json.load(file)
            s = json.dumps(data)
    elif s.endswith('.yaml'):
        with open(s, 'r') as file:
            data = yaml.safe_load(file)
            s = yaml.dump(data, default_flow_style=False)
    return s

sys_msg = '''You are an AI designed to create a multi-agent workflow to address the user's task by breaking it down into discrete, logical steps, each handled by a specialized AI agent. 
Your goal is to generate a structured output compatible with OpenAI's structured output model for GPT-4o. Represent the workflow as a directed acyclic graph (a tree), where nodes are agents performing unique tasks and edges show the flow of information between them. 
Ensure critical data flows to the appropriate agents at the right time, with the final agent’s output directly answering the user’s request. 
Prioritize simplicity and efficiency by minimizing the number of agents and steps while ensuring accurate, high-quality results.

Instructions:
- For each agent, determine the following information:
  - id: agent's index (in the correct order starting with 1)
  - name: short name reflecting the agent’s role
  - profile: system prompt specifying the agent’s role and precise behavior
  - prompt: clear, detailed task instruction(s) for the agent to complete its task 
  - model: select a base model that best suits the task from the list below: \n{model_list}
  - tools: list ALL the tools that are necessary or useful for task completion from the list below: \n{tool_list}
  - input: Specify all input modalities involved from {modalities}.
  - output: Specify all output modalities produced from {modalities}.
- List all the edges. Denote an edge from node a to node b as [a,b].
Return the list of agents and edges.
'''
def process_prompt(prompt=sys_msg):# Load the prompt template
    from pathlib import Path
    current_dir = Path(__file__).parent
    models_path = str(current_dir / "models.yaml")
    tools_path = str(current_dir / "tools.json")

    models = process_input(models_path)
    tools = process_input(tools_path)
    modalities = '{text, image, video, audio}'

    updated_prompt = (prompt.replace('{model_list}', models).replace('{tool_list}', tools).replace('{modalities}', modalities))
    print(updated_prompt)
    return updated_prompt

process_prompt()
user_msg = "Read my csv file that contails people's names and a descriptions. Select an appropriate birthday present for each of them, and generate a anime picture for each. Then suggest 3-5 links for birthday presents from online shopping platforms that ship within the US and save the presents names, prices, and the corresponding links to the same csv file. Pay attention that each present should be below $50."

client = OpenAI()
completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": process_prompt()},
        {"role": "user", "content": user_msg},
    ],
    response_format=Workflow,
)
workflow = completion.choices[0].message.parsed
print(workflow.model_dump_json(indent=2))

with open('planner_output.json', 'w') as file:
        json.dump(workflow.model_dump_json(), file, indent=4)

