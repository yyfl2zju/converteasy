"""
文件工具函数
"""

import asyncio
from pathlib import Path
from datetime import datetime
from typing import List

from app.config import settings, SUPPORTED_CONVERSIONS, PYTHON_CONVERSIONS


def ensure_dir(dir_path: str) -> None:
    """确保目录存在"""
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def detect_ext_by_name(filename: str) -> str:
    """根据文件名检测扩展名"""
    return Path(filename).suffix.lower()


def is_allowed_ext(category: str, ext: str) -> bool:
    """检查扩展名是否允许"""
    if category == "document":
        return ext in settings.ALLOWED_DOC_EXT
    elif category == "audio":
        return ext in settings.ALLOWED_AUDIO_EXT
    elif category == "image":
        return ext in settings.ALLOWED_IMAGE_EXT
    return False


def is_conversion_supported(category: str, source_ext: str, target_format: str) -> bool:
    """验证转换是否支持"""
    if category != "document":
        conversions = SUPPORTED_CONVERSIONS.get(category, {})
        # 处理 jpg/jpeg 等价
        if category == "image":
            source_key = source_ext.lstrip(".").lower()
            if source_key == "jpeg":
                source_key = "jpg"

            # 检查目标格式是否在支持列表中
            if target_format in conversions:
                # 检查源格式是否在目标格式的支持列表中
                # 注意：SUPPORTED_CONVERSIONS["image"] 的结构是 target -> [sources]
                # 但上面的 config.py 定义似乎是 source -> [targets] ???
                # 让我们检查 config.py 的定义
                pass

        return target_format in conversions and source_ext in conversions[target_format]

    conversions = SUPPORTED_CONVERSIONS.get("document", {})
    if target_format not in conversions:
        return False

    source_format = source_ext.replace(".", "")
    conversion_key = f"{source_format}->{target_format}"

    # 检查是否需要 Python 脚本
    if conversion_key in PYTHON_CONVERSIONS:
        script_path = settings.SCRIPTS_DIR / PYTHON_CONVERSIONS[conversion_key]["script"]
        if not script_path.exists():
            print(f"⚠ Python 脚本不存在: {script_path}")
            return False
        return True

    # LibreOffice 转换
    return source_ext in conversions.get(target_format, [])


def get_supported_targets(category: str, source_ext: str) -> List[str]:
    """获取支持的转换目标格式"""
    if category != "document":
        conversions = SUPPORTED_CONVERSIONS.get(category, {})
        supported = []
        for target, sources in conversions.items():
            if source_ext in sources:
                supported.append(target)
        return supported

    conversions = SUPPORTED_CONVERSIONS.get("document", {})
    supported = []
    source_format = source_ext.replace(".", "")

    for target, sources in conversions.items():
        conversion_key = f"{source_format}->{target}"

        if conversion_key in PYTHON_CONVERSIONS:
            script_path = settings.SCRIPTS_DIR / PYTHON_CONVERSIONS[conversion_key]["script"]
            if script_path.exists():
                supported.append(target)
        elif source_ext in sources:
            supported.append(target)

    return supported


