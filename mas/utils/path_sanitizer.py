import os
import re
from pathlib import Path
from typing import Optional
import platform

class PathSanitizer:
    """Secure path sanitizer for handling file paths from untrusted sources."""
    
    # 定义安全的基本目录（沙箱）
    SANDBOX_DIR = Path("sandbox")
    
    # 定义非法字符模式
    ILLEGAL_CHARS = {
        'windows': r'[<>:"/\\|?*\x00-\x1f]',
        'posix': r'[/\x00]',
    }
    
    # 定义保留文件名（在不同操作系统上）
    RESERVED_NAMES = {
        'windows': {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        },
        'posix': set()
    }
    
    @classmethod
    def sanitize_path(cls, unsafe_path: str, allowed_extensions: Optional[set] = None) -> Path:
        """
        Sanitize a file path to ensure it's safe to use.
        
        Args:
            unsafe_path: The potentially unsafe path from untrusted source
            allowed_extensions: Set of allowed file extensions (e.g., {'.jpg', '.png'})
            
        Returns:
            A sanitized Path object within the sandbox directory
            
        Raises:
            ValueError: If the path is fundamentally unsafe or invalid
        """
        # 1. 转换为Path对象并规范化路径
        path = Path(unsafe_path)
        
        # 2. 检查是否尝试访问沙箱外的路径
        try:
            # 解析所有符号链接和相对路径
            resolved = path.resolve()
            # 确保路径在沙箱内
            if not str(resolved).startswith(str(cls.SANDBOX_DIR.resolve())):
                raise ValueError("Path attempts to access outside sandbox")
        except Exception as e:
            raise ValueError(f"Invalid path: {e}")
        
        # 3. 获取操作系统特定的非法字符模式
        system = 'windows' if platform.system() == 'Windows' else 'posix'
        illegal_pattern = cls.ILLEGAL_CHARS[system]
        
        # 4. 处理文件名部分
        filename = path.name
        # 移除非法字符
        safe_name = re.sub(illegal_pattern, '_', filename)
        # 确保文件名不为空
        if not safe_name:
            safe_name = 'unnamed_file'
        
        # 5. 检查保留文件名
        if system == 'windows':
            name_without_ext = safe_name.rsplit('.', 1)[0].upper()
            if name_without_ext in cls.RESERVED_NAMES['windows']:
                safe_name = f"_{safe_name}"
        
        # 6. 检查文件扩展名
        if allowed_extensions:
            ext = Path(safe_name).suffix.lower()
            if ext and ext not in allowed_extensions:
                raise ValueError(f"File extension {ext} not allowed")
        
        # 7. 限制文件名长度
        # Windows: 260 chars total, POSIX: 255 chars per component
        max_length = 255 if system == 'posix' else 260
        if len(safe_name) > max_length:
            name, ext = os.path.splitext(safe_name)
            safe_name = name[:max_length - len(ext)] + ext
        
        # 8. 构建最终的安全路径
        safe_path = cls.SANDBOX_DIR / safe_name
        
        return safe_path
    
    @classmethod
    def ensure_sandbox_exists(cls) -> None:
        """Ensure the sandbox directory exists."""
        cls.SANDBOX_DIR.mkdir(parents=True, exist_ok=True) 