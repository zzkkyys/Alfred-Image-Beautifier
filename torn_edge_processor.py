"""
撕裂边缘处理器
实现撕裂边缘效果功能
"""

import os

from PIL import Image

from config import config
from image_processor import ImageProcessor
from utils import show_macos_notification


class TornEdgeProcessor(ImageProcessor):
    """撕裂边缘处理器"""

    def __init__(self):
        super().__init__(config.torn_edge_workflow_name)
        self.torn_config = config.torn_edge

    def extract_and_apply_torn_edge(
        self,
        target_img: Image.Image,
        source_torn_img: Image.Image,
        edge: str = "all",
        thickness: int = 50,
    ) -> Image.Image:
        """
        从带有撕裂边缘特效的源图片中提取边缘形状，并应用到目标图片上。

        Args:
            target_img: 目标图片对象
            source_torn_img: 带有撕裂边缘特效的源图片对象
            edge: 应用撕裂边缘的方位，可以是 'top', 'bottom', 'left', 'right' 或 'all'
            thickness: 提取的撕裂边缘的厚度

        Returns:
            处理后的图片对象
        """
        try:
            # 确保两个图像都是RGBA模式
            target_img = target_img.convert("RGBA")
            source_torn_img = source_torn_img.convert("RGBA")

            target_width, target_height = target_img.size
            source_width, source_height = source_torn_img.size

            target_alpha = target_img.split()[3].copy()
            new_alpha = target_alpha

            def apply_mask_from_source(source_region, target_box):
                """从源区域应用遮罩到目标区域"""
                if source_region:
                    mask = source_region.split()[3]
                    resized_mask = mask.resize(
                        (target_box[2] - target_box[0], target_box[3] - target_box[1])
                    )
                    temp_alpha = new_alpha.crop(target_box)
                    composite_mask = Image.composite(
                        Image.new("L", temp_alpha.size, 255),
                        Image.new("L", temp_alpha.size, 0),
                        resized_mask,
                    )
                    new_alpha.paste(composite_mask, target_box)

            # 应用顶部边缘
            if edge in ("top", "all"):
                if thickness <= source_height:
                    top_region = source_torn_img.crop((0, 0, source_width, thickness))
                    apply_mask_from_source(top_region, (0, 0, target_width, thickness))

            # 应用底部边缘
            if edge in ("bottom", "all"):
                if thickness <= source_height:
                    bottom_region = source_torn_img.crop(
                        (0, source_height - thickness, source_width, source_height)
                    )
                    apply_mask_from_source(
                        bottom_region,
                        (0, target_height - thickness, target_width, target_height),
                    )

            # 应用左侧边缘
            if edge in ("left", "all"):
                if thickness <= source_width:
                    left_region = source_torn_img.crop((0, 0, thickness, source_height))
                    apply_mask_from_source(
                        left_region, (0, 0, thickness, target_height)
                    )

            # 应用右侧边缘
            if edge in ("right", "all"):
                if thickness <= source_width:
                    right_region = source_torn_img.crop(
                        (source_width - thickness, 0, source_width, source_height)
                    )
                    apply_mask_from_source(
                        right_region,
                        (target_width - thickness, 0, target_width, target_height),
                    )

            target_img.putalpha(new_alpha)
            return target_img

        except Exception as e:
            print(f"处理图像时发生错误: {e}")
            return None

    def process_image(self, image: Image.Image) -> Image.Image:
        """处理图像：添加撕裂边缘效果"""
        # 检查源图像文件是否存在
        if not os.path.exists(self.torn_config.source_image_path):
            raise FileNotFoundError(f"找不到{self.torn_config.source_image_path}文件")

        # 加载基础撕裂边缘图片
        source_torn_image = Image.open(self.torn_config.source_image_path)

        # 应用撕裂边缘效果
        result_image = self.extract_and_apply_torn_edge(
            image,
            source_torn_image,
            edge=self.torn_config.edge,
            thickness=self.torn_config.thickness,
        )

        if result_image is None:
            raise RuntimeError("处理图像失败")

        return result_image

    def run(self) -> None:
        """运行撕裂边缘处理流程"""
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
        except FileNotFoundError as e:
            print(f"错误: {e}")
            show_macos_notification(self.workflow_name, f"❌{e}")
        except Exception as e:
            print(f"发生错误: {e}")
            show_macos_notification(self.workflow_name, f"❌发生错误: {str(e)[:50]}")


def main():
    """主函数"""
    processor = TornEdgeProcessor()
    processor.run()


if __name__ == "__main__":
    main()