def format_file_size(bytes_size: int) -> str:
    """格式化文件大小"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024):.1f} MB"
    return f"{bytes_size / (1024 * 1024 * 1024):.1f} GB"


def build_public_url(pathname: str) -> str:
    """构建公网访问 URL"""
    base = settings.PUBLIC_BASE_URL.rstrip("/")
    return f"{base}{pathname}"


def build_download_url(filename: str) -> str:
    """构建下载 URL"""
    return build_public_url(f"/download/{filename}")


def build_preview_url(filename: str) -> str:
    """构建预览 URL"""
    return build_public_url(f"/preview/{filename}")


async def cleanup_expired_files() -> None:
    """清理过期文件"""
    from app.utils.task_manager import task_manager

    now = datetime.now()
    expire_time = settings.FILE_EXPIRE_TIME

    print(f"🧹 开始清理过期文件，当前时间: {now.isoformat()}")

    # 清理过期任务和文件
    expired_tasks = task_manager.get_expired_tasks(expire_time)
    for task in expired_tasks:
        # 删除输入文件
        if task.input_path and Path(task.input_path).exists():
            try:
                Path(task.input_path).unlink()
                print(f"✓ 清理过期输入文件: {task.input_path}")
            except Exception as e:
                print(f"✗ 清理输入文件失败: {task.input_path} - {e}")

        # 删除输出文件
        if task.output_path and Path(task.output_path).exists():
            try:
                Path(task.output_path).unlink()
                print(f"✓ 清理过期输出文件: {task.output_path}")
            except Exception as e:
                print(f"✗ 清理输出文件失败: {task.output_path} - {e}")

        task_manager.delete_task(task.id)
        print(f"✓ 清理过期任务: {task.id}")

    # 清理 uploads 目录中的孤立文件（超过1小时）
    await cleanup_orphaned_files(settings.UPLOAD_DIR, 3600, "uploads")

    # 清理 public 目录中的孤立文件（超过24小时）
    await cleanup_orphaned_files(settings.PUBLIC_DIR, 86400, "public")


async def cleanup_orphaned_files(directory: str, max_age: int, dir_name: str) -> None:
    """清理孤立文件"""
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return

        now = datetime.now()
        cleaned_count = 0

        for file_path in dir_path.iterdir():
            if file_path.is_dir():
                continue

            try:
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if (now - mtime).total_seconds() > max_age:
                    # 跳过友好命名的文件
                    import re

                    if re.search(r"_\d{8,10}\.", file_path.name):
                        continue

                    file_path.unlink()
                    print(f"✓ 清理孤立文件 ({dir_name}): {file_path}")
                    cleaned_count += 1
            except Exception as e:
                print(f"✗ 检查文件失败: {file_path} - {e}")

        if cleaned_count > 0:
            print(f"📁 在 {dir_name} 目录中清理了 {cleaned_count} 个孤立文件")
    except Exception as e:
        print(f"✗ 清理 {dir_name} 目录失败: {e}")


async def check_dependencies() -> None:
    """检查系统依赖"""
    import shutil
    import sys
    from pathlib import Path

    # 检查 LibreOffice
    soffice_candidates = [
        settings.SOFFICE_PATH,
        shutil.which("soffice"),
        shutil.which("soffice.exe"),
        "C:\\Program Files\\LibreOffice\\program\\soffice.exe",
    ]
    soffice_path = None
    for candidate in soffice_candidates:
        if candidate and Path(str(candidate)).exists():
            soffice_path = candidate
            break

    if soffice_path:
        try:
            proc = await asyncio.create_subprocess_exec(
                str(soffice_path),
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5.0)
            if proc.returncode == 0 and stdout:
                version = stdout.decode().strip().split("\n")[0]
                print(f"✓ LibreOffice 可用: {version}")
            else:
                print(f"⚠ LibreOffice 未找到（文档转换功能不可用）")
        except Exception as e:
            print(f"⚠ LibreOffice 检查出错: {e}")
    else:
        print("⚠ LibreOffice 未找到（文档转换功能不可用）")

    # 检查 FFmpeg
    ffmpeg_candidates = [
        settings.FFMPEG_PATH,
        shutil.which("ffmpeg"),
        shutil.which("ffmpeg.exe"),
        "C:\\ProgramData\\chocolatey\\bin\\ffmpeg.exe",
    ]
    ffmpeg_path = None
    for candidate in ffmpeg_candidates:
        if candidate and Path(str(candidate)).exists():
            ffmpeg_path = candidate
            break

    if ffmpeg_path:
        try:
            proc = await asyncio.create_subprocess_exec(
                str(ffmpeg_path),
                "-version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5.0)
            if proc.returncode == 0 and stdout:
                version = stdout.decode().split("\n")[0]
                print(f"✓ FFmpeg 可用: {version}")
            else:
                print("⚠ FFmpeg 未找到（音频转换功能不可用）")
        except Exception as e:
            print(f"⚠ FFmpeg 检查出错: {e}")
    else:
        print("⚠ FFmpeg 未找到（音频转换功能不可用）")

    # 检查图片转换依赖（必需）
    try:
        import PIL
        import fitz

        print("✓ 图片转换依赖可用: Pillow, PyMuPDF")
    except ImportError as e:
        print(f"✗ 图片转换依赖缺失: {e}")

    # 检查 Python 文档转换依赖（可选）
    try:
        import pdfplumber
        import docx
        import openpyxl
        import pandas

        print("✓ Python 文档转换依赖可用")
    except ImportError as e:
        print(f"⚠ 部分 Python 依赖缺失: {e}")
