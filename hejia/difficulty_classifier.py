import time
import logging
from dotenv import load_dotenv
from openai import OpenAI
import os
from typing import Literal
from pydantic import BaseModel


QUESTION_CLASSIFIER_SYSTEM_PROMPT = """
You are a problem difficulty classifier that categorizes user questions into three levels of difficulty, based on the problem's cognitive complexity, tool requirements, estimated time a human expert would need to solve it, and the mode of interaction between humans and AI systems.

Please follow these principles:

1. Easy:
- The problem is routine, well-defined, and bounded.
- A single LLM can generate a high-quality response in a single turn, without needing tools, memory, or external search.
- Requires minimal or no reasoning.
- A competent human could respond within MINUTES.
- AI responds reflexively, like a fast-thinking assistant in conversation.
- Examples: casual dialogue, grammar correction, summarizing short texts, translating simple content, factual questions.

2. Medium:
- The problem requires multiple steps of reasoning, access to real-time or external knowledge, or multimodal/contextual understanding.
- Solving it often involves integration, synthesis, or tool use.
- A competent human would spend HOURS to generate a good solution.
- AI systems operate autonomously as a multi-agent expert team, capable of performing complex workflows without constant human oversight.
- Human input may define goals or constraints, but the AI system delivers the solution independently.
- Examples: writing complex software systems, analyzing multiple documents, querying the internet, formulating business strategies, multimodal input analysis, travel planning.

3. Hard:
- The problem lies at or beyond the frontier of human knowledge.
- Requires deep domain expertise, critical judgment, or original thinking.
- Even experts may take DAYS, WEEKS, or more to explore possible solutions.
- AI systems must be configured as top-tier expert collaborators, working in tight, iterative interaction with human specialists.
- Examples: solving open scientific questions, designing novel medical or engineering systems, conducting philosophical or theoretical inquiries, AI alignment problems.

Your output should be one of: "Easy", "Medium", or "Hard".
"""


load_dotenv()


class DifficultyLevel(BaseModel):
    difficulty_level: Literal["easy", "medium", "hard"]
    
class DifficultyClassifier:
    """
    Classify the difficulty level of a question.
    """

    def __init__(self):
        # Read API key and base URL from environment variables
        oai_api_key = os.getenv('OAI_API_KEY')
        oai_base_url = os.getenv('OAI_BASE_URL')
        self.client_oai = OpenAI(base_url=oai_base_url, api_key=oai_api_key)

    def classify_difficulty(self, question: str) -> str:
        """
        Uses GPT-4 API to classify the difficulty level of a question.

        Args:
            question (str): The complex task that needs to be decomposed.

        Returns:
            SubproblemDAG: A DAG representation of subtasks.
        """
        messages = [
            {
                "role": "system",
                "content": QUESTION_CLASSIFIER_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": question
            }
        ]

        max_retries = 5
        for attempt in range(max_retries):
            try:
                response_oai = self.client_oai.beta.chat.completions.parse(
                    model="gpt-4o-2024-08-06",
                    messages=messages,
                    response_format=DifficultyLevel
                )
                answer = response_oai.choices[0].message.parsed  # Extract structured DAG
                return answer.difficulty_level
            except Exception as e:
                logging.warning(f"Request failed: {e}. Retrying ({attempt + 1}/{max_retries})...")
                time.sleep(0.2 ** attempt)  # Exponential backoff for retries

        raise RuntimeError("Maximum retry attempts reached. Unable to obtain a valid response.")

