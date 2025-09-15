# 图像美化工作流 - 重构版本

这是一个Alfred工作流，用于美化剪贴板中的截图和图像。

## 功能特性

1. **美化截图** - 为截图添加圆角和渐变背景
2. **撕裂边缘效果** - 为图像添加撕裂边缘特效

## 重构后的代码结构

### 核心模块

- `image_processor.py` - 图像处理基类和工具函数
- `config.py` - 配置管理模块
- `beautify_processor.py` - 美化截图处理器
- `torn_edge_processor.py` - 撕裂边缘处理器
- `utils.py` - 通用工具函数

### 主程序

- `beautify_screenshot.py` - 美化截图主程序
- `torn_edge.py` - 撕裂边缘主程序

## 重构改进

### 1. 消除代码重复
- 创建了`ImageProcessor`基类，统一了剪贴板操作和错误处理
- 提取了通用的图像处理工具函数到`ImageUtils`类

### 2. 模块化设计
- 每个功能都有独立的处理器类
- 配置参数集中管理
- 清晰的职责分离

### 3. 配置管理
- 使用`@dataclass`定义配置结构
- 支持灵活的参数调整
- 集中管理所有配置项

### 4. 错误处理
- 统一的异常处理机制
- 友好的错误提示
- 完善的日志记录

### 5. 代码可读性
- 清晰的函数命名和文档
- 合理的代码组织结构
- 类型提示支持

## 使用方法

### Alfred工作流
1. 复制图像到剪贴板
2. 使用Alfred快捷键调用：
   - `Beautify screenshot` - 美化截图
   - `torn screenshot` - 添加撕裂边缘

### 直接运行
```bash
python beautify_screenshot.py
python torn_edge.py
```

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

## 依赖项

- Python 3.7+
- Pillow (PIL)
- numpy
- Cocoa (macOS)

## 文件说明

- `base.png` - 撕裂边缘效果的源图像文件
- `info.plist` - Alfred工作流配置文件
- `__pycache__/` - Python字节码缓存目录
