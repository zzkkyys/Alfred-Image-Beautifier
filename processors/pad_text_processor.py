# -*- coding: utf-8 -*-

import io
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageSequence

from base.config import config, PadTextConfig
from base.image_processor import ImageProcessor, ImageUtils

def get_text_size(text, font, max_width):
    """
    重写后的函数，支持中文等无空格语言的自动换行。
    """
    if not text:
        return [], 0

    lines = []
    # 创建一个临时的、微小的 Image 对象用于获取 Draw 实例
    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    
    current_line = ""
    total_height = 0

    for char in text:
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=font)
        
        if bbox[2] > max_width:
            if current_line:
                lines.append(current_line)
                bbox_line = draw.textbbox((0, 0), current_line, font=font)
                total_height += bbox_line[3] - bbox_line[1]
            current_line = char
        else:
            current_line = test_line
            
    # 添加最后一行
    if current_line:
        lines.append(current_line)
        bbox_last_line = draw.textbbox((0, 0), current_line, font=font)
        total_height += bbox_last_line[3] - bbox_last_line[1]

    return lines, total_height


class PadTextProcessor(ImageProcessor):
    def __init__(self):
        super().__init__("Pad Text Processor")
        self.pad_text_config: PadTextConfig = config.pad_text

    def process_image(self, img: Image.Image) -> Image.Image:
        text = os.environ.get("text", "默认文本：你好世界").strip()

        # 对于 macOS，Hiragino 是个不错的选择。对于 Windows/Linux，可能需要 'msyh.ttc' 或其他字体。
        font_path = self.pad_text_config.font_path
        font_size = self.pad_text_config.font_size
        pad_color = self.pad_text_config.pad_color
        max_width_ratio = self.pad_text_config.max_width_ratio

        width, height = img.size
        
        
        max_width = int(width * max_width_ratio)
        
        
        
        # 检查字体文件是否存在
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            print(f"警告：字体 '{font_path}' 不存在，使用默认字体。中文可能无法显示。")
            font = ImageFont.load_default()

        # 使用修正后的函数计算文本尺寸和分行
        lines, text_height = get_text_size(text, font, width - 20)
        
        pad_height = text_height + 20
        new_img = Image.new("RGBA", (width, height + pad_height), pad_color + (255,))
        new_img.paste(img, (0, 0))
        draw = ImageDraw.Draw(new_img)
        
        y = height + 10
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            # h = bbox[3] - bbox[1] # 行高已经由 get_text_size 统一处理，这里直接用 textbbox 的高度更准确
            line_height = font.getbbox(line)[3] - font.getbbox(line)[1]
            draw.text(((width - w) // 2, y), line, font=font, fill=(0, 0, 0))
            y += line_height # 使用字体的实际行高来递增 y
            
        return new_img.convert(img.mode)

    def rename_file(self, input_path: str) -> str:
        base, ext = os.path.splitext(input_path)
        if input_path.lower().endswith(".gif"):
            return base + "_padded.gif"
        else:
            return base + "_padded.png"

# --- 示例用法 ---
if __name__ == '__main__':
    # 创建一个空白图片用于测试
    try:
        test_image = Image.new("RGB", (400, 200), "blue")
        
        # 确保设置了环境变量
        if "text" not in os.environ:
            os.environ["text"] = "这是一段比较长的中文测试文本，用于演示自动换行的功能是否正常工作。"
            print(f"环境变量 'text' 未设置，使用默认值: '{os.environ['text']}'")

        processor = PadTextProcessor()
        result_image = processor.process_image(test_image)
        
        # 保存结果
        output_path = "result_padded.png"
        result_image.save(output_path)
        print(f"处理完成，图片已保存到 {output_path}")
        result_image.show()

    except Exception as e:
        print(f"发生错误: {e}")