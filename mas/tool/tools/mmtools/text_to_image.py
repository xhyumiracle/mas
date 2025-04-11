import openai
import asyncio
from typing import Dict, Any, List, Optional
from mas.tool.base import Toolkit
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

class TextToImageTool(Toolkit):
    def __init__(self):
        
        super().__init__(
            name="text_to_image",
            description="文本转图片的工具包",
            tools=[self.generate_image_by_dalle]
        )
        load_dotenv()
    
    async def generate_image_by_dalle(self, prompt: str) -> Dict[str, Any]:
        """
        通过 OpenAI DALL·E API 生成图像。
        """
        client = AsyncOpenAI(
            api_key=os.getenv('OAI_API_KEY'),
            base_url=os.getenv('OAI_BASE_URL')
        )
        
        max_retries = 5
        base_model = "dall-e-3"
        image_size = "1024x1024"
        image_quality = "standard"
        num_images = 1

        retries = 0
        while retries < max_retries:
            try:
                response = await client.images.generate(
                    model=base_model,
                    prompt=prompt,
                    size=image_size,
                    quality=image_quality,
                    n=num_images
                )
                image_url = response.data[0].url
                return {"status": "success", "output_msg": image_url, "output_modality": "image"}
            except Exception as e:
                retries += 1
                print(f"{base_model} OpenAI API call failed (retry {retries}): {e}")
                await asyncio.sleep(2 ** retries)
        
        return {"status": "failed", "output_msg": "OpenAI API call failed", "output_modality": "image"}

text_to_image_tool = TextToImageTool()

# 示例用法
if __name__ == "__main__":
    async def main():
        prompt = "a futuristic cityscape at sunset with flying cars"
        response = await text_to_image_tool.generate_image_by_dalle(prompt)
        print(response)
    
    asyncio.run(main())