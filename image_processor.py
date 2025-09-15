"""
图像处理基类模块
提供统一的图像处理接口和通用功能
"""

import io
import os
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union

import numpy as np
from Cocoa import NSData, NSImage, NSPasteboard, NSPasteboardTypePNG
from PIL import Image, ImageDraw, ImageGrab, ImageOps

from utils import show_macos_notification


class ImageProcessor(ABC):
    """图像处理基类"""

    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name

    def get_image_from_clipboard(self) -> Image.Image:
        """从剪贴板获取图像"""
        img = ImageGrab.grabclipboard()
        if isinstance(img, Image.Image):
            # 强制转换为RGBA，保证透明通道
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            show_macos_notification(self.workflow_name, "✅成功读取剪贴板上的图像")
            return img
        else:
            raise ValueError("No image found in clipboard")

    def image_to_clipboard(self, image: Union[Image.Image, str]) -> None:
        """将图像复制到剪贴板"""
        if isinstance(image, str):
            image = Image.open(image)

        # 保存图像到字节缓冲区
        # 强制转换为RGBA，保证透明通道
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_data = buffer.getvalue()

        # 转换为NSData
        data = NSData.dataWithBytes_length_(image_data, len(image_data))

        # 创建NSImage并复制到剪贴板
        ns_image = NSImage.alloc().initWithData_(data)
        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        pb.setData_forType_(data, NSPasteboardTypePNG)
        show_macos_notification(self.workflow_name, "✅成功复制处理后的图像到剪贴板")

    @abstractmethod
    def process_image(self, image: Image.Image) -> Image.Image:
        """处理图像的核心方法，子类必须实现"""
        pass

    def process_image_file(self, input_path: str, output_path: str = None) -> str:
        """处理图片文件并保存结果
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径（可选，默认自动生成）
        Returns:
            输出图片路径
        """
        image = Image.open(input_path).convert("RGBA")
        result = self.process_image(image)
        if output_path is None:
            base, ext = os.path.splitext(input_path)
            output_path = base + "_processed.png"
        result.save(output_path, format="PNG")
        return output_path
        
    def process_gif_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """处理 GIF 文件并保存结果，保证生成的 GIF 能动"""
        im = Image.open(input_path)

        # 提取原始GIF信息
        duration = im.info.get('duration', 100)
        loop = im.info.get('loop', 0)

        # 第一遍：处理所有帧并保持为RGBA格式
        rgba_frames = []
        try:
            while True:
                # 确保我们处理的是当前帧的副本，并转换为RGBA
                frame_img = im.copy().convert("RGBA")
                processed_frame = self.process_image(frame_img)
                rgba_frames.append(processed_frame)
                im.seek(im.tell() + 1)
        except EOFError:
            pass # 已经读取完所有帧

        if not rgba_frames:
            raise ValueError("Could not process any frames from the GIF.")

        # 第二遍：创建统一调色板并应用到所有帧
        # 我们使用第一帧来生成一个主调色板
        # quantize() 会将图像转换为拥有最佳255色调色板的"P"模式图像
        master_palette_frame = rgba_frames[0].quantize(colors=255)
        
        paletted_frames = []
        for frame in rgba_frames:
            # 将每一帧都强制转换为使用主调色板
            # Corrected code
            # First, convert the frame from RGBA to RGB, then quantize it
            paletted_frame = frame.convert('RGB').quantize(palette=master_palette_frame, dither=Image.Dither.FLOYDSTEINBERG)
            paletted_frames.append(paletted_frame)

        # 设置输出路径
        if output_path is None:
            base, ext = os.path.splitext(input_path)
            output_path = base + "_processed.gif"

        # 保存处理后的帧
        # 注意：第一帧是 paletted_frames[0]，其余的在 append_images 中
        paletted_frames[0].save(
            output_path,
            save_all=True,
            append_images=paletted_frames[1:],
            duration=duration,
            loop=loop,
            optimize=False,
            # 对于包含透明的GIF，需要指定透明度索引
            transparency=master_palette_frame.info.get('transparency', None)
        )
        return output_path
    
    def run(self) -> None:
        """运行图像处理流程"""
        try:
            # 从剪贴板获取图像
            image = self.get_image_from_clipboard()

            # 处理图像
            processed_image = self.process_image(image)

            # 复制到剪贴板
            self.image_to_clipboard(processed_image)

        except ValueError as e:
            print(f"错误: {e}")
            show_macos_notification(self.workflow_name, "❌剪贴板上没有图像")
        except Exception as e:
            print(f"发生错误: {e}")
            show_macos_notification(self.workflow_name, f"❌发生错误: {str(e)[:50]}")


class ImageUtils:
    """图像处理工具类"""

    @staticmethod
    def add_rounded_corners(image: Image.Image, radius: int) -> Image.Image:
        """为图像添加圆角，保留原图透明信息"""
        image = image.convert("RGBA")
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, *image.size), radius, fill=255)
        r, g, b, a = image.split()
        # 只处理alpha通道，圆角区域为原alpha，其他为0
        new_alpha = Image.composite(a, mask, mask)
        rounded_image = Image.merge("RGBA", (r, g, b, new_alpha))
        return rounded_image

    @staticmethod
    def create_gradient_background(
        size: Tuple[int, int],
        start_color: Tuple[int, int, int],
        end_color: Tuple[int, int, int],
    ) -> Image.Image:
        """创建渐变背景"""
        width, height = size

        # 创建坐标网格
        y, x = np.meshgrid(np.linspace(0, 1, height), np.linspace(0, 1, width))

        # 计算RGB值
        r = (start_color[0] + (end_color[0] - start_color[0]) * y).astype(np.uint8)
        g = (start_color[1] + (end_color[1] - start_color[1]) * y).astype(np.uint8)
        b = (start_color[2] + (end_color[2] - start_color[2]) * y).astype(np.uint8)

        # 堆叠RGB通道
        gradient = np.stack([r, g, b], axis=-1)
        gradient = np.transpose(gradient, (1, 0, 2))
        # 增加alpha通道，全部为255
        alpha = np.full((gradient.shape[0], gradient.shape[1], 1), 255, dtype=np.uint8)
        gradient_rgba = np.concatenate([gradient, alpha], axis=-1)
        return Image.fromarray(gradient_rgba, mode="RGBA")

    @staticmethod
    def calculate_radius(image: Image.Image, max_radius: int = 15) -> int:
        """计算合适的圆角半径"""
        radius = int(image.width * 0.05)
        return min(radius, max_radius)

    @staticmethod
    def calculate_padding(image: Image.Image, max_padding: int = 10) -> int:
        """计算合适的内边距"""
        padding = int(image.width * 0.05)
        return min(padding, max_padding)
