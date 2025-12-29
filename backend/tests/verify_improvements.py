#!/usr/bin/env python3
"""
快速验证PDF转Word改进的脚本
用于测试新功能是否正常工作
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """测试所有必要的导入"""
    print("=" * 60)
    print("测试 1: 检查依赖包")
    print("=" * 60)

    try:
        from pdfminer.high_level import extract_text  # noqa: F401

        print("✅ pdfminer.six - 已安装")
    except ImportError as e:
        print(f"❌ pdfminer.six - 未安装: {e}")

    try:
        from docx import Document  # noqa: F401

        print("✅ python-docx - 已安装")
    except ImportError as e:
        print(f"❌ python-docx - 未安装: {e}")

    try:
        import fitz

        print(f"✅ PyMuPDF - 已安装 (版本: {fitz.version})")
    except ImportError as e:
        print(f"❌ PyMuPDF - 未安装: {e}")

    try:
        import pdfplumber  # noqa: F401

        print("✅ pdfplumber - 已安装")
    except ImportError as e:
        print(f"❌ pdfplumber - 未安装: {e}")

    print()


def test_config():
    """测试配置更新"""
    print("=" * 60)
    print("测试 2: 检查配置更新")
    print("=" * 60)

    try:
        from app.config import settings

        print(f"✅ CONVERSION_TIMEOUT: {settings.CONVERSION_TIMEOUT}秒")

        if hasattr(settings, "PDF_LARGE_FILE_THRESHOLD_MB"):
            print(f"✅ PDF_LARGE_FILE_THRESHOLD_MB: {settings.PDF_LARGE_FILE_THRESHOLD_MB}MB")
        else:
            print("⚠️  PDF_LARGE_FILE_THRESHOLD_MB: 未配置（使用默认值20MB）")

        if hasattr(settings, "PDF_STREAM_PROCESSING"):
            print(f"✅ PDF_STREAM_PROCESSING: {settings.PDF_STREAM_PROCESSING}")
        else:
            print("⚠️  PDF_STREAM_PROCESSING: 未配置（使用默认值True）")

    except Exception as e:
        print(f"❌ 配置检查失败: {e}")

    print()


def test_script_functions():
    """测试脚本函数是否可导入"""
    print("=" * 60)
    print("测试 3: 检查脚本函数")
    print("=" * 60)

    try:
        from app.scripts.pdf_to_doc import (  # noqa: F401
            pdf_to_doc_fitz,
            pdf_to_doc_pdfminer,
            pdf_to_doc_pdfplumber,
        )

        print("✅ pdf_to_doc_pdfminer - 可用")
        print("✅ pdf_to_doc_fitz - 可用（PPT优化）")
        print("✅ pdf_to_doc_pdfplumber - 可用")
    except Exception as e:
        print(f"❌ 函数导入失败: {e}")

    print()


def test_ppt_detection_logic():
    """测试PPT检测逻辑"""
    print("=" * 60)
    print("测试 4: PPT宽高比检测逻辑")
    print("=" * 60)

    # 16:9 幻灯片
    aspect_16_9 = 16 / 9
    is_ppt_16_9 = 1.7 < aspect_16_9 < 1.8
    print(f"16:9 幻灯片 - 宽高比: {aspect_16_9:.3f}, 检测: {'✅ PPT' if is_ppt_16_9 else '❌'}")

    # 4:3 幻灯片
    aspect_4_3 = 4 / 3
    is_ppt_4_3 = 1.3 < aspect_4_3 < 1.4
    print(f"4:3 幻灯片  - 宽高比: {aspect_4_3:.3f}, 检测: {'✅ PPT' if is_ppt_4_3 else '❌'}")

    # A4 纸张
    aspect_a4 = 210 / 297  # A4纸张比例
    is_ppt_a4 = (1.7 < aspect_a4 < 1.8) or (1.3 < aspect_a4 < 1.4)
    print(
        f"A4 文档     - 宽高比: {aspect_a4:.3f}, 检测: {'❌ 普通PDF' if not is_ppt_a4 else '✅ PPT'}"
    )

    print()


def test_file_size_threshold():
    """测试文件大小阈值"""
    print("=" * 60)
    print("测试 5: 文件大小阈值计算")
    print("=" * 60)

    threshold_mb = 20
    threshold_bytes = threshold_mb * 1024 * 1024

    print(f"大文件阈值: {threshold_mb}MB = {threshold_bytes:,} bytes")
    print("小文件 (<20MB): 使用 pdfminer (稳定性优先)")
    print("大文件 (≥20MB): 使用 PyMuPDF (性能优先)")

    # 示例文件大小
    examples = [
        ("小PDF", 5 * 1024 * 1024),
        ("中等PDF", 15 * 1024 * 1024),
        ("大PDF", 30 * 1024 * 1024),
        ("超大PDF", 100 * 1024 * 1024),
    ]

    print("\n文件大小示例:")
    for name, size in examples:
        size_mb = size / (1024 * 1024)
        strategy = "PyMuPDF (性能)" if size >= threshold_bytes else "pdfminer (稳定)"
        print(f"  {name}: {size_mb:.1f}MB → {strategy}")

    print()


def main():
    """运行所有测试"""
    print("\n" + "🔍 " + "PDF转Word改进 - 快速验证".center(56) + " 🔍")
    print()

    test_imports()
    test_config()
    test_script_functions()
    test_ppt_detection_logic()
    test_file_size_threshold()

    print("=" * 60)
    print("验证完成!")
    print("=" * 60)
    print("\n📖 详细说明请查看: PDF_TO_WORD_IMPROVEMENTS.md")
    print()


if __name__ == "__main__":
    main()
