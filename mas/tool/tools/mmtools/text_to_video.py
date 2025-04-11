from typing import Dict, Any
from mas.tool.base import Toolkit
from dotenv import load_dotenv
from mas.tool.tools.mmtools.video_to_file import VideoToFileTool
import replicate

class TextToVideoTool(Toolkit):
    def __init__(self):
        
        super().__init__(
            name="replicate_text_to_video",
            description="文本转视频工具包",
            tools=[self.generate_video_by_replicate]
        )
        
        load_dotenv()

  
    @classmethod
    def generate_video_by_replicate(cls, prompt: str, file_path: str) -> Dict[str, Any]:
        """
        通过 Replicate 生成视频的工具。
        ref: https://replicate.com/docs/get-started/python
        """
        model = "luma/ray"
        output = replicate.run(
            model,
            input={"prompt": prompt}
        )
        try:
            VideoToFileTool.video_bytes_to_file(output.read(), file_path)
        except Exception as e:
            return {"status": "failed", "output_msg": str(e), "output_modality": "video"}
        # with open("output.mp4", "wb") as file:
        #     file.write(output.read())
        # return output
        return {"status": "success", "output_msg": file_path, "output_modality": "video"}

text_to_video_tool = TextToVideoTool()

# 示例用法
if __name__ == "__main__":
    prompt = "a futuristic cityscape at sunset with flying cars"
    response = text_to_video_tool.generate_video_by_replicate(prompt)
    print(response)
    
