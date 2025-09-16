"""
主程序
使用重构后的模块化代码
"""
import os, sys

from processors.beautify_processor import BeautifyProcessor
from processors.torn_edge_processor import TornEdgeProcessor
from processors.whitebg_processor import WhiteBGProcessor
from argparse import ArgumentParser


if __name__ == "__main__":
    
    parser = ArgumentParser(description="美化截图处理器")
    parser.add_argument("action", help="clipboard or file", choices=["beautify", "torn_edge", "whitebg"])
    parser.add_argument("source", help="clipboard or file", choices=["clipboard", "file"])
    args = parser.parse_args()
        
    print("Action:", args.action, file=sys.stderr)
    print("Source:", args.source, file=sys.stderr)

    if args.action == "beautify":
        processor = BeautifyProcessor()
    elif args.action == "torn_edge":
        processor = TornEdgeProcessor()
    elif args.action == "whitebg":
        processor = WhiteBGProcessor()


    if args.source == "file":
        file_paths = os.environ["files"]
        print("File paths:", file_paths, file=sys.stderr)
        for file_path in file_paths.split("\t"):
            processor.process_image_file(file_path)
    elif args.source == "clipboard":
        processor.run()
        
