from google import genai
from mas.tool.base import Toolkit
from typing import Dict, Any
import time
from IPython.display import Markdown
from google.genai import types

class VideoToTextTool(Toolkit):
    def __init__(self):
        super().__init__(
            name="video_to_text",
            description="视频转文字的工具包",
            tools=[self.understand_video_by_file, self.understand_video_by_youtube_url]
        )

        self.client = genai.Client(api_key="GEMINI_API_KEY")
    
    def check_video_status(self, video_file: str):
        # Check whether the file is ready to be used.
        while video_file.state.name == "PROCESSING":
            print('.', end='')
            time.sleep(1)
            video_file = self.client.files.get(name=video_file.name)

        if video_file.state.name == "FAILED":
            raise False
        else:
            return True
        
    def upload_video(self, video_path: str):
        print("Uploading file...")
        video_file = self.client.files.upload(file=video_path)
        print(f"Completed upload: {video_file.uri}")

        if self.check_video_status(video_file):
            return video_file.uri
        else:
            raise ValueError("Video upload failed")


    def understand_video_by_file(self, video_file: str) -> Dict[str, Any]:
        '''
        通过视频文件 + google gemini 理解视频
        '''
        # Pass the video file reference like any other media part.
        response = self.client.models.generate_content(
            model="gemini-1.5-pro",
            contents=[
                video_file,
                "Summarize this video based on the information in the video."])

        # Print the response, rendering any Markdown
        Markdown(response.text)

        return response

    def understand_video_by_youtube_url(self, video_url: str) -> Dict[str, Any]:
        '''
        通过 youtube url + google gemini 理解视频
        '''
        response = self.client.models.generate_content(
            model='models/gemini-2.0-flash',
            contents=types.Content(
                parts=[
                    types.Part(text='Can you summarize this video?'),
                    types.Part(
                        file_data=types.FileData(file_uri=video_url)
                    )
                ]
            )
        )
        return response

video_to_text_tool = VideoToTextTool()
