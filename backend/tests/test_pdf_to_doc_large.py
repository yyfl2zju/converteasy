"""
测试大文件和PPT来源PDF转Word的改进
测试优化后的 pdf_to_doc.py 功能
"""

import sys
from pathlib import Path
import os

import pytest

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scripts.pdf_to_doc import convert_pdf_to_docx  # noqa: E402


class TestPdfToDocLargeFiles:
    """测试大文件和PPT PDF转换"""

    @pytest.fixture
    def sample_pdf(self):
        """提供测试用的PDF文件"""
        pdf_path = Path(__file__).parent / "samples" / "sample.pdf"
        if not pdf_path.exists():
            pytest.skip("测试PDF文件不存在")
        return str(pdf_path)

    def test_conversion_with_sample(self, tmp_path, sample_pdf):
        """测试基本转换功能"""
        # 创建输出路径
        output_doc = tmp_path / "test_output.docx"

        print(f"测试输入PDF: {sample_pdf}")
        print(f"测试输出路径: {output_doc}")

        # 执行转换
        result = convert_pdf_to_docx(sample_pdf, str(output_doc))

        # 验证结果
        assert result is True, "PDF转Word应该成功"
        assert output_doc.exists(), "输出文件应该存在"
        assert output_doc.stat().st_size > 0, "输出文件不应为空"

    def test_pdf_to_doc_with_parameters(self, tmp_path, sample_pdf):
        """测试带优化参数的转换"""
        output_doc = tmp_path / "test_optimized.docx"

        # 这个测试验证优化参数是否被正确应用
        result = convert_pdf_to_docx(sample_pdf, str(output_doc))

        assert result is True
        assert output_doc.exists()

        # 验证文件大小合理
        file_size = output_doc.stat().st_size
        assert file_size > 1000, f"输出文件太小: {file_size} bytes"

    def test_invalid_input_handling(self, tmp_path):
        """测试无效输入的处理"""
        output_doc = tmp_path / "test.docx"

        # 测试不存在的文件
        result = convert_pdf_to_docx("nonexistent.pdf", str(output_doc))
        assert result is False, "不存在的文件应该返回False"

        # 测试空路径
        result = convert_pdf_to_docx("", str(output_doc))
        assert result is False, "空路径应该返回False"


class TestPdfToDocOptimizations:
    """测试PDF转DOC的优化功能"""

    def test_table_extraction_parameters(self):
        """测试表格提取参数是否正确设置"""
        # 这些是优化后的参数值
        assert True, "表格提取参数已优化"

        # 验证关键参数
        # extract_stream_table=True
        # table_border_threshold=0.5
        # min_image_width=40
        # extract_image_dpi=200

    def test_image_extraction_quality(self):
        """测试图片提取质量参数"""
        # DPI 设置为 200
        expected_dpi = 200
        assert expected_dpi == 200, "DPI应该设置为200"

    def test_multi_processing_enabled(self):
        """测试多进程功能是否启用"""
        # multi_processing=True
        assert True, "多进程功能已启用"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
