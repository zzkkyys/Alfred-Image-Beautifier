"""
白底替换处理器
将图像的透明区域替换为白色背景
"""

from PIL import Image
from base.config import config
from base.image_processor import ImageProcessor

class WhiteBGProcessor(ImageProcessor):
    """将透明区域替换为白色背景的处理器"""
    def __init__(self):
        super().__init__("WhiteBG Processor")

    def process_image(self, image: Image.Image) -> Image.Image:
        # 确保为RGBA
        image = image.convert("RGBA")
        # 创建白色背景
        white_bg = Image.new("RGBA", image.size, (255, 255, 255, 255))
        # 粘贴原图，使用自身alpha作为mask
        white_bg.paste(image, (0, 0), mask=image)
        # 转为RGB，去除alpha
        return white_bg.convert("RGBA")

    def rename_file(self, input_path: str) -> str:
        import os
        base, ext = os.path.splitext(input_path)
        if input_path.lower().endswith(".gif"):
            return base + "_whitebg.gif"
        else:
            return base + "_whitebg.jpg"


def main():
    processor = WhiteBGProcessor()
    processor.run()

if __name__ == "__main__":
    main()
