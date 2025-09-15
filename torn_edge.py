import io
import numpy as np
from PIL import Image, ImageGrab
from Cocoa import NSData, NSImage, NSPasteboard, NSPasteboardTypePNG
from utils import show_macos_notification

def get_image_from_clipboard():
    img = ImageGrab.grabclipboard()
    if isinstance(img, Image.Image):
        show_macos_notification("Torn Edge Effect", "✅成功读取剪贴板上的图像")
        return img
    else:
        raise ValueError("No image found in clipboard")

def image_to_clipboard(image):
    # Load the image using Pillow
    if isinstance(image, str):
        image = Image.open(image)

    # Save the image to a bytes buffer
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    image_data = buffer.getvalue()

    # Convert the bytes buffer to NSData
    data = NSData.dataWithBytes_length_(image_data, len(image_data))

    # Create an NSImage from the NSData
    ns_image = NSImage.alloc().initWithData_(data)

    # Copy the NSImage to the clipboard
    pb = NSPasteboard.generalPasteboard()
    pb.clearContents()
    pb.setData_forType_(data, NSPasteboardTypePNG)
    show_macos_notification("Torn Edge Effect", "✅成功复制图像到剪贴板")

def extract_and_apply_torn_edge(target_img, source_torn_img, edge='all', thickness=50):
    """
    从带有撕裂边缘特效的源图片中提取边缘形状，并应用到目标图片上。

    Args:
        target_img (Image): 目标图片对象。
        source_torn_img (Image): 带有撕裂边缘特效的源图片对象。
        edge (str): 应用撕裂边缘的方位，可以是 'top', 'bottom', 'left', 'right' 或 'all'。
        thickness (int): 提取的撕裂边缘的厚度。
    
    Returns:
        Image: 处理后的图片对象。
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
            if source_region:
                mask = source_region.split()[3]
                resized_mask = mask.resize((target_box[2] - target_box[0], target_box[3] - target_box[1]))
                temp_alpha = new_alpha.crop(target_box)
                new_alpha.paste(Image.composite(Image.new('L', temp_alpha.size, 255), Image.new('L', temp_alpha.size, 0), resized_mask), target_box)

        if edge in ('top', 'all'):
            if thickness <= source_height:
                top_region = source_torn_img.crop((0, 0, source_width, thickness))
                apply_mask_from_source(top_region, (0, 0, target_width, thickness))

        if edge in ('bottom', 'all'):
            if thickness <= source_height:
                bottom_region = source_torn_img.crop((0, source_height - thickness, source_width, source_height))
                apply_mask_from_source(bottom_region, (0, target_height - thickness, target_width, target_height))

        if edge in ('left', 'all'):
            if thickness <= source_width:
                left_region = source_torn_img.crop((0, 0, thickness, source_height))
                apply_mask_from_source(left_region, (0, 0, thickness, target_height))

        if edge in ('right', 'all'):
            if thickness <= source_width:
                right_region = source_torn_img.crop((source_width - thickness, 0, source_width, source_height))
                apply_mask_from_source(right_region, (target_width - thickness, 0, target_width, target_height))

        target_img.putalpha(new_alpha)
        return target_img

    except Exception as e:
        print(f"处理图像时发生错误: {e}")
        return None

# 主程序
try:
    # 从剪贴板获取图像
    target_image = get_image_from_clipboard()
    
    # 加载基础撕裂边缘图片
    source_torn_image = Image.open("base.png")
    
    # 应用撕裂边缘效果
    result_image = extract_and_apply_torn_edge(target_image, source_torn_image, edge='all', thickness=80)
    
    if result_image:
        # 将结果图像复制到剪贴板
        image_to_clipboard(result_image)
    else:
        show_macos_notification("Torn Edge Effect", "❌处理图像失败")
        
except ValueError as e:
    print(f"错误: {e}")
    show_macos_notification("Torn Edge Effect", "❌剪贴板上没有图像")
except FileNotFoundError:
    print("错误: 找不到base.png文件")
    show_macos_notification("Torn Edge Effect", "❌找不到base.png文件")
except Exception as e:
    print(f"发生错误: {e}")
    show_macos_notification("Torn Edge Effect", f"❌发生错误: {str(e)[:50]}")