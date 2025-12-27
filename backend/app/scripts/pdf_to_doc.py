#!/usr/bin/env python3
import argparse
import sys
import os
import traceback
import time
import subprocess
from pdfminer.high_level import extract_text, extract_pages
from pdfminer.layout import LTTextContainer
from docx import Document
from docx.shared import Pt


def save_document(doc, doc_path):
    """保存文档，如果目标是 .doc，则先保存为 .docx 再转换"""
    if doc_path.lower().endswith(".doc"):
        temp_docx = doc_path + "x"
        doc.save(temp_docx)
        print(f"[INFO] 已保存临时文件: {temp_docx}")

        try:
            print("[INFO] 正在调用 LibreOffice 将 DOCX 转换为 DOC...")
            out_dir = os.path.dirname(os.path.abspath(doc_path))

            cmd = ["soffice", "--headless", "--convert-to", "doc", "--outdir", out_dir, temp_docx]

            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if os.path.exists(temp_docx):
                os.remove(temp_docx)

            if not os.path.exists(doc_path):
                print(f"[WARNING] LibreOffice 转换看似成功但未找到输出文件: {doc_path}")

        except Exception as e:
            print(f"[ERROR] LibreOffice 转换失败: {e}")
            print("[INFO] 回退方案: 直接重命名 .docx 为 .doc")
            if os.path.exists(temp_docx):
                if os.path.exists(doc_path):
                    os.remove(doc_path)
                os.rename(temp_docx, doc_path)
    else:
        doc.save(doc_path)


def pdf_to_doc_pdfminer(pdf_path, doc_path):
    """使用 pdfminer 提取文本并转换为 Word 文档（优化版）"""
    try:
        print(f"[INFO] 开始转换: {pdf_path} -> {doc_path}")
        start_time = time.time()

        # 获取文件大小
        file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        print(f"[INFO] 文件大小: {file_size_mb:.2f} MB")

        # 创建 Word 文档
        doc = Document()
        total_paragraphs = 0
        total_pages = 0

        # 使用流式处理，避免一次性加载整个文件
        print("[INFO] 使用流式处理模式...")

        try:
            # 逐页处理PDF，减少内存占用
            for page_num, page_layout in enumerate(extract_pages(pdf_path), 1):
                total_pages += 1

                # 每10页输出一次进度
                if page_num % 10 == 0:
                    elapsed = time.time() - start_time
                    print(f"[PROGRESS] 已处理 {page_num} 页 (耗时: {elapsed:.1f}秒)")

                page_text = ""

                # 提取页面文本
                for element in page_layout:
                    if isinstance(element, LTTextContainer):
                        page_text += element.get_text()

                if page_text.strip():
                    # 按段落分割
                    paragraphs = page_text.split("\n\n")

                    for para in paragraphs:
                        para = para.strip()
                        if para and len(para) > 2:  # 过滤太短的内容
                            # 处理超长段落
                            if len(para) > 1500:
                                # 按句子分割长段落
                                sentences = para.replace(". ", ".\n").split("\n")
                                for sentence in sentences:
                                    if sentence.strip():
                                        p = doc.add_paragraph(sentence.strip())
                                        # 为较短的行设置较小的间距（可能是标题）
                                        if len(sentence) < 100:
                                            p.paragraph_format.space_after = Pt(6)
                                        total_paragraphs += 1
                            else:
                                p = doc.add_paragraph(para)
                                # 智能判断是否为标题（较短且可能全大写）
                                if len(para) < 100 and (para.isupper() or para.istitle()):
                                    p.runs[0].bold = True
                                    p.runs[0].font.size = Pt(14)
                                    p.paragraph_format.space_after = Pt(12)
                                total_paragraphs += 1

                # 添加页面分隔（每5页一次，避免文档过长）
                if page_num % 5 == 0 and page_num < total_pages:
                    doc.add_paragraph("_" * 50)

                # 大文件处理：每处理50页释放一些资源
                if file_size_mb > 20 and page_num % 50 == 0:
                    print(f"[INFO] 释放内存（已处理 {page_num} 页）")
                    import gc

                    gc.collect()

        except Exception as e:
            print(f"[WARNING] 流式处理失败，尝试简单模式: {str(e)}")
            # 回退到简单模式
            text = extract_text(pdf_path)
            if text and text.strip():
                paragraphs = text.split("\n\n")
                for para in paragraphs:
                    para = para.strip()
                    if para and len(para) > 2:
                        doc.add_paragraph(para)
                        total_paragraphs += 1

        # 如果没有提取到内容
        if total_paragraphs == 0:
            doc.add_paragraph("此 PDF 文件没有可提取的文本内容")
            doc.add_paragraph("")
            doc.add_paragraph("可能的原因：")
            doc.add_paragraph("1. PDF 由图片组成，没有文本层")
            doc.add_paragraph("2. PDF 使用了特殊编码")
            doc.add_paragraph("3. PDF 文件损坏")
            print("[WARNING] 未提取到文本内容")

        # 保存文档
        save_document(doc, doc_path)
        elapsed = time.time() - start_time
        print(f"[SUCCESS] 转换成功: {pdf_path} -> {doc_path}")
        print(f"[INFO] 处理了 {total_pages} 页，提取了 {total_paragraphs} 个段落")
        print(f"[INFO] 总耗时: {elapsed:.1f} 秒")
        return True

    except Exception as e:
        print(f"[ERROR] pdfminer 转换失败: {str(e)}")
        traceback.print_exc()
        return False


