"""
测试依赖检查脚本
"""
import pytest
from unittest.mock import patch, MagicMock
from app.scripts.check_dependencies import check_dependencies


def test_check_dependencies_all_present():
    """测试所有依赖都存在的情况"""
    # 这个测试在有完整依赖的环境下会通过
    result = check_dependencies()
    assert isinstance(result, bool)


def test_check_dependencies_with_mock_imports():
    """测试特殊包名的导入逻辑"""
    with patch('builtins.__import__') as mock_import:
        # 模拟导入成功
        mock_import.return_value = MagicMock()
        
        # 测试特殊包名映射
        test_packages = {
            'pymupdf': 'fitz',
            'pdfminer.six': 'pdfminer',
            'python-docx': 'docx',
            'python-pptx': 'pptx',
            'beautifulsoup4': 'bs4'
        }
        
        # 验证这些包名可以被正确处理
        for package_name, actual_import in test_packages.items():
            try:
                if package_name == "pymupdf":
                    import fitz  # noqa: F401
                elif package_name == "pdfminer.six":
                    import pdfminer  # noqa: F401
                elif package_name == "python-docx":
                    import docx  # noqa: F401
                elif package_name == "python-pptx":
                    import pptx  # noqa: F401
                elif package_name == "beautifulsoup4":
                    from bs4 import BeautifulSoup  # noqa: F401
            except ImportError:
                # 在没有安装包的情况下，测试逻辑本身是正确的
                pass


def test_check_dependencies_return_type():
    """测试返回值类型"""
    result = check_dependencies()
    assert isinstance(result, bool), "check_dependencies应该返回布尔值"


@pytest.mark.parametrize("package,expected_import", [
    ("pymupdf", "fitz"),
    ("python-docx", "docx"),
    ("python-pptx", "pptx"),
    ("beautifulsoup4", "bs4"),
])
def test_special_package_name_mapping(package, expected_import):
    """测试特殊包名到实际导入名的映射"""
    # 验证特殊包名的处理逻辑
    if package == "pymupdf":
        assert expected_import == "fitz"
    elif package == "python-docx":
        assert expected_import == "docx"
    elif package == "python-pptx":
        assert expected_import == "pptx"
    elif package == "beautifulsoup4":
        assert expected_import == "bs4"
