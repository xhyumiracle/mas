import asyncio
from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)

from mas.mas import MasFactory
from mas.orch import MockOrch, LLMOrch
from mas.curator import ModelCurator, ToolCurator
from mas.flow import PocketflowExecutor, SequentialExecutor

logger = logging.getLogger(__name__)
from mas.utils.logging import init_logging

# Initialize logging with colors
init_logging()

mas = MasFactory(
    cls_Orch=LLMOrch,
    cls_Executor=SequentialExecutor,
    cls_Curators=[ModelCurator, ToolCurator],
)
mas.build()
# mas.run("Write a story in George R.R. Martin's style")
asyncio.run(mas.run("Generate a short movie with sound about HarryPotter fighting, you should first generate 3 storyboard images then proceed. ONLY use mock tool set"))