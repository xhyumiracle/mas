import openai
import asyncio
from typing import Dict, Any, List
from mas.tool.base import Toolkit
from openai import OpenAI
from dotenv import load_dotenv
import os
import time

class TextToAudioTool(Toolkit):
    def __init__(self):
        
        super().__init__(
            name="text_to_audio",
            description="文本转语音的工具包",
            tools=[self.generate_audio_by_whisper]
        )
                
        load_dotenv()


    def generate_audio_by_whisper(self, input_msg) -> Dict[str, Any]:
        """
        通过 OpenAI Whisper API 进行文本转语音（TTS）。
        """
        self.client = OpenAI(
            api_key=os.getenv('OAI_API_KEY'),
            base_url=os.getenv('OAI_BASE_URL')
        )

        self.max_retries = 5
        self.model = "tts-1"
        self.voice = "alloy"

        retries = 0
        text_input = input_msg
        output_file = "output.mp3"
        
        while retries < self.max_retries:
            try:
                response = self.client.audio.speech.create(
                    model=self.model,
                    voice=self.voice,
                    input=text_input
                )
                response.stream_to_file(output_file)
                return {"status": "success", "output_msg": output_file, "output_modality": "audio"}
            except Exception as e:
                retries += 1
                print(f"Whisper TTS API call failed (retry {retries}): {e}")
                time.sleep(2 ** retries)

        return {"status": "failed", "output_msg": "Whisper TTS API call failed", "output_modality": "audio"}

text_to_audio_tool = TextToAudioTool()
# 示例用法
if __name__ == "__main__":
    async def main():
        input_msg = "I love Mcdonald's Big Mac, and I want to eat it."
        response = await text_to_audio_tool.generate_audio_by_whisper(input_msg)
        print(response)
    
    asyncio.run(main())