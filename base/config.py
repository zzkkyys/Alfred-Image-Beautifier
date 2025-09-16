"""
配置管理模块
集中管理所有配置参数
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class BeautifyConfig:
    """美化截图配置"""

    # 圆角配置
    radius_ratio: float = 0.05  # 圆角半径比例
    max_radius: int = 15  # 最大圆角半径

    # 内边距配置
    padding_ratio: float = 0.05  # 内边距比例
    max_padding: int = 10  # 最大内边距

    # 渐变背景配置
    start_color: Tuple[int, int, int] = (102, 42, 197)  # 起始颜色
    end_color: Tuple[int, int, int] = (238, 61, 165)  # 结束颜色


@dataclass
class TornEdgeConfig:
    """撕裂边缘配置"""

    # 边缘厚度
    thickness: int = 80

    # 应用边缘
    edge: str = "all"  # 'top', 'bottom', 'left', 'right', 'all'

    # 源图像文件路径
    source_image_path: str = "base.png"


@dataclass
class WorkflowConfig:
    """工作流配置"""

    beautify: BeautifyConfig = field(default_factory=BeautifyConfig)
    torn_edge: TornEdgeConfig = field(default_factory=TornEdgeConfig)

    # 工作流名称
    beautify_workflow_name: str = "Beautify Screenshot"
    torn_edge_workflow_name: str = "Torn Edge Effect"


# 全局配置实例
config = WorkflowConfig()
