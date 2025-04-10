import openai
import asyncio
from typing import Dict, Any, List
from mas.tool.base import Toolkit
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import replicate

class TextToVideoTool(Toolkit):
    def __init__(self):
        
        super().__init__(
            name="replicate_text_to_video",
            description="文本转视频工具包",
            tools=[self.generate_video_by_replicate]
        )
        
        load_dotenv()

  
    def generate_video_by_replicate(self, prompt: str) -> Dict[str, Any]:
        """
        通过 Replicate 生成视频的工具。
        ref: https://replicate.com/docs/get-started/python
        """
        self.model = "luma/ray"
        output = replicate.run(
            self.model,
            input={"prompt": prompt}
        )
        with open("output.mp4", "wb") as file:
            file.write(output.read())
        return output

text_to_video_tool = TextToVideoTool()

# 示例用法
if __name__ == "__main__":
    prompt = "a futuristic cityscape at sunset with flying cars"
    response = text_to_video_tool.generate_video_by_replicate(prompt)
    print(response)
    
