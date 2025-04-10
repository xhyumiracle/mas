from agno.models.google import Gemini
from agno.media import Audio, Image, File, Video
from agno.utils.log import logger
from agno.models.message import Message

from mas.model.pool import ModelPool

from google import genai
from google.genai.types import Part
from google.genai.types import File as GeminiFile

from typing import Any, Dict, List, Optional, Sequence, Union
from pathlib import Path
import os, mimetypes, requests, json
from urllib.parse import urlparse



valid_mime_types = {
    "audio/wav", "audio/mp3", "audio/aiff", 
    "audio/aac", "audio/ogg", "audio/flac"
}
valid_extensions = {".wav", ".mp3", ".aiff", ".aac", ".ogg", ".flac"}

#client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))


def upload_audio_url(url: str, client) -> GeminiFile:
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        # Check content type from headers or file extension
        content_type = response.headers.get('Content-Type', '')
        ext = os.path.splitext(urlparse(url).path)[1].lower()

        if content_type not in valid_mime_types and ext not in valid_extensions:
            raise ValueError(f"Invalid audio format. File must have one of these MIME types: {valid_mime_types} or extensions: {valid_extensions}")
        
        # Ensure content_type is valid
        elif content_type in valid_mime_types:
            # Determine file extension : ext = content_type - "audio/"
            ext = f".{content_type.split('/')[1]}"
        
        temp_filepath = f"temp_audio_file{ext}"
        print(temp_filepath)
        # Write file in chunks
        with open(temp_filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192): # write in chunks to save memory
                f.write(chunk)

        uploaded_file = client.files.upload(file=temp_filepath)
        os.remove(temp_filepath)  # Cleanup temp file
        return uploaded_file
    
    else:
        raise ValueError("Failed to download the file from URL. Check that the URL is valid.")

    
def upload_audio_filepath(path: str, client) -> GeminiFile:
    mime_type, _ = mimetypes.guess_type(path)
    file_ext = os.path.splitext(path)[1].lower()

    if mime_type not in valid_mime_types and file_ext not in valid_extensions:
        raise ValueError(f"Invalid audio format. File must have one of these MIME types: {valid_mime_types} or extensions: {valid_extensions}")
    
    print(f"Successfully uploaded audio file: {path}")
    return client.files.upload(file=path)

            

# @ModelPool.register(name="gemini", description="Gemini")
class GeminiModel(Gemini):
    def __init__(self, id="gemini-1.5-flash"):
        super().__init__(id=id)

    def _format_video_for_message(self, video: Video) -> Optional[GeminiFile]:
        # Case 1: Video is a bytes object
        if video.content and isinstance(video.content, bytes):
            return Part.from_bytes(
                mime_type=f"video/{video.format}" if video.format else "video/mp4", data=video.content
            )
        # Case 2: Video is stored locally
        elif video.filepath is not None:
            video_path = video.filepath if isinstance(video.filepath, Path) else Path(video.filepath)

            remote_file_name = f"files/{video_path.stem.lower().replace(' ', '-')}"
            # Check if video is already uploaded
            existing_video_upload = None
            try:
                existing_video_upload = self.get_client().files.get(name=remote_file_name)
            except Exception as e:
                pass

            if existing_video_upload:
                video_file = existing_video_upload
            else:
                # Upload the video file to the Gemini API
                if video_path.exists() and video_path.is_file():
                    video_file = self.get_client().files.upload(
                        file=video_path,
                        config=dict(
                            name=remote_file_name,
                            display_name=video_path.stem,
                            mime_type=f"video/{video.format}" if video.format else "video/mp4",
                        ),
                    )
                else:
                    logger.error(f"Video file {video_path} does not exist.")
                    raise Exception(f"Video file {video_path} does not exist.")

                # Check whether the file is ready to be used.
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = self.get_client().files.get(name=video_file.name)

                if video_file.state.name == "FAILED":
                    raise ValueError(video_file.state.name)

            return Part.from_uri(
                file_uri=video_file.uri, mime_type=f"video/{video.format}" if video.format else "video/mp4"
            )
        else:
            logger.warning(f"Unknown video type: {type(video.content)}")
            return None

    def _format_messages(self, messages: List[Message]):
        """
        Converts a list of Message objects to the Gemini-compatible format.

        Args:
            messages (List[Message]): The list of messages to convert.
        """
        formatted_messages: List = []
        system_message = None
        for message in messages:
            role = message.role
            if role in ["system", "developer"]:
                system_message = message.content
                continue

            role = "model" if role == "assistant" else role

            # Add content to the message for the model
            content = message.content
            # Initialize message_parts to be used for Gemini
            message_parts: List[Any] = []

            # Function calls
            if (not content or role == "model") and message.tool_call:
                tool_call = message.tool_call
                content = {
                    "role": "function",
                    "name": tool_call.name,
                    "content": json.dumps(tool_call.arguments)
                }
            elif role == "tool" and message.tool_result:
                tool_result = message.tool_result
                content = {
                    "role": "function",
                    "name": tool_result.name,
                    "content": tool_result.content
                }
            elif isinstance(content, str):
                message_parts = [content]
            '''
            else
                if isinstance(content, str):
                    message_parts = [Part.from_text(text=content)]
            '''

            if message.role == "user":
                # Add images to the message for the model
                if message.images is not None:
                    for image in message.images:
                        if image.content is not None and isinstance(image.content, GeminiFile):
                            # Google recommends that if using a single image, place the text prompt after the image.
                            message_parts.insert(0, image.content)
                        else:
                            image_content = self._format_image_for_message(image)
                            if image_content:
                                message_parts.append(Part.from_bytes(**image_content))

                # Add videos to the message for the model
                if message.videos is not None:
                    try:
                        for video in message.videos:
                            # Case 1: Video is a file_types.File object (Recommended)
                            # Add it as a File object
                            if video.content is not None and isinstance(video.content, GeminiFile):
                                # Google recommends that if using a single image, place the text prompt after the image.
                                message_parts.insert(
                                    0, Part.from_uri(file_uri=video.content.uri, mime_type=video.content.mime_type)
                                )
                            else:
                                video_file = self._format_video_for_message(video)

                                # Google recommends that if using a single video, place the text prompt after the video.
                                if video_file is not None:
                                    message_parts.insert(0, video_file)  # type: ignore
                    except Exception as e:
                        logger.warning(f"Failed to load video from {message.videos}: {e}")
                        continue

                # Add audio to the message for the model
                if message.audio is not None:
                    try:
                        for audio in message.audio: # GeminiFile: a file uploaded to the API
                            if audio.url is not None:
                                file = upload_audio_url(audio.url, self.get_client())
                            elif audio.filepath is not None:
                                file = upload_audio_filepath(audio.filepath, self.get_client())
                            elif audio.content is not None: # it's in byte64
                                file = Part.from_bytes(data=audio.content, mime_type='audio/mp3')
                            message_parts.append(file)
                            
                    except Exception as e:
                        logger.warning(f"Failed to load audio from {message.audio}: {e}")
                        continue

                # Add files to the message for the model
                if message.files is not None:
                    for file in message.files:
                        file_content = self._format_file_for_message(file)
                        if file_content:
                            message_parts.append(file_content)

        return message_parts, system_message
    
    