def pdf_to_doc_pdfplumber(pdf_path, doc_path):
    """备选方案：使用 pdfplumber 提取文本"""
    try:
        import pdfplumber

        print(f"[INFO] 使用 pdfplumber 转换: {pdf_path} -> {doc_path}")

        doc = Document()
        total_pages = 0
        total_paragraphs = 0

        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)

            for page_num, page in enumerate(pdf.pages, 1):
                print(f"[INFO] 处理第 {page_num}/{total_pages} 页")

                # 提取文本
                text = page.extract_text()

                if text and text.strip():
                    paragraphs = text.split("\n\n")
                    for para in paragraphs:
                        para = para.strip()
                        if para:
                            doc.add_paragraph(para)
                            total_paragraphs += 1
                else:
                    # 如果没提取到文本，添加占位符
                    doc.add_paragraph(f"第 {page_num} 页 - 无文本内容")
                    total_paragraphs += 1

        if total_paragraphs == 0:
            doc.add_paragraph("未能从 PDF 中提取到文本内容")

        save_document(doc, doc_path)
        print(f"[SUCCESS] pdfplumber 转换成功: {pdf_path} -> {doc_path}")
        print(f"[INFO] 处理了 {total_pages} 页，提取了 {total_paragraphs} 个段落")
        return True

    except Exception as e:
        print(f"[ERROR] pdfplumber 转换失败: {str(e)}")
        return False


