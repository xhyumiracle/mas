import time
import logging
from dotenv import load_dotenv
from openai import OpenAI
import os
from typing import Literal
from pydantic import BaseModel

load_dotenv()

# I designed this class to select the appropriate LLM model for the question.
# Data is referenced from the following link: https://openrouter.ai/rankings -> top this week
# Only keep the model with APIs


QUESTION_CLASSIFIER_SYSTEM_PROMPT = """
You are a question classifier that categorizes user questions into predefined categories based on content, context, and intent. 
"""


class QuestionCategory(BaseModel):
    category: Literal["Roleplay", "Programming", "Marketing", "Marketing/Seo", "Technology", "Science", "Translation", "Legal", "Finance", "Health", "Trivia", "Academia"]



class QuestionClassifier:
    """
    Classify the category of a natural language question.
    """

    def __init__(self):
        # Read API key and base URL from environment variables
        oai_api_key = os.getenv('OAI_API_KEY')
        oai_base_url = os.getenv('OAI_BASE_URL')
        self.client_oai = OpenAI(base_url=oai_base_url, api_key=oai_api_key)
    
    def category_to_llm(self, category: str) -> str:
        """
        Map the category to the corresponding LLM model.
        """
        model_map = {
            "Roleplay": "Google: Gemini 2.0 Flash",
            "Programming": "Anthropic: Claude 3.7 Sonnet",
            "Marketing": "Google: Gemini 2.0 Flash",
            "Marketing/Seo": "Google: Gemini 1.5 Flash",
            "Technology": "OpenAI: GPT-4o-mini",
            "Science": "OpenAI: GPT-4o-mini",
            "Translation": "Google: Gemini 2.0 Flash",
            "Legal": "OpenAI: GPT-4o-mini",
            "Finance": "DeepSeek: DeepSeek V3 0324",
            "Health": "Google: Gemma 3 4B",
            "Trivia": "Google: Gemini 2.0 Flash",
            "Academia": "Google: Gemini 1.5 Flash"
        }
        return model_map.get(category)
    def classify_question(self, question: str) -> str:
        """
        Uses GPT-4 API to classify the category of a question.

        Args:
            question (str): The natural language question to classify.

        Returns:
            str: The category of the question.
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
                    response_format=QuestionCategory
                )
                answer = response_oai.choices[0].message.parsed
                model = self.category_to_llm(answer.category)
                return model
            except Exception as e:
                logging.warning(f"Request failed: {e}. Retrying ({attempt + 1}/{max_retries})...")
                time.sleep(0.2 ** attempt)

        raise RuntimeError("Maximum retry attempts reached. Unable to obtain a valid response.")

if __name__ == "__main__":
    question_classifier = QuestionClassifier()
    question = "What is the capital of France?"
    category = question_classifier.classify_question(question)
    print(category)
