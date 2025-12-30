"""
PDF转PPT功能单元测试
测试 app/scripts/pdf_to_ppt.py 的核心功能
"""

import os
import sys
import pytest
import zipfile
from pathlib import Path
from PIL import Image

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scripts.pdf_to_ppt import (
    _check_poppler,
    pdf_to_images,
    create_ppt_from_images,
    pdf_to_ppt,
)


class TestPopplerDetection:
    """测试Poppler检测功能"""

    def test_poppler_detection(self):
        """测试Poppler是否可用"""
        result = _check_poppler()
        # 应该返回True或False
        assert isinstance(result, bool)


class TestPdfToImages:
    """测试PDF转图片功能"""

    @pytest.fixture
    def sample_pdf(self):
        """提供测试用的PDF文件"""
        pdf_path = Path(__file__).parent / "samples" / "sample.pdf"
        if not pdf_path.exists():
            pytest.skip("测试PDF文件不存在")
        return str(pdf_path)

    def test_pdf_to_images_basic(self, sample_pdf):
        """测试PDF转图片功能"""
        if not _check_poppler():
            pytest.skip("Poppler未安装")

        images = pdf_to_images(sample_pdf, dpi=150)

        # 验证结果
        assert isinstance(images, list), "应该返回图片列表"
        assert len(images) > 0, "至少应该有一张图片"

        # 验证第一张图片
        first_image = images[0]
        assert isinstance(first_image, Image.Image), "应该是PIL Image对象"
        assert first_image.width > 0, "图片宽度应该大于0"
        assert first_image.height > 0, "图片高度应该大于0"


class TestCreatePptFromImages:
    """测试从图片创建PPT功能"""

    @pytest.fixture
    def sample_images(self):
        """创建测试用的图片"""
        # 创建一个简单的测试图片
        img = Image.new("RGB", (800, 600), color="white")
        return [img]

    @pytest.fixture
    def output_pptx(self, tmp_path):
        """提供输出PPTX文件路径"""
        return str(tmp_path / "test_output.pptx")

    def test_create_ppt_basic(self, sample_images, output_pptx):
        """测试从图片创建PPT的基本功能"""
        result = create_ppt_from_images(sample_images, output_pptx)

        # 验证返回值
        assert result is True, "应该返回True表示成功"

        # 验证输出文件
        assert os.path.exists(output_pptx), "输出文件应该存在"
        assert os.path.getsize(output_pptx) > 0, "输出文件不应为空"

        # 验证PPTX结构
        assert zipfile.is_zipfile(output_pptx), "PPTX应该是有效的ZIP文件"

    def test_create_ppt_with_custom_size(self, sample_images, output_pptx):
        """测试使用自定义幻灯片尺寸"""
        result = create_ppt_from_images(
            sample_images, output_pptx, slide_width=10, slide_height=7.5
        )

        assert result is True
        assert os.path.exists(output_pptx)


class TestPdfToPptIntegration:
    """测试PDF到PPT的完整流程"""

    @pytest.fixture
    def sample_pdf(self):
        """提供测试用的PDF文件"""
        pdf_path = Path(__file__).parent / "samples" / "sample.pdf"
        if not pdf_path.exists():
            pytest.skip("测试PDF文件不存在")
        return str(pdf_path)

    @pytest.fixture
    def output_pptx(self, tmp_path):
        """提供输出PPTX文件路径"""
        return str(tmp_path / "test_output.pptx")

    def test_pdf_to_ppt_full_workflow(self, sample_pdf, output_pptx):
        """测试完整的PDF转PPT工作流"""
        if not _check_poppler():
            pytest.skip("Poppler未安装")

        result = pdf_to_ppt(sample_pdf, output_pptx, dpi=150)

        # 验证返回值
        assert result is True, "转换应该成功"

        # 验证输出文件
        assert os.path.exists(output_pptx), "输出文件应该存在"
        assert os.path.getsize(output_pptx) > 0, "输出文件不应为空"

        # 验证PPTX结构
        assert zipfile.is_zipfile(output_pptx), "PPTX应该是有效的ZIP文件"

        with zipfile.ZipFile(output_pptx, "r") as zip_ref:
            namelist = zip_ref.namelist()
            # 检查必需的文件
            assert "ppt/presentation.xml" in namelist, "应包含presentation.xml"
            assert any("ppt/slides/slide" in name for name in namelist), "应包含幻灯片"

    def test_pdf_to_ppt_with_invalid_input(self, output_pptx):
        """测试无效输入的处理"""
        result = pdf_to_ppt("nonexistent.pdf", output_pptx)
        assert result is False, "不存在的文件应该返回False"

    def test_pdf_to_ppt_with_custom_dpi(self, sample_pdf, output_pptx):
        """测试使用自定义DPI"""
        if not _check_poppler():
            pytest.skip("Poppler未安装")

        result = pdf_to_ppt(sample_pdf, output_pptx, dpi=100)
        assert result is True
        assert os.path.exists(output_pptx)


class TestErrorHandling:
    """测试错误处理"""

    def test_invalid_pdf_path(self, tmp_path):
        """测试无效的PDF路径"""
        output_pptx = str(tmp_path / "output.pptx")
        result = pdf_to_ppt("", output_pptx)
        assert result is False

    def test_invalid_output_path(self):
        """测试无效的输出路径"""
        result = pdf_to_ppt("sample.pdf", "")
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
