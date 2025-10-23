#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简单的使用示例
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from extractors.excel_parser import ExcelContextExtractor


def main():
    # 1. 指定 Excel 文件
    excel_file = "../../Margin Call.xlsm"
    
    if not Path(excel_file).exists():
        print(f"❌ 文件不存在: {excel_file}")
        print("💡 请修改 excel_file 变量为你的文件路径")
        return
    
    print(f"🔍 正在解析: {excel_file}\n")
    
    # 2. 创建解析器并提取
    parser = ExcelContextExtractor(excel_file)
    context = parser.extract_all()
    
    print(f"✅ 提取完成！\n")
    
    # 3. 保存为 JSON
    output_file = "output/simple_output.json"
    parser.save_context(output_file)
    
    print(f"💾 已保存到: {output_file}\n")
    
    # 4. 快速查看结果
    print("📊 提取摘要:")
    print(f"  - 包含格式: {len(context)} 种")
    
    # 查看 compact_view
    compact = context.get('compact_view', {})
    if compact:
        print(f"\n  📋 工作表概览:")
        for sheet_name, info in compact.items():
            dims = info.get('dimensions', {})
            summary = info.get('formula_summary', {})
            print(f"    • {sheet_name}: {dims.get('rows')}行 x {dims.get('cols')}列, {summary.get('total')}个公式")
    
    # 查看 VBA
    vba = context.get('vba_code', {})
    if vba and vba.get('has_vba'):
        summary = vba.get('summary', {})
        print(f"\n  💻 VBA 代码:")
        print(f"    • 模块数: {summary.get('module_count')}")
        print(f"    • 代码行数: {summary.get('total_lines')}")
        print(f"    • 过程: {', '.join(summary.get('procedures', []))}")
    
    print(f"\n✅ 完成！现在可以:")
    print(f"  1. 查看 {output_file}")
    print(f"  2. 运行第二阶段: cd ../../excel_to_code && python main.py --input ../{output_file}")


if __name__ == '__main__':
    main()
