import openai
import asyncio
from typing import Dict, Any, List
from openai import OpenAI
from mas.tool.base import Toolkit
from dotenv import load_dotenv
import os
import time

class AudioToTextTool(Toolkit):
    """
    通过 OpenAI Whisper API 进行语音转文本(STT)的 AI 代理。
    """
    def __init__(self):
        
        super().__init__(
            name="whisper_stt",
            description="音频转文字的工具包",
            tools=[self.audio_to_text_by_whisper]
        )
                
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv('OAI_API_KEY'),
            base_url=os.getenv('OAI_BASE_URL')
        )


    def audio_to_text_by_whisper(self, input_audio_file) -> Dict[str, Any]:
        """
        通过 OpenAI Whisper API 进行语音转文本（STT）。
        """
        retries = 0
        audio_file= open(input_audio_file, "rb")
        
        while retries < self.max_retries:
            try:
                transcription = self.client.audio.transcriptions.create(
                    model="gpt-4o-transcribe", 
                    file=audio_file
                )
                output_msg = transcription.text
                return {"status": "success", "output_msg": output_msg, "output_modality": "text"}
            except Exception as e:
                retries += 1
                print(f"Whisper TTS API call failed (retry {retries}): {e}")
                time.sleep(2 ** retries)

        return {"status": "failed", "output_msg": "Whisper STT API call failed", "output_modality": "text"}

audio_to_text_tool = AudioToTextTool()
# 示例用法
if __name__ == "__main__":
    input_audio_file = "output.mp3"
    response = audio_to_text_tool.audio_to_text_by_whisper(input_audio_file)
    print(response)

