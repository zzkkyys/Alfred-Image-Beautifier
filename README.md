
这是一个Alfred workflow，用于美化剪贴板中的截图和图像。

## 功能特性

### 支持的图片处理

1. **美化图片** - 为截图添加圆角和渐变背景
2. **撕裂边缘效果** - 为图像添加撕裂边缘特效
3. **白色背景** - 将透明背景图像转换为白色背景

### 输入方式

- 支持从剪贴板获取图像
   - 使用截图工具截图后自动复制到剪贴板
   - 直接在`Finder`中复制图像文件到剪贴板
- 支持通过Alfred universal actions处理文件
   - 在`Finder`中选取一个或多个图像文件，使用Alfred universal action快捷键唤起窗口，搜索本workflow命令，进行处理



## 使用方法




## 配置选项

### 美化截图配置
- `radius_ratio`: 圆角半径比例 (默认: 0.05)
- `max_radius`: 最大圆角半径 (默认: 15)
- `padding_ratio`: 内边距比例 (默认: 0.05)
- `max_padding`: 最大内边距 (默认: 10)
- `start_color`: 渐变起始颜色 (默认: (102, 42, 197))
- `end_color`: 渐变结束颜色 (默认: (238, 61, 165))

### 撕裂边缘配置
- `thickness`: 边缘厚度 (默认: 80)
- `edge`: 应用边缘 ('top', 'bottom', 'left', 'right', 'all')
- `source_image_path`: 源图像文件路径 (默认: "base.png")

