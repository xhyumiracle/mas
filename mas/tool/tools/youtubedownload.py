from pytubefix import YouTube


class YouTubeDownloader:
    
    @staticmethod
    def download_video(url, output_path=None):
        """Download YouTube video at a given url with the highest resolution to a user specified output path."""
        try:
            yt = YouTube(url)
            video = yt.streams.get_highest_resolution()
            video.download(output_path)
            print(f"Downloaded video: {yt.title}")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    @staticmethod
    def download_audio(url, output_path=None):
        """Downloads the audio-only stream from a YouTube url."""
        try:
            yt = YouTube(url)
            audio = yt.streams.get_audio_only()
            audio.download(output_path)
            print(f"Downloaded audio: {yt.title}")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    @staticmethod
    def check_video(url):
        """Checks if a YouTube video is accessible."""
        try:
            yt = YouTube(url)
            print(f"Video {yt.title} is accessible")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False


from mas.tool.pool import ToolPool

ToolPool.register(
    name="youtube_downloader",
    description="A tool for downloading YouTube videos and audio, and checking video accessibility."
)(YouTubeDownloader())


