#!/usr/bin/env python3
import argparse
import sys
import os
import zipfile
from PIL import Image
import fitz  # PyMuPDF


def convert_image_to_image(input_path, output_path, target_format):
    """图片转图片"""
    try:
        with Image.open(input_path) as img:
            # 转换模式以适应目标格式
            if target_format.lower() in ["jpg", "jpeg"]:
                if img.mode in ("RGBA", "LA"):
                    # JPG 不支持透明度，转为 RGB 背景白色
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != "RGB":
                    img = img.convert("RGB")

            img.save(output_path, quality=95)
        return True
    except Exception as e:
        print(f"[ERROR] Image conversion failed: {e}")
        return False


def convert_image_to_pdf(input_path, output_path):
    """图片转 PDF"""
    try:
        with Image.open(input_path) as img:
            if img.mode == "RGBA":
                img = img.convert("RGB")
            img.save(output_path, "PDF", resolution=100.0)
        return True
    except Exception as e:
        print(f"[ERROR] Image to PDF failed: {e}")
        return False


def convert_pdf_to_image(input_path, output_path, target_format):
    """PDF 转图片 (单页直接转，多页转ZIP)"""
    try:
        doc = fitz.open(input_path)
        page_count = len(doc)

        if page_count == 0:
            print("[ERROR] Empty PDF")
            return False

        # 如果只有一页，直接输出图片
        if page_count == 1:
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=150)
            pix.save(output_path)
            return True

        # 如果有多页，打包成 ZIP
        # 注意：output_path 传入时是 .zip 结尾吗？
        # 路由层传入的 output_path 是根据 target_format 生成的。
        # 如果 target 是 png，output_path 是 xxx.png。
        # 这里我们需要修改 output_path 为 .zip，或者在路由层处理。
        # 为了简单，如果多页，我们生成一个 zip 文件，并重命名 output_path 为 .zip (如果它不是)
        # 但路由层可能已经确定了文件名。
        # 策略：如果多页，生成 zip，并把 zip 内容写入 output_path (如果 output_path 扩展名不重要)
        # 或者，强制要求 PDF -> Image 返回 ZIP 如果多页。
        # 但前端可能期待 .png。
        # 如果前端请求 pdf -> png，得到一个 zip，浏览器下载后文件名是 xxx.png，内容是 zip。
        # 用户改后缀解压即可。但这体验不好。
        #
        # 更好的做法：只转换第一页？或者生成长图？
        # 用户通常期望每一页都是一张图。
        # 让我们生成 ZIP。

        # 临时目录
        base_name = os.path.splitext(os.path.basename(output_path))[0]
        temp_dir = os.path.dirname(output_path)

        zip_path = output_path
        if not zip_path.endswith(".zip"):
            zip_path = os.path.splitext(output_path)[0] + ".zip"

        with zipfile.ZipFile(zip_path, "w") as zf:
            for i in range(page_count):
                page = doc.load_page(i)
                pix = page.get_pixmap(dpi=150)
                img_filename = f"{base_name}_{i+1}.{target_format}"
                img_path = os.path.join(temp_dir, img_filename)
                pix.save(img_path)
                zf.write(img_path, img_filename)
                os.remove(img_path)

        # 如果原始 output_path 不是 zip，重命名
        if output_path != zip_path:
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(zip_path, output_path)

        return True

    except Exception as e:
        print(f"[ERROR] PDF to Image failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Image Converter")
    parser.add_argument("-i", "--input", required=True, help="Input file path")
    parser.add_argument("-o", "--output", required=True, help="Output file path")
    parser.add_argument("-t", "--target", required=True, help="Target format (jpg, png, pdf, etc.)")

    args = parser.parse_args()

    input_ext = os.path.splitext(args.input)[1].lower()
    target = args.target.lower()

    print(f"[INFO] Converting {args.input} -> {args.output} (Target: {target})")

    success = False

    if input_ext == ".pdf":
        # PDF -> Image
        success = convert_pdf_to_image(args.input, args.output, target)
    elif target == "pdf":
        # Image -> PDF
        success = convert_image_to_pdf(args.input, args.output)
    else:
        # Image -> Image
        success = convert_image_to_image(args.input, args.output, target)

    if success:
        print(f"[SUCCESS] Conversion complete: {args.output}")
        sys.exit(0)
    else:
        print("[ERROR] Conversion failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
