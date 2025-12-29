"""Word 转 HTML 转换脚本的单元测试."""

import os

import tempfile

from docx import Document

from app.scripts.doc_to_html import docx_to_html


def test_simple_paragraph():
    """测试简单段落转换是否成功."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "test.docx")
        output_path = os.path.join(tmpdir, "test.html")

        doc = Document()
        doc.add_paragraph("Hello World")
        doc.save(input_path)

        result = docx_to_html(input_path, output_path)

        assert result is True
        assert os.path.exists(output_path)


def test_file_not_found():
    """测试当输入文件不存在时的行为."""
    result = docx_to_html("not_exist.docx", "output.html")
    assert result is False
