from moviepy.editor import VideoFileClip
from mas.tool.base import Toolkit
from typing import Dict, Any

class VideoToAudioTool(Toolkit):
    def __init__(self):
        super().__init__(
            name="video_to_audio",
            description="直接抽取视频中的音频",
            tools=[self.extract_audio_from_video]
        )

    def extract_audio_from_video(self, video_path: str):
        '''
        抽取视频中的音频
        '''
        audio_path = video_path.replace(".mp4", ".wav")
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        return audio_path

video_to_audio_tool = VideoToAudioTool()
