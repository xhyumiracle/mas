from dataclasses import dataclass
from mas.orch.parser import YamlParser, JsonParser
from mas.graph.agent_task_graph import AgentTaskGraph
from mas.orch import Orchestrator
from mas.message import Message
import yaml, os, json
from pydantic import BaseModel
from typing import List
from pathlib import Path
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()



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


@dataclass
class LLMOrch(Orchestrator):
    user_request: str
    base_model: str = 'gpt-4o'  # More generally: assume this is the LLM client or interface
    client = OpenAI(base_url=os.getenv('OPENAI_BASE_URL'), api_key=os.getenv('OPENAI_API_KEY')) # necessary to define it here otherwise openai's chat completion will return error

    @staticmethod
    def get_paths():
        """Returns the paths needed for process_prompt as a tuple."""
        from pathlib import Path
        current_dir = Path(__file__).parent
        prompt_path = current_dir / "prompt.yaml"
        models_path = current_dir / "models"
        tools_path = current_dir / "tools"
        return prompt_path, models_path, tools_path

    def get_structured_output(self, user_input:str, Print:bool=True) -> Workflow:
        """
        Let LLM generate a structured output for the task graph
        """
        # Default system message if none provided
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
    Return the list of agents and edges.'''
        
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
        # # Load models and tools from files
        # current_dir = Path(__file__).parent
        # models_path = str(current_dir / "models.json")
        # tools_path = str(current_dir / "tools.json")

        # models = process_input(models_path)
        # tools = process_input(tools_path)

        ''' Load models and tools from pools '''

        models = self.model_pool.all_names_and_descriptions()
        tools = self.tool_pool.all_names_and_descriptions()
        modalities = '{text, image, video, audio}'

        # Update system prompt with models, tools, and modalities
        updated_prompt = (
            sys_msg
            .replace('{model_list}', yaml.dump(models))
            .replace('{tool_list}', yaml.dump(tools))
            .replace('{modalities}', modalities)
        )
        print(updated_prompt)
        
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": updated_prompt},
                {"role": "user", "content": user_input},
            ],
            response_format=Workflow,
        )
        # Extract and return the workflow
        workflow = completion.choices[0].message.parsed
        
        if Print:
            print(workflow.model_dump_json(indent=2))
        return workflow
        


    def generate_by_messages(self) -> AgentTaskGraph:
        """Generate an AgentTaskGraph from a sequence of messages."""
        # Prepare system and user prompts
        llm_output = self.get_structured_output(self.user_request) # it's a dict
        json_string = llm_output.model_dump_json()
        parser = JsonParser()
        graph = parser.parse_from_string(json_string)

        return graph

