"""
美化截图主程序
使用重构后的模块化代码
"""

from beautify_processor import main
from argparse import ArgumentParser


if __name__ == "__main__":
    
    parser = ArgumentParser(description="美化截图处理器")
    parser.add_argument("source", help="clipboard or file", choices=["clipboard", "file"])
    args = parser.parse_args()

    if args.source:
        main(args.source)
