from mas.mas import MasFactory
from mas.agent.agno import AgnoAgent
from mas.agent.mock import MockAgent
from mas.orch.mock import MockOrch
from mas.orch.parser.yaml import YamlParser
from mas.flow.executor.pocketflow import PocketflowExecutor
from mas.tool import TOOLS
from mas.model import MODELS

mas = MasFactory(
    cls_Orch=MockOrch,
    cls_Executor=PocketflowExecutor,
    cls_Agent=MockAgent,
    cls_Parser=YamlParser,
    executor_is_chain=True,
    model_map=MODELS,
    tool_map=TOOLS,
)

mas.build()
mas.run("Write a story in George R.R. Martin's style")