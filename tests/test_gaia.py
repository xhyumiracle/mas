from dotenv import load_dotenv

from mas.orch.planner import Planner
from mas.executor.sequential import SequentialExecutor
from mas.curator.mock import MockCurator
load_dotenv()

import logging

from mas.mas import MasFactory

logger = logging.getLogger(__name__)

def test_mas():
    query = "If Eliud Kipchoge could maintain his record-making marathon pace indefinitely, how many thousand hours would it take him to run the distance between the Earth and the Moon its closest approach? Please use the minimum perigee value on the Wikipedia page for the Moon when carrying out your calculation. Round your result to the nearest 1000 hours and do not use any comma separators if necessary."

    mas = MasFactory(
        cls_Orch=Planner,
        cls_Executor=SequentialExecutor,
        cls_Curator=MockCurator,
    )
    mas.build()
    mas.run(query)