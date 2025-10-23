#!/usr/bin/env python3
"""命令行工具"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from extractors.excel_parser import ExcelContextExtractor


def main():
    parser = argparse.ArgumentParser(description='Excel Parser - 机械化提取')
    parser.add_argument('--input', '-i', required=True, help='Excel 文件路径')
    parser.add_argument('--output', '-o', help='输出 JSON 路径（可选）')
    
    args = parser.parse_args()
    
    # 解析
    extractor = ExcelContextExtractor(args.input)
    context = extractor.extract_all()
    
    # 保存
    if args.output:
        output_path = args.output
    else:
        input_path = Path(args.input)
        output_path = f"output/{input_path.stem}.json"
    
    extractor.save_context(output_path)
    
    print(f"\n✅ 完成! 输出: {output_path}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
