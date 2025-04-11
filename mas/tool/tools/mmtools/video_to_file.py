from typing import Dict, Any
from mas.tool.base import Toolkit
from mas.utils.path_sanitizer import PathSanitizer

class VideoToFileTool(Toolkit):
    """Tool for saving video data to files."""
    
    # 允许的视频文件扩展名
    ALLOWED_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv'}
    
    def __init__(self):
        super().__init__(
            name="video_to_file",
            description="将视频数据保存到文件的工具",
            tools=[self.video_bytes_to_file]
        )
        # 确保沙箱目录存在
        PathSanitizer.ensure_sandbox_exists()
    
    @classmethod
    def video_bytes_to_file(cls, video: bytes, file_path: str) -> str:
        """
        将视频数据安全地存储到本地文件。
        
        Args:
            video: 视频数据（字节）
            file_path: 建议的文件路径（将被安全处理）
            
        Returns:
            实际保存的文件路径
            
        Raises:
            ValueError: 如果文件路径不安全或扩展名不被允许
        """
        # 使用安全路径处理器
        safe_path = PathSanitizer.sanitize_path(
            file_path,
            allowed_extensions=cls.ALLOWED_EXTENSIONS
        )
        
        # 写入文件
        with open(safe_path, "wb") as f:
            f.write(video)
            
        return str(safe_path)