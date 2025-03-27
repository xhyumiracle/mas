import logging
from dataclasses import dataclass, field
import yaml, os, json
from pydantic import BaseModel, ValidationError
from typing import List, Optional
from pathlib import Path
from openai import OpenAI
from tenacity import RetryCallState, retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from mas.errors.orch_error import OrchestrationError
from mas.orch.parser import YamlParser, JsonParser
from mas.graph.agent_task_graph import AgentTaskGraph
from mas.orch import Orchestrator
from mas.message import Message

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class Agent(BaseModel):
    id: int
    name: str
    profile: str
    prompt: str
    model: str
    tools: List[str]
    input: List[str]
    output: List[str]

class Workflow(BaseModel):
    agents: List[Agent]
    edges: List[List[int]]


@dataclass
class LLMOrch(Orchestrator):
    base_model: str = 'gpt-4o'  # More generally: assume this is the LLM client or interface
    client = OpenAI(base_url=os.getenv('OPENAI_BASE_URL'), api_key=os.getenv('OPENAI_API_KEY')) # necessary to define it here otherwise openai's chat completion will return error
    updated_prompt: str = field(init=False)

    def __post_init__(self):
        models = self.model_pool.all_names_and_descriptions()
        tools = self.tool_pool.all_names_and_descriptions()
        modalities = '{text, image, video, audio}'
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
        # Update system prompt with models, tools, and modalities
        self.updated_prompt = (
            sys_msg
            .replace('{model_list}', yaml.dump(models))
            .replace('{tool_list}', yaml.dump(tools))
            .replace('{modalities}', modalities)
        )
    
    @staticmethod
    def get_paths():
        """Returns the paths needed for process_prompt as a tuple."""
        from pathlib import Path
        current_dir = Path(__file__).parent
        prompt_path = current_dir / "prompt.yaml"
        models_path = current_dir / "models"
        tools_path = current_dir / "tools"
        return prompt_path, models_path, tools_path

    def get_structured_output(self, messages:List[Message] , Print:bool=True) -> Workflow:
        """
        Let LLM generate a structured output for the task graph
        """
        
        # def process_input(s):
        #     """Process input file or string based on its extension: json/yaml or string ready for use"""
        #     if s.endswith('.json'):
        #         with open(s, 'r') as file:
        #             data = json.load(file)
        #             s = json.dumps(data)
        #     elif s.endswith('.yaml'):
        #         with open(s, 'r') as file:
        #             data = yaml.safe_load(file)
        #             s = yaml.dump(data, default_flow_style=False)
        #     return s
        # # Load models and tools from files
        # current_dir = Path(__file__).parent
        # models_path = str(current_dir / "models.json")
        # tools_path = str(current_dir / "tools.json")

        # models = process_input(models_path)
        # tools = process_input(tools_path)

        # print(updated_prompt)
        
        logger.info(f"LLMOrch: messages: {messages}")
        resp_message = None
        try:
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=messages,
                response_format=Workflow,
            )
            # Extract and return the workflow
            resp_message = completion.choices[0].message
        except ValidationError as e:
            raise OrchestrationError(f"Invalid structured output format, can't parse it")
        
        if Print:
            print(resp_message.parsed.model_dump_json(indent=2))
        return resp_message
    
    
    def generate_by_message(self, user_message, historical_messages) -> AgentTaskGraph:
        """Generate an AgentTaskGraph from a sequence of messages."""
        
        ''' Retry logic '''
        # Shared context that changes between retries
        retry_context_messages = []

        # Hook for tenacity to call before each retry sleep
        def before_retry(retry_state: RetryCallState):
            # append output to retry
            err = retry_state.outcome.exception()
            logger.warning(f"Retry LLMOrch.generate due to an Exception: {err}")
            if err:
                retry_context_messages.append({"role": "user", "content": str(err)})
            else:
                logger.warning("No exception found, this should not happen")
        ''' Retry logic end'''

        @retry(
            stop=stop_after_attempt(3), # retry times
            wait=wait_fixed(1),         # wait time between retries
            retry=retry_if_exception_type(OrchestrationError),
            before_sleep=before_retry
        )
        def run_once(original_messages: List[Message]) -> AgentTaskGraph:
            full_messages = original_messages + retry_context_messages
            llm_output_message = self.get_structured_output(full_messages) # it's a dict

            # append output to retry
            retry_context_messages.append(llm_output_message)

            workflow = llm_output_message.parsed
            json_string = workflow.model_dump_json()
            parser = JsonParser()
            graph = parser.parse_from_string(json_string)
            return graph
        
        messages=[
            *historical_messages,
            {"role": "system", "content": self.updated_prompt},
            user_message.to_dict(),
        ]

        graph = run_once(messages)

        return graph