def pdf_to_doc_fitz(pdf_path, doc_path):
    """使用 PyMuPDF (fitz) 提取文本（优化版，适合PPT转PDF）"""
    try:
        import fitz  # PyMuPDF

        print(f"[INFO] 使用 PyMuPDF 转换: {pdf_path} -> {doc_path}")
        start_time = time.time()

        file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        print(f"[INFO] 文件大小: {file_size_mb:.2f} MB")

        doc = Document()
        total_pages = 0
        total_paragraphs = 0
        total_images = 0

        # 打开 PDF 文件
        pdf_document = fitz.open(pdf_path)
        total_pages = len(pdf_document)
        print(f"[INFO] PDF总页数: {total_pages}")

        # 检测是否为PPT来源PDF（通常页面尺寸比例接近16:9或4:3）
        first_page = pdf_document[0]
        page_rect = first_page.rect
        aspect_ratio = page_rect.width / page_rect.height
        is_ppt_like = (1.7 < aspect_ratio < 1.8) or (1.3 < aspect_ratio < 1.4)

        if is_ppt_like:
            print(f"[INFO] 检测到PPT风格PDF (宽高比: {aspect_ratio:.2f})，使用优化模式")

        for page_num in range(total_pages):
            # 进度显示
            if page_num % 10 == 0:
                elapsed = time.time() - start_time
                print(f"[PROGRESS] 处理第 {page_num + 1}/{total_pages} 页 (耗时: {elapsed:.1f}秒)")

            # 获取页面
            page = pdf_document[page_num]

            # 提取文本（使用"blocks"模式保留布局信息）
            blocks = page.get_text("blocks")

            page_has_content = False

            # 按位置排序blocks（从上到下，从左到右）
            blocks.sort(key=lambda b: (b[1], b[0]))  # (y0, x0)

            for block in blocks:
                # block格式: (x0, y0, x1, y1, "text", block_no, block_type)
                if len(block) >= 5:
                    text = block[4].strip()

                    if text and len(text) > 1:
                        page_has_content = True

                        # PPT风格处理：识别标题
                        if is_ppt_like:
                            # 靠近页面顶部的文本可能是标题
                            y_pos = block[1]
                            page_height = page_rect.height

                            if y_pos < page_height * 0.25:  # 上部25%
                                p = doc.add_paragraph(text)
                                p.runs[0].bold = True
                                p.runs[0].font.size = Pt(16)
                                p.paragraph_format.space_after = Pt(12)
                                total_paragraphs += 1
                            else:
                                # 内容文本
                                lines = text.split("\n")
                                for line in lines:
                                    line = line.strip()
                                    if line and len(line) > 1:
                                        p = doc.add_paragraph(line)
                                        # 列表项检测
                                        if line.startswith(("•", "-", "*", "·")) or (
                                            len(line) > 0 and line[0].isdigit() and "." in line[:3]
                                        ):
                                            p.style = "List Bullet"
                                        total_paragraphs += 1
                        else:
                            # 普通PDF处理
                            p = doc.add_paragraph(text)
                            # 短文本可能是标题
                            if len(text) < 100 and (text.isupper() or text.count(" ") < 5):
                                p.runs[0].bold = True
                                p.runs[0].font.size = Pt(14)
                            total_paragraphs += 1

            # 如果页面没有文本，尝试提取图片信息
            if not page_has_content:
                image_list = page.get_images()
                if image_list:
                    doc.add_paragraph(
                        f"[第 {page_num + 1} 页包含 {len(image_list)} 张图片，无文本]"
                    )
                    total_images += len(image_list)
                    total_paragraphs += 1
                else:
                    doc.add_paragraph(f"[第 {page_num + 1} 页无内容]")
                    total_paragraphs += 1

            # 添加页面分隔符（PPT风格每页都分隔）
            if is_ppt_like:
                doc.add_paragraph("")
                doc.add_paragraph("=" * 60)
                doc.add_paragraph("")
            elif page_num % 3 == 0 and page_num < total_pages - 1:
                doc.add_paragraph("_" * 50)

            # 大文件内存管理
            if file_size_mb > 20 and page_num % 50 == 0 and page_num > 0:
                print(f"[INFO] 释放内存（已处理 {page_num} 页）")
                import gc

                gc.collect()

        pdf_document.close()

        if total_paragraphs == 0:
            doc.add_paragraph("未能从 PDF 中提取到文本内容")

        save_document(doc, doc_path)
        elapsed = time.time() - start_time
        print(f"[SUCCESS] PyMuPDF 转换成功: {pdf_path} -> {doc_path}")
        print(f"[INFO] 处理了 {total_pages} 页，提取了 {total_paragraphs} 个段落")
        if total_images > 0:
            print(f"[INFO] 检测到 {total_images} 张图片")
        print(f"[INFO] 总耗时: {elapsed:.1f} 秒")
        return True

    except Exception as e:
        print(f"[ERROR] PyMuPDF 转换失败: {str(e)}")
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description="PDF 转 Word 文档")
    parser.add_argument("-i", "--input", required=True, help="输入 PDF 文件路径")
    parser.add_argument("-o", "--output", required=True, help="输出 Word 文件路径")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[ERROR] 输入文件不存在: {args.input}")
        sys.exit(1)

    if not args.input.lower().endswith(".pdf"):
        print(f"[ERROR] 输入文件不是 PDF 格式: {args.input}")
        sys.exit(1)

    print(f"[INFO] 输入文件: {args.input}")
    print(f"[INFO] 输出文件: {args.output}")
    file_size = os.path.getsize(args.input)
    file_size_mb = file_size / (1024 * 1024)
    print(f"[INFO] 文件大小: {file_size} 字节 ({file_size_mb:.2f} MB)")

    # 根据文件大小选择最佳转换策略
    success = False

    # 大文件（>20MB）或可能是PPT来源的PDF，优先使用 PyMuPDF
    if file_size_mb > 20:
        print("[INFO] 检测到大文件，优先使用 PyMuPDF（性能更好）")
        print("[INFO] 尝试方法1: PyMuPDF (优化大文件)")
        success = pdf_to_doc_fitz(args.input, args.output)

        if not success:
            print("[INFO] 尝试方法2: pdfminer (流式处理)")
            success = pdf_to_doc_pdfminer(args.input, args.output)

        if not success:
            print("[INFO] 尝试方法3: pdfplumber")
            success = pdf_to_doc_pdfplumber(args.input, args.output)
    else:
        # 小文件使用原有顺序
        print("[INFO] 尝试方法1: pdfminer (最稳定)")
        success = pdf_to_doc_pdfminer(args.input, args.output)

        if not success:
            print("[INFO] 尝试方法2: PyMuPDF (布局保留)")
            success = pdf_to_doc_fitz(args.input, args.output)

        if not success:
            print("[INFO] 尝试方法3: pdfplumber")
            success = pdf_to_doc_pdfplumber(args.input, args.output)

    if success:
        # 验证输出文件
        if os.path.exists(args.output) and os.path.getsize(args.output) > 0:
            print(f"[SUCCESS] 最终转换成功，输出文件大小: {os.path.getsize(args.output)} 字节")
            sys.exit(0)
        else:
            print("[ERROR] 输出文件创建失败或为空")
            sys.exit(1)
    else:
        print("[ERROR] 所有转换方法都失败了")
        print("[INFO] 请检查是否安装了必要的依赖:")
        print("  pip install pdfminer.six python-docx pdfplumber PyMuPDF")
        sys.exit(1)


if __name__ == "__main__":
    main()
