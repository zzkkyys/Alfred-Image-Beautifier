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
import sys
from .utils import show_macos_notification
from .workflow.notify import notify


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
            notify(self.workflow_name, "✅成功读取剪贴板上的图像")
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
        notify(self.workflow_name, "✅成功复制处理后的图像到剪贴板")

    @abstractmethod
    def process_image(self, image: Image.Image) -> Image.Image:
        """处理图像的核心方法，子类必须实现"""
        pass

    @abstractmethod
    def rename_file(self, input_path: str) -> str:
        """根据输入路径生成新的文件名，子类必须实现"""
        pass
    def process_image_file(self, input_path: str, output_path: str = None) -> str:
        """处理图片文件并保存结果
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径（可选，默认自动生成）
        Returns:
            输出图片路径
        """
        if input_path.lower().endswith('.gif'):
            return self.process_gif_file(input_path, output_path)
        
        image = Image.open(input_path).convert("RGBA")
        result = self.process_image(image)
        if output_path is None:
            output_path = self.rename_file(input_path)
        result.save(output_path, format="PNG")
        return output_path
        

    def process_gif_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """处理 GIF 文件并保存结果，保证生成的 GIF 能动且支持透明（最终确定版）"""
        
        print("Processing GIF with direct index pasting control:", input_path, file=sys.stderr)
        
        im = Image.open(input_path)

        # 1. 设定透明色在调色板中的固定索引
        transparency_index = 255

        # 提取原始GIF信息
        duration = im.info.get('duration', 100)
        loop = im.info.get('loop', 0)

        # 2. 第一遍：处理所有帧，得到最终效果的RGBA图像列表
        rgba_frames = []
        try:
            while True:
                rgba_frame = self.process_image(im.copy().convert("RGBA"))
                rgba_frames.append(rgba_frame)
                im.seek(im.tell() + 1)
        except EOFError:
            pass

        if not rgba_frames:
            raise ValueError("Could not process any frames from the GIF.")

        # 3. 创建一个能代表所有帧颜色的全局统一调色板
        
        # 为了创建一个好的全局调色板，我们将所有帧的RGB数据拼接起来
        all_frames_rgb_data = np.vstack(
            [np.array(frame.convert("RGB")) for frame in rgba_frames]
        )
        all_frames_image = Image.fromarray(all_frames_rgb_data, 'RGB')
        
        # 从这个拼接的图像中生成一个255色的最优调色板，为透明色留出1个位置
        temp_palette_image = all_frames_image.quantize(colors=255, dither=Image.Dither.NONE)
        
        # 创建最终的调色板：前255色来自图像内容，最后1色是我们自己加的
        final_palette = Image.new("P", (1, 1))
        palette_data = temp_palette_image.getpalette()
        if not palette_data: # 以防万一
            palette_data = [0] * (255 * 3)
        # 添加一个任意的颜色（比如黑色）作为透明色的占位符，它将被透明，所以具体颜色不重要
        palette_data.extend([0, 0, 0]) 
        final_palette.putpalette(palette_data)

        # 4. 第二遍：将每一帧转换为调色板模式，并手动应用透明度
        paletted_frames = []
        for frame in rgba_frames:
            # 提取原始的Alpha通道作为遮罩
            alpha_mask = Image.eval(frame.getchannel('A'), lambda a: 255 if a < 128 else 0)

            # 将RGBA帧的颜色信息转换为使用我们的最终调色板的'P'模式图像
            p_frame = frame.convert("RGB").quantize(palette=final_palette, dither=Image.Dither.NONE)

            # 关键步骤：使用paste方法将透明索引“刷”到需要透明的区域
            # 在'P'模式下，paste的第一个参数如果是整数，会被当作调色板索引
            # 我们将索引255（透明色）粘贴到由alpha_mask定义的区域上
            p_frame.paste(transparency_index, mask=alpha_mask)
            
            paletted_frames.append(p_frame)

        # 设置输出路径
        if output_path is None:
            output_path = self.rename_file(input_path)

        # 5. 保存GIF，明确指定透明色的索引
        paletted_frames[0].save(
            output_path,
            save_all=True,
            append_images=paletted_frames[1:],
            duration=duration,
            loop=loop,
            optimize=False,
            transparency=transparency_index
        )
        return output_path

    def run(self,) -> None:
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
            notify(self.workflow_name, "❌剪贴板上没有图像")
        except Exception as e:
            print(f"发生错误: {e}")
            notify(self.workflow_name, f"❌发生错误: {str(e)[:50]}")


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
