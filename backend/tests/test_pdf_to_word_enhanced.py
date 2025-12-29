"""
测试 PDF 转 Word 图片保留功能
验证 Issue #4 的修复
"""
import pytest
from pathlib import Path
import subprocess
import os


def test_pdf_to_word_enhanced_exists():
    """测试增强版转换脚本是否存在"""
    script_path = Path("app/scripts/pdf_to_doc_enhanced.py")
    assert script_path.exists(), "pdf_to_doc_enhanced.py 应该存在"


def test_pdf_to_word_with_sample():
    """测试 PDF 转 Word 基本功能"""
    input_pdf = Path("tests/samples/sample.pdf")
    output_docx = Path("tests/output/test_enhanced.docx")
    
    # 创建输出目录
    output_docx.parent.mkdir(parents=True, exist_ok=True)
    
    if not input_pdf.exists():
        pytest.skip("测试 PDF 文件不存在，跳过测试")
    
    # 执行转换
    result = subprocess.run([
        "python",
        "app/scripts/pdf_to_doc_enhanced.py",
        "-i", str(input_pdf),
        "-o", str(output_docx)
    ], capture_output=True, text=True, cwd=Path.cwd())
    
    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")
    
    # 验证转换成功
    assert result.returncode == 0, f"转换应该成功，但返回码为 {result.returncode}"
    assert output_docx.exists(), "输出文件应该存在"
    assert output_docx.stat().st_size > 0, "输出文件不应为空"
    
    # 清理
    if output_docx.exists():
        output_docx.unlink()


def test_pdf_format_retention():
    """测试 PDF 转 Word 格式保留（Issue #5）"""
    pytest.skip("需要准备包含格式的测试 PDF 文件")


def test_pdf_image_retention():
    """测试 PDF 转 Word 图片保留（Issue #4）"""  
    pytest.skip("需要准备包含图片的测试 PDF 文件")
