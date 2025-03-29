from agno.models.openai import OpenAIChat
from agno.models.message import Message
from agno.media import File
from agno.utils.openai import images_to_message, audio_to_message

from agno.utils.log import logger

from mas.model.pool import ModelPool
from openai import OpenAI

import os, httpx
from pathlib import Path
from typing import Dict, Any, List, Sequence, Union


def file_to_message(files: Sequence[File]) -> List[Dict[str, Any]]:
    """
    Convert a sequence of File objects to OpenAI-compatible message content by uploading files.

    Args:
        files (Sequence[File]): Sequence of File objects to process.
        client (OpenAI): OpenAI client instance for file uploads.

    Returns:
        List[Dict[str, Any]]: List of message content entries with file references.

    Raises:
        ValueError: If file fetching or uploading fails.
    """
    file_messages = []
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    for file in files:
        try:
            # Step 1: Fetch file content and validate
            if file.url:
                content, mime_type = file.file_url_content
                if not content:
                    raise ValueError(f"Failed to fetch content from URL: {file.url}")
                filename = file.url.split('/')[-1]
                logger.info(f"Successfully fetched file from URL: {file.url}")
            elif file.filepath:
                path = Path(file.filepath) if isinstance(file.filepath, str) else file.filepath
                if not (path.exists() and path.is_file()):
                    raise ValueError(f"File path does not exist or is not a file: {path}")
                with open(path, "rb") as f:
                    content = f.read()
                if not content:
                    raise ValueError(f"File is empty: {path}")
                filename = path.name
                logger.info(f"Successfully read file from path: {path}")
            elif file.content:
                if not file.content:
                    raise ValueError("File content is empty")
                content = file.content if isinstance(file.content, bytes) else str(file.content).encode('utf-8')
                filename = "uploaded_file" + (f".{file.mime_type.split('/')[-1]}" if file.mime_type else "")
                logger.info("Using provided file content")
            else:
                logger.warning(f"Skipping file with no url, filepath, or content: {file}")
                continue
# Step 2: Upload to OpenAI and validate response
            file_obj = {"file": (filename, content), "purpose": "user_data"}
            response = client.files.create(**file_obj)
            
            if not hasattr(response, 'id') or not response.id:
                raise ValueError(f"File upload failed, no file_id returned for {filename}")
            file_id = response.id
            logger.info(f"Successfully uploaded file to OpenAI, file_id: {file_id}")

            # Add file reference to message content
            file_messages.append({
                "type": "file",
                "file": {"file_id": file_id}
            })
        except httpx.RequestError as e:
            logger.error(f"Failed to fetch file: {e}")
            raise ValueError(f"Failed to fetch file: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to process or upload file: {e}")
            raise ValueError(f"Failed to process or upload file: {str(e)}")

    return file_messages



@ModelPool.register(name="gpt-4o", description="OpenAI GPT-4O")
class GPT4o(OpenAIChat):
    def __init__(self):
        super().__init__(id="gpt-4o")

    # modified to deal with files
    def _format_message(self, message: Message) -> Dict[str, Any]:
        """
        Format a message into the format expected by OpenAI.

        Args:
            message (Message): The message to format.

        Returns:
            Dict[str, Any]: The formatted message.
        """
        message_dict: Dict[str, Any] = {
            "role": self.role_map[message.role],
            "content": message.content,
            "name": message.name,
            "tool_call_id": message.tool_call_id,
            "tool_calls": message.tool_calls,
        }

        message_dict = {k: v for k, v in message_dict.items() if v is not None}

        # Handle images and audio (existing logic)
        if (message.images is not None and len(message.images) > 0) or (
            message.audio is not None and len(message.audio) > 0) or (
            message.files is not None and len(message.files) > 0
        ):

                if isinstance(message.content, str):
                    message_dict["content"] = [{"type": "text", "text": message.content}]
                elif message.content is None:
                    message_dict["content"] = []
                if message.files is not None:
                    message_dict["content"].extend(file_to_message(message.files))
                if message.images is not None:
                    message_dict["content"].extend(images_to_message(images=message.images))
                if message.audio is not None:
                    message_dict["content"].extend(audio_to_message(audio=message.audio))

        if message.audio_output is not None:
            message_dict["content"] = None
            message_dict["audio"] = {"id": message.audio_output.id}

        if message.videos is not None:
            logger.warning("Video input is currently unsupported.")

        if message.tool_calls is not None and len(message.tool_calls) == 0:
            message_dict["tool_calls"] = None

        if message.content is None and "content" not in message_dict:
            message_dict["content"] = None

        return message_dict



