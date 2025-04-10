from openai import OpenAI
import asyncio
from typing import Dict, Any, List
from mas.tool.base import Toolkit
from dotenv import load_dotenv
import os
import base64
import time

class ImageToTextTool(Toolkit):
    def __init__(self):
        
        super().__init__(
            name="image_to_text",
            description="图片转文字的工具包",
            tools=[self.inference_by_image_file, self.inference_by_image_url]
        )
        
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv('OAI_API_KEY'),
            base_url=os.getenv('OAI_BASE_URL')
        )
        
        self.max_retries = 5
    
    def image_to_text_by_url(self, image_url: str) -> Dict[str, Any]:
        """
        通过 OpenAI GPT4o 理解图像。
        """
        retries = 0
        while retries < self.max_retries:
            try:
                response = self.client.responses.create(
                    model="gpt-4o-mini",
                    input=[{
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "what's in this image?"},
                            {
                                "type": "input_image",
                                "image_url": image_url,
                            },
                        ],
                    }],
                )

                ans = response.output_text
                return {"status": "success", "output_msg": ans, "output_modality": "text"}
            except Exception as e:
                retries += 1
                print(f"OpenAI API call failed (retry {retries}): {e}")
                time.sleep(2 ** retries)
        
        return {"status": "failed", "output_msg": "OpenAI API call failed", "output_modality": "text"}

    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")


    def image_to_text_by_file(self, image_path: str) -> Dict[str, Any]:
        """
        通过 OpenAI GPT4o 理解图像。
        """
        base64_image = self.encode_image(image_path)
        image_url = f"data:image/jpeg;base64,{base64_image}"
        return self.image_to_text_by_url(image_url)

image_to_text_tool = ImageToTextTool()

# 示例用法
if __name__ == "__main__":
    image_path = "image.png"
    response =  image_to_text_tool.image_to_text_by_file(image_path)
    print(response)
