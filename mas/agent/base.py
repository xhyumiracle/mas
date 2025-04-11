from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Literal, Sequence, Optional, Union

from mas.message import Message, Part

@dataclass
class Agent(ABC):
    id: str
    name: str
    input_modality: List[Literal["text", "audio", "image", "video", "file"]]
    output_modality: List[Literal["text", "audio", "image", "video", "file"]]

    async def run(
        self,
        goal: Union[Message, str, Dict],
        observations: Optional[Sequence[Message]] = None,
    ) -> Message:
        """Run the agent with a goal and optional observations.
        
        Args:
            goal: The goal to achieve (can be Message, str, or Dict)
            observations: Optional observations/history messages
            max_iterations: Maximum number of iterations to run
            
        Returns:
            The final response message
        """
        if isinstance(goal, str):
            goal = Message(role="user", parts=[Part(text=goal)])
        elif isinstance(goal, dict):
            goal = Message(**goal)
        return await self._run(goal, observations)

    @abstractmethod
    async def _run(
        self,
        goal: Message,
        observations: Optional[Sequence[Message]],
    ) -> Message:
        """Internal run method that handles Message type goal.
        
        Args:
            goal: The goal to achieve (guaranteed to be Message)
            observations: Optional observations/history messages
            max_iterations: Maximum number of iterations to run
            
        Returns:
            The final response message
        """
        raise NotImplementedError

class IterativeAgent(Agent):
    """Base class for agents that work iteratively towards a goal."""
    async def _run(
        self,
        goal: Message,
        observations: Optional[Sequence[Message]],
    ) -> Message:
        return await self._run_iterative(goal, observations, max_iterations=10)

    async def _run_iterative(
        self,
        goal: Message,
        observations: Optional[Sequence[Message]],
        *,
        max_iterations: int = 10,
    ) -> Message:
        observations = list(observations) if observations else []
        
        for _ in range(max_iterations):
            # 1. Act based on current state
            result = await self.act(goal, observations)
            observations.append(result)
            
            # 2. Evaluate if goal is achieved
            if await self.evaluate(goal, observations):
                break
                
        return observations[-1]  # Return the last result
    
    @abstractmethod
    async def act(self, goal: Message, observations: Sequence[Message]) -> Message:
        """Take an action based on goal and current observations.
        
        Args:
            goal: The goal to achieve
            observations: Current observations/history
             
        Returns:
            The result of the action
        """
        pass
        
    @abstractmethod
    async def evaluate(self, goal: Message, observations: Sequence[Message]) -> bool:
        """Evaluate if the goal has been achieved.
        
        Args:
            goal: The goal to achieve
            observations: Current observations/history
            
        Returns:
            True if goal is achieved, False otherwise
        """
        pass
