from typing import List

from mas.memory.filemap import FileMap
from mas.message.types import File
from mas.tool.base import Toolkit


class MockTool(Toolkit):
    def __init__(self):
        super().__init__(
            name="mock",
            description="test only", #  and returns the cleaned text-only content as a dictionary."
            tools=[
                self.mock_text_to_text, 
                self.mock_text_to_image, 
                self.mock_images_to_video, 
                self.mock_text_images_to_audio, 
                self.mock_add_audio_to_video
            ]
        )

    @staticmethod
    def mock_text_to_text(query: str) -> str:
        """test only tool, don't use unless"""
        return "mock result for " + query
    
    @staticmethod
    def mock_text_to_image(text: str, _filemap: FileMap) -> str:
        """mock: generate an image from text"""
        result_file = File(name="result.jpg", mime_type="image/jpeg", content=[])
        result_file2 = File(name="result2.jpg", mime_type="image/jpeg", content=[])
        return [_filemap.add(result_file), _filemap.add(result_file2)]
    
    @staticmethod
    def mock_images_to_video(image_uri_list: List[str], _filemap: FileMap) -> str:
        """mock: generate a video from a list of images"""
        images = [_filemap.get_by_uri(uri) for uri in image_uri_list]
        # do something with images
        result_file = File(name="result.mp4", mime_type="video/mp4", content=[])
        return [_filemap.add(result_file)]
    
    @staticmethod
    def mock_text_images_to_audio(text: str, image_uri_list: List[str], _filemap: FileMap) -> str:
        """mock: generate an audio from a text and a list of images"""
        images = [_filemap.get_by_uri(uri) for uri in image_uri_list]
        # do something with text and images
        result_file = File(name="result.mp3", mime_type="audio/mp3", content=[])
        return [_filemap.add(result_file)]
    
    @staticmethod
    def mock_add_audio_to_video(video_uri: str, audio_uri: str, _filemap: FileMap) -> str:
        """mock: add an audio to a video"""
        video = _filemap.get_by_uri(video_uri)
        audio = _filemap.get_by_uri(audio_uri)
        # do something with video and audio
        result_file = File(name="result_video_with_audio.mp4", mime_type="video/mp4", content=[])
        return [_filemap.add(result_file)]