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
    cls_Executor=PocketflowExecutor,
    cls_Agent=MockAgent,
    cls_Curators=[ModelCurator, ToolCurator],
    executor_is_chain=True,
)
mas.build()
mas.run("Write a story in George R.R. Martin's style")