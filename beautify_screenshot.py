# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
import io
import numpy as np
from Cocoa import NSData, NSImage, NSPasteboard, NSPasteboardTypePNG
from PIL import Image, ImageDraw, ImageGrab, ImageOps


from utils import show_macos_notification


# +
# Function to read image from clipboard
def get_image_from_clipboard():
    img = ImageGrab.grabclipboard()
    if isinstance(img, Image.Image):
        show_macos_notification("Beautify Screenshot", "✅成功读取剪贴板上的图像")
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
    show_macos_notification("Beautify Screenshot", "✅成功复制美化图像到剪贴板")


# +
# Function to add rounded corners to an image
def add_rounded_corners(image, radius):
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, *image.size), radius, fill=255)
    rounded_image = ImageOps.fit(image, mask.size)
    rounded_image.putalpha(mask)
    return rounded_image




def create_gradient_background(size, start_color, end_color):
    width, height = size
    
    # Create a meshgrid of y and x coordinates normalized between 0 and 1
    y, x = np.meshgrid(np.linspace(0, 1, height), np.linspace(0, 1, width))
    
    # Calculate the RGB values using vectorized operations
    r = (start_color[0] + (end_color[0] - start_color[0]) * y).astype(np.uint8)
    g = (start_color[1] + (end_color[1] - start_color[1]) * y).astype(np.uint8)
    b = (start_color[2] + (end_color[2] - start_color[2]) * y).astype(np.uint8)
    
    # Stack r, g, b channels together
    gradient = np.stack([r, g, b], axis=-1)
    
    # Convert to PIL Image
    gradient = np.transpose(gradient, (1, 0, 2))
    gradient_image = Image.fromarray(gradient)
    
    return gradient_image


# +
# Read the image from the clipboard
image = get_image_from_clipboard()

# Add rounded corners
radius = int(image.width*0.05)  # Adjust the radius as needed
if radius > 15:
    radius = 15
rounded_image = add_rounded_corners(image, radius)

# Define the size of the background larger than the image
padding = min(10, int(rounded_image.width*0.05))  # Adjust the padding as needed
background_size = (
    rounded_image.width + 2 * padding,
    rounded_image.height + 2 * padding,
)

# Create a gradient background
start_color = (102, 42, 197)  # White
end_color = (238, 61, 165)  # Blue
gradient_background = create_gradient_background(
    background_size, start_color, end_color
)
print('bg', background_size, gradient_background.size)

# Calculate the position to center the image on the background
position = (
    (background_size[0] - rounded_image.width) // 2,
    (background_size[1] - rounded_image.height) // 2,
)

# Combine the rounded image with the gradient background
gradient_background.paste(rounded_image, position, rounded_image)
image_to_clipboard(gradient_background)
