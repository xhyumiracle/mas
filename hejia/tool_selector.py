import time
import logging
from dotenv import load_dotenv
from openai import OpenAI
import os
from typing import Literal
from pydantic import BaseModel

load_dotenv()

# Tool选择器的系统提示词
TOOL_CLASSIFIER_SYSTEM_PROMPT = """
You are a tool classifier that categorizes user requests into predefined tool categories based on content, context, and intent.
"""

# 定义问题分类器模型
class ToolCategory(BaseModel):
    tool: Literal[
        "DatabaseQueryTool",
        "FileManagementTool",
        "DataVisualizationTool",
        "EmailSendingTool",
        "WebScrapingTool",
        "TranslationTool",
        "SentimentAnalysisTool",
        "TextSummarizationTool",
        "FinancialAnalysisTool",
        "CalendarSchedulingTool"
    ]


class ToolClassifier:
    """
    Classify the appropriate tool for a natural language request.
    """

    def __init__(self):
        oai_api_key = os.getenv('OAI_API_KEY')
        oai_base_url = os.getenv('OAI_BASE_URL')
        self.client_oai = OpenAI(base_url=oai_base_url, api_key=oai_api_key)

    def classify_request(self, request: str) -> str:
        """
        Uses GPT-4 API to classify the appropriate tool for a given request.

        Args:
            request (str): The natural language request to classify.

        Returns:
            str: The action or handler for the chosen tool.
        """
        messages = [
            {"role": "system", "content": TOOL_CLASSIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": request}
        ]

        max_retries = 5
        for attempt in range(max_retries):
            try:
                response_oai = self.client_oai.beta.chat.completions.parse(
                    model="gpt-4o-2024-08-06",
                    messages=messages,
                    response_format=ToolCategory
                )
                selected_tool = response_oai.choices[0].message.parsed
                return selected_tool
            except Exception as e:
                logging.warning(f"Request failed: {e}. Retrying ({attempt + 1}/{max_retries})...")
                time.sleep(0.2 ** attempt)

        raise RuntimeError("Maximum retry attempts reached. Unable to obtain a valid response.")


if __name__ == "__main__":
    tool_classifier = ToolClassifier()
    user_request = "Create a chart to visualize the sales data."
    selected_action = tool_classifier.classify_request(user_request)
    print(selected_action)
