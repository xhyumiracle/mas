from mas.tool.base import Toolkit
from typing import Dict, Any
from moviepy.editor import VideoFileClip

class VideoToImageTool(Toolkit):
    def __init__(self):
        super().__init__(
            name="video_to_image",
            description="视频转图片的工具包",
            tools=[self.extract_frames_from_video]
        )

    def extract_frames_from_video(self, video_path: str):
        '''
        抽取视频中的帧，返回一个list的图片
        '''
        video = VideoFileClip(video_path)
        frames = video.iter_frames()
        return frames

if __name__ == "__main__":
    video_to_image_tool = VideoToImageTool()
