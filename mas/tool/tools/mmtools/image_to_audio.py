from .image_to_text import image_to_text_tool
from .text_to_audio import text_to_audio_tool

from mas.tool.base import Toolkit

class ImageToAudioTool(Toolkit):
    def __init__(self):
        super().__init__(
            name="image_to_audio",
            description="图像转音频的工具包",
            tools=[self.inference_by_image_file, self.inference_by_image_url]
        )
            
        self.image_to_text_tool = image_to_text_tool
        self.text_to_audio_tool = text_to_audio_tool

    def inference_by_image_file(self, image_path: str):
        '''
        输入图片路径, 通过 OpenAI GPT4o 理解图像，再使用 OpenAI TTS 生成音频
        '''
        text_response = self.image_to_text_tool.image_to_text_by_file(image_path)
        audio_response = self.text_to_audio_tool.inference(text_response["output_msg"])
        return audio_response

    def inference_by_image_url(self, image_url: str):
        '''
        输入图片url, 通过 OpenAI GPT4o 理解图像，再使用 OpenAI TTS 生成音频
        '''
        text_response = self.image_to_text_tool.image_to_text_by_url(image_url)
        audio_response = self.text_to_audio_tool.inference(text_response["output_msg"])
        return audio_response
    
image_to_audio_tool = ImageToAudioTool()

# 示例用法
if __name__ == "__main__":
    image_path = "image.png"
    response = image_to_audio_tool.inference_by_image_file(image_path)