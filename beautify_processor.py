"""
美化截图处理器
实现截图美化功能
"""

import sys

from PIL import Image

from config import config
from image_processor import ImageProcessor, ImageUtils


class BeautifyProcessor(ImageProcessor):
    """美化截图处理器"""

    def __init__(self):
        super().__init__(config.beautify_workflow_name)
        self.beautify_config = config.beautify

    def process_image(self, image: Image.Image) -> Image.Image:
        """处理图像：添加圆角和渐变背景"""
        # 计算圆角半径
        radius = ImageUtils.calculate_radius(
            image, max_radius=self.beautify_config.max_radius
        )

        # 添加圆角
        rounded_image = ImageUtils.add_rounded_corners(image, radius)

        # 计算内边距和背景尺寸
        padding = ImageUtils.calculate_padding(
            rounded_image, max_padding=self.beautify_config.max_padding
        )
        print("Padding:", padding, file=sys.stderr)
        background_size = (
            rounded_image.width + 2 * padding,
            rounded_image.height + 2 * padding,
        )

        # 创建渐变背景（RGBA，支持透明）
        gradient_background = ImageUtils.create_gradient_background(
            background_size,
            self.beautify_config.start_color,
            self.beautify_config.end_color,
        ).convert("RGBA")

        # 计算居中位置
        position = (
            (background_size[0] - rounded_image.width) // 2,
            (background_size[1] - rounded_image.height) // 2,
        )

        # 合并图像，使用alpha通道作为mask
        if rounded_image.mode != "RGBA":
            rounded_image = rounded_image.convert("RGBA")
        alpha = rounded_image.split()[-1]
        gradient_background.paste(rounded_image, position, mask=alpha)

        return gradient_background


def main(source: str = "clipboard"):
    """主函数"""
    processor = BeautifyProcessor()
    if source == "file":
        import os
        file_paths = os.environ["files"]
        print("File paths:", file_paths, file=sys.stderr)
        for file_path in file_paths.split("\t"):
            base, ext = os.path.splitext(file_path)
            if file_path.lower().endswith(".gif"):
                output_path = processor.process_gif_file(file_path)
            else:
                processor.process_image_file(file_path)
    elif source == "clipboard":
        processor.run()


if __name__ == "__main__":
    main()
