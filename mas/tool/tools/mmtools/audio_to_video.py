import openai
import asyncio
from typing import Dict, Any, List
from openai import OpenAI
from mas.tool.base import Toolkit
from dotenv import load_dotenv
import os
import time
from .text_to_video import text_to_video_tool
from .audio_to_text import audio_to_text_tool

class AudioToVideoTool(Toolkit):
    def __init__(self):
        
        super().__init__(
            name="audio_to_video",
            description="音频转视频的工具包",
            tools=[self.audio_to_video_by_replicate]
        )
                
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv('OAI_API_KEY'),
            base_url=os.getenv('OAI_BASE_URL')
        )


    def audio_to_video_by_replicate(self, input_audio_file) -> Dict[str, Any]:
        """
        输入音频文件，通过 OpenAI Whisper API 进行语音转文本(STT)，然后通过 replicate 生成视频。
        """
        stt_response = audio_to_text_tool.audio_to_text_by_whisper(input_audio_file)
        replicate_response = text_to_video_tool.generate_video_by_replicate(stt_response["output_msg"])
        return replicate_response

audio_to_video_tool = AudioToVideoTool()
# 示例用法
if __name__ == "__main__":
    input_audio_file = "output.mp3"
    response = audio_to_video_tool.inference(input_audio_file)

