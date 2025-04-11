# MAS

## Quick Start

- setup

> requirements: python>=3.11

```base
$ conda create -n mas python=3.11
$ conda activate mas
```

```bash
$ pip install -r requirements.txt
```

- examples

```bash
$ python experiments/example_factory.py
$ python experiments/example_all.py
$ pytest
```

## Usage
```python
from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)

from mas.mas import MasFactory
from mas.orch import MockOrch
from mas.curator import ModelCurator, ToolCurator
from mas.flow import PocketflowExecutor
from mas.agent import MockAgent, AgnoAgent

logger = logging.getLogger(__name__)

mas = MasFactory(
    cls_Orch=MockOrch,
    cls_Curators=[ModelCurator, ToolCurator],
    cls_Executor=PocketflowExecutor,
)
mas.build()
mas.run("Write a story in George R.R. Martin's style")
```

### Adding Tools
1. Implement `Toolkit` class
```python
from mas.tool.base import Toolkit

class MockTextToTextTool(Toolkit):
    def __init__(self):
        super().__init__(
            name="mock_text_to_text",
            description="test only", # tool set description for orchestrator to see
            tools=[self.mock_text_to_text] # active tools
        )

    @staticmethod # tool can be either @staticmethod or not, both work
    def mock_text_to_text(query: str) -> str:
        """test only tool, don't use unless""" # tool function description for LLM to decide which tool to call
        return "mock result for " + query
```

1. Add to the global TOOLS in `mas/tool/tools/__init__.py`

```python
# import your tool class
from mas.tool.tools.mock import MockTextToTextTool

# add to TOOLS
TOOLS = (
    TOOLS 
    | MockTextToTextTool().to_dict()
```

> hint: To test your tool, use `pytest tests/test_tool.py -s`

### Adding Models

1. Implement `Model` class

```python
from typing import Dict, Any, List, Sequence, Callable
from mas.model.base import Model
from mas.message import Message

class GPT4o(Model):
    async def run(self, messages: List[Message], tool_definitions: List[Dict[str, Any]] = None) -> Message:
        pass
    
    def create_tool_definitions(self, tools: List[Callable]) -> List[Dict[str, Any]]:
        pass
```

2. Add to the global MODELS in `mas/model/models/__init__.py`

```python
from .openai import GPT4o

MODELS = {
    "gpt-4o": {
        "class": GPT4o,
        "description": "OpenAI GPT-4o"
    }
}
```
> hint: To test your model, use `pytest tests/test_model.py -s`

### Adding Agents

1. Implement `Agent` class

```python
from typing import Optional, Sequence
from mas.agent import Agent
from mas.message import Message, Part
class MockAgent(Agent):

    async def _run(
        self,
        goal: Message,
        observations: Optional[Sequence[Message]],
    ) -> Message:
        return Message(role="assistant", parts=[Part(text=f"Hello, I am Agent[id={self.id}]), my goal is: {goal}")])
```

2. Add to `mas/agent/factory.py`

## Introduction
![MAS framework](assets/arch.png)

MAS is a framework for building autonomous multi-agent systems (MAS).

"The less, the better."

MAS is designed to be modular and extensible, almost all components are pluggable.

**Key features:**
- Separating *Execution Flow* from *Agent Task Graph*:
  - allowing flexible control over the execution style
- Separating *Curation* from *Orchestration*, allowing orchestrator focus on the task graph generation, while curators focus on resolving the specific agent settings
- Multi-modality:
  - supporting image, video, audio, file, etc.
  - supporting modality validation over the graph
- Shared memory:
  - the global execution trace is available among all agents
- Minimum fixed interface:
  - AgentTaskGraph, AgentTaskFlow, Message, Flow Memory are fixed structure, capturing the minimum yet critical interfaces to modeling the MAS problem.
  - Others are customizable or modularized, allowing you to leverage any existing frameworks or implement your own.

**Modularized components:**
- Modularized *Orchestrator*:
  - you can implement your own orchestrator, with different graph generation strategies
- Modularized *Flow Executor*: 
  - you can use any workflow-style framework, e.g. Pocketflow etc.
  - you can also implement your own executor, e.g. simple chain executor
- Modularized *Agent*: 
  - you can use any agent framework, e.g. LangChain, Agno (default) etc.
- Customizable *Flow Memory Data*:
  - the flow memory is a map between "(executed) edge" and "data"
  - "data" is a customizable dict
- Modularized *Tool* and *Base Model*:
  - you can implement your own tool and base model, simply by adding to the maps.
- Modularized *Curator*:
  - you can implement your own curator, with different curation strategies
- Modularized *Parser*:
  - customize it to allow parsing arbitrary LLM orchestrator output format
- Modularized *Storage*:
  - you can use any storage to store the flow memory, e.g. InMemoryStorage, RedisStorage, SQLiteStorage etc.

## What's in the box

- Orchestrator: Responsible for generating the agent task graph
  - MockOrch: Mock orchestrator
  - LLMOrch: LLM orchestrator
- Parser: Responsible for parsing the agent task graph from raw formats
  - YamlParser: YAML parser
- AgentTaskGraph:
  - modality validation
- AgentTaskFlow: separating graph with execution flow
  - FlowExecutor: can use any workflow-style framework
    - SimpleSequentialExecutor: simple for loop execution
    - PocketflowExecutor
- Memory: shared memory between agents
- Message: message definition
- Agent: the agent class, can use any framework
  - MockAgent: Mock agent simple fix-answer agent for test
  - AgnoAgent: "Agno" framework agent
- Tool:
  - extent any tool by implementing the Agno's Toolkit interface, and add to TOOLS
- Model:
  - extent any model by implementing the Agno's Model interface, and add to MODELS
- Storage: pluggable storage
  - InMemoryStorage: In-memory storage
  - RedisStorage: Redis storage
  - SqliteStorage: SQLite storage

## TODO

- [X] implement LLM-based orchestrators
- [ ] add enough tools
- [ ] add enough models
- [ ] async flow executor to better support branching-flow
- [ ] test multi-modality
- [ ] test different storage
- [ ] support fix-workflow agents?
- [ ] stream output
