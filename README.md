# MAS

## Usage

- setup

```bash
$ pip install -r requirements.txt
```

- examples

```bash
$ python experiments/example_factory.py
$ python experiments/example_all.py
$ pytest
```

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
    - SimpleChainExecutor: simple for loop execution
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

- [ ] add more tools
- [ ] add more models
- [ ] implement LLM-based orchestrators
- [ ] improve flow executor to support branching-flow
- [ ] test multi-modality
- [ ] test different storage
- [ ] support fix-workflow agents?
