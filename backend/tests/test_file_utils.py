import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
from app.utils.file_utils import (
    format_file_size,
    detect_ext_by_name,
    build_public_url,
    check_dependencies,
)


def test_format_file_size():
    assert format_file_size(512) == "512 B"
    assert format_file_size(2048).endswith("KB")
    assert format_file_size(2 * 1024 * 1024).endswith("MB")


def test_detect_ext_by_name():
    assert detect_ext_by_name("file.DOCX") == ".docx"
    assert detect_ext_by_name("/path/to/audio.mp3") == ".mp3"


def test_build_public_url(settings=__import__("app.config", fromlist=["settings"]).settings):
    base = settings.PUBLIC_BASE_URL.rstrip("/")
    assert build_public_url("/preview/abc.pdf").startswith(base)


# ========== 新增：依赖检查功能测试 ==========


@pytest.mark.asyncio
async def test_check_dependencies_basic():
    """测试基本的依赖检查功能"""
    # 这个测试会执行实际的依赖检查
    try:
        await check_dependencies()
        # 如果没有抛出异常，说明函数执行成功
        assert True
    except Exception as e:
        pytest.fail(f"check_dependencies 抛出异常: {e}")


@pytest.mark.asyncio
async def test_check_dependencies_with_valid_paths():
    """测试有效路径的依赖检查"""
    with patch("app.utils.file_utils.settings") as mock_settings:
        # 模拟有效的工具路径
        mock_settings.SOFFICE_PATH = "soffice"
        mock_settings.FFMPEG_PATH = "ffmpeg"

        with patch("shutil.which") as mock_which:
            mock_which.side_effect = lambda x: (
                f"/usr/bin/{x}" if x in ["soffice", "ffmpeg"] else None
            )

            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = True

                with patch("asyncio.create_subprocess_exec") as mock_subprocess:
                    # 模拟成功的subprocess执行
                    mock_process = AsyncMock()
                    mock_process.returncode = 0
                    mock_process.communicate.return_value = (b"version info\n", b"")
                    mock_subprocess.return_value = mock_process

                    # 执行测试
                    await check_dependencies()

                    # 验证subprocess被调用
                    assert mock_subprocess.called


@pytest.mark.asyncio
async def test_check_dependencies_timeout_handling():
    """测试依赖检查的超时处理"""
    import asyncio

    with patch("app.utils.file_utils.settings") as mock_settings:
        mock_settings.SOFFICE_PATH = "soffice"
        mock_settings.FFMPEG_PATH = "ffmpeg"

        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/soffice"

            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = True

                with patch("asyncio.create_subprocess_exec") as mock_subprocess:
                    # 模拟超时
                    mock_process = AsyncMock()
                    mock_subprocess.return_value = mock_process

                    with patch("asyncio.wait_for") as mock_wait:
                        mock_wait.side_effect = asyncio.TimeoutError()

                        # 应该捕获超时异常并继续执行
                        await check_dependencies()


@pytest.mark.asyncio
async def test_check_dependencies_path_candidates():
    """测试路径候选检查逻辑"""
    with patch("app.utils.file_utils.settings") as mock_settings:
        # 设置初始路径为无效
        mock_settings.SOFFICE_PATH = "invalid_path"
        mock_settings.FFMPEG_PATH = "invalid_path"

        with patch("shutil.which") as mock_which:
            # 为LibreOffice和FFmpeg的所有候选路径提供返回值
            # LibreOffice: SOFFICE_PATH, soffice, soffice.exe, 默认路径
            # FFmpeg: FFMPEG_PATH, ffmpeg, ffmpeg.exe, 默认路径
            mock_which.side_effect = [
                None,  # LibreOffice候选1: soffice
                None,  # LibreOffice候选2: soffice.exe
                None,  # FFmpeg候选1: ffmpeg
                None,  # FFmpeg候选2: ffmpeg.exe
            ]

            with patch("pathlib.Path.exists") as mock_exists:
                # 所有路径都不存在
                mock_exists.return_value = False

                # 应该能够处理所有候选路径都无效的情况
                await check_dependencies()


@pytest.mark.asyncio
async def test_check_dependencies_missing_tools():
    """测试工具缺失的情况"""
    with patch("app.utils.file_utils.settings") as mock_settings:
        mock_settings.SOFFICE_PATH = "soffice"
        mock_settings.FFMPEG_PATH = "ffmpeg"

        with patch("shutil.which") as mock_which:
            # 所有候选路径都返回None
            mock_which.return_value = None

            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = False

                # 应该能处理工具缺失的情况，不抛出异常
                await check_dependencies()


@pytest.mark.asyncio
async def test_check_dependencies_import_checks():
    """测试Python包导入检查 - 验证PIL和fitz导入逻辑"""
    # 只验证函数能正确处理导入检查，不mock整个导入系统
    with patch("shutil.which") as mock_which:
        # 所有工具都找不到
        mock_which.return_value = None

        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False

            # 测试即使工具缺失，函数也能正常执行并检查Python包
            # 如果PIL或fitz缺失，会打印警告但不会崩溃
            try:
                await check_dependencies()
                # 成功执行即通过测试
                assert True
            except ImportError:
                # 如果有ImportError，应该是PIL或fitz等可选依赖，不应该是shutil等标准库
                pytest.fail("check_dependencies不应该因缺少可选依赖而失败")
