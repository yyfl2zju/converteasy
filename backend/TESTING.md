# 快速测试指南

## 测试增强版 PDF 转 Word 功能

### 1. 准备测试文件

创建或下载一个包含图片和格式的 PDF 文件，放到 `backend/tests/samples/` 目录。

### 2. 运行转换测试

```powershell
# 激活环境
conda activate converteasy

# 进入后端目录
cd E:\Desktop\converteasy-main\backend

# 测试转换（替换为你的测试文件）
python app/scripts/pdf_to_doc_enhanced.py -i tests/samples/your_test.pdf -o tests/output/result.docx
```

### 3. 运行单元测试

```powershell
# 运行所有测试
pytest

# 只运行新增的测试
pytest tests/test_pdf_to_word_enhanced.py -v

# 运行测试并显示详细输出
pytest tests/test_pdf_to_word_enhanced.py -v -s
```

### 4. 验证结果

打开生成的 `result.docx` 文件，检查：
- ✅ 图片是否保留
- ✅ 字体格式是否保留（加粗、斜体等）
- ✅ 颜色是否正确
- ✅ 表格格式是否完整
- ✅ 段落对齐方式是否正确

### 5. 通过API测试（可选）

启动后端服务后，访问 http://127.0.0.1:8080/docs，测试：
1. 上传一个 PDF 文件
2. 选择转换为 DOCX
3. 下载结果查看

## 已知限制

`pdf2docx` 库的一些限制：
- 复杂的 PDF 布局可能无法完美还原
- 某些特殊字体可能被替换为默认字体
- 极大的 PDF 文件可能需要较长时间转换

## 回退方案

如果遇到问题，可以通过修改 `config.py` 回退到旧版本：

```python
"pdf->doc": {"script": "pdf_to_doc.py", "description": "PDF 转 Word"},
"pdf->docx": {"script": "pdf_to_doc.py", "description": "PDF 转 Word"},
```
