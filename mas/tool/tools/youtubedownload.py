from pytubefix import YouTube
from mas.tool.base import Toolkit

class YouTubeDownloadTool(Toolkit):
    def __init__(self):
        super().__init__(
            name="youtube_download",
            description="A tool for downloading YouTube videos and audio, and checking video accessibility.", # this is for orchestrator to see
            tools=[self.youtube_download_video, self.youtube_download_audio, self.youtube_check_video]
        )
    
    @staticmethod
    def youtube_download_video(url, output_path=None):
        # this is for LLM to see
        """Download YouTube video at a given url with the highest resolution to a user specified output path."""
        try:
            yt = YouTube(url)
            video = yt.streams.get_highest_resolution()
            video.download(output_path)
            print(f"Downloaded video: {yt.title}")
        except Exception as e:
            print(f"An error occurred: {e}")

    @staticmethod
    def youtube_download_audio(url, output_path=None):
        """Downloads the audio-only stream from a YouTube url."""
        try:
            yt = YouTube(url)
            audio = yt.streams.get_audio_only()
            audio.download(output_path)
            print(f"Downloaded audio: {yt.title}")
        except Exception as e:
            print(f"An error occurred: {e}")

    @staticmethod
    def youtube_check_video(url):
        """Checks if a YouTube video is accessible."""
        try:
            yt = YouTube(url)
            print(f"Video {yt.title} is accessible")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

