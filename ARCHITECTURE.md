# 代码架构图

## 重构后的模块结构

```
Alfred工作流/
├── 核心模块/
│   ├── image_processor.py          # 图像处理基类
│   │   ├── ImageProcessor (ABC)    # 抽象基类
│   │   └── ImageUtils              # 工具函数类
│   ├── config.py                   # 配置管理
│   │   ├── BeautifyConfig          # 美化配置
│   │   ├── TornEdgeConfig          # 撕裂边缘配置
│   │   └── WorkflowConfig          # 工作流配置
│   └── utils.py                    # 通用工具函数
├── 处理器/
│   ├── beautify_processor.py       # 美化截图处理器
│   │   └── BeautifyProcessor       # 继承自ImageProcessor
│   └── torn_edge_processor.py      # 撕裂边缘处理器
│       └── TornEdgeProcessor       # 继承自ImageProcessor
├── 主程序/
│   ├── beautify_screenshot.py      # 美化截图入口
│   └── torn_edge.py               # 撕裂边缘入口
└── 资源文件/
    ├── base.png                    # 撕裂边缘源图像
    └── info.plist                  # Alfred配置
```

## 类关系图

```
ImageProcessor (抽象基类)
├── get_image_from_clipboard()
├── image_to_clipboard()
├── run()
└── process_image() [抽象方法]

BeautifyProcessor (继承自ImageProcessor)
├── process_image() [实现]
└── 使用BeautifyConfig配置

TornEdgeProcessor (继承自ImageProcessor)
├── process_image() [实现]
├── extract_and_apply_torn_edge()
└── 使用TornEdgeConfig配置

ImageUtils (工具类)
├── add_rounded_corners()
├── create_gradient_background()
├── calculate_radius()
└── calculate_padding()
```

## 数据流

```
用户操作 → Alfred工作流 → 主程序 → 处理器 → 基类方法
    ↓
剪贴板图像 → 图像处理 → 结果图像 → 剪贴板输出
    ↓
配置参数 → 处理逻辑 → 通知用户
```

## 重构优势

1. **代码复用**: 基类消除了重复的剪贴板操作代码
2. **模块化**: 每个功能独立，易于维护和扩展
3. **配置化**: 参数集中管理，易于调整
4. **错误处理**: 统一的异常处理机制
5. **可测试性**: 清晰的类结构便于单元测试
6. **可扩展性**: 新增功能只需继承基类并实现process_image方法
