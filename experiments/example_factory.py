import logging
from mas.mas import MasFactory
from mas.orch import MockOrch
from mas.orch.parser import YamlParser
from mas.curator import ModelCurator, ToolCurator
from mas.flow import PocketflowExecutor
from mas.agent import MockAgent, AgnoAgent
from mas.tool import TOOLS
from mas.model import MODELS

logging.basicConfig(level=logging.NOTSET)

from dotenv import load_dotenv
load_dotenv()

mas = MasFactory(
    model_map=MODELS,
    tool_map=TOOLS,
    cls_Orch=MockOrch,
    cls_Parser=YamlParser, # optional
    cls_Executor=PocketflowExecutor,
    cls_Agent=MockAgent,
    cls_Curators={"model": ModelCurator, "tool": ToolCurator},
    executor_is_chain=True,
)

mas.build()
mas.run("Write a story in George R.R. Martin's style")