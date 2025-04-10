import openai
import asyncio
from typing import Dict, Any, List
from mas.tool.base import Toolkit
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import replicate

class ImageToVideoTool(Toolkit):
    def __init__(self):
        
        super().__init__(
            name="image_to_video",
            description="图片转视频的工具包",
            tools=[self.generate_video_by_replicate]
        )
        
        load_dotenv()

  
    def image_to_video_by_replicate(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """
        通过 Replicate 生成视频的工具。
        ref: https://replicate.com/docs/get-started/python
        """
        self.model = "luma/ray"
        input = {
            "prompt": prompt,
            "start_image_url": image_path
        }

        output = replicate.run(
            self.model,
            input=input
        )
        with open("output.mp4", "wb") as file:
            file.write(output.read())
        return output

image_to_video_tool = ImageToVideoTool()

# 示例用法
if __name__ == "__main__":
    image_path = "image.png"
    prompt = "a futuristic cityscape at sunset with flying cars"
    response = image_to_video_tool.image_to_video_by_replicate(image_path, prompt)
    print(response)
    
