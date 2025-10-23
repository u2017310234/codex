#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整演示：从 Excel 文件到代码生成的完整工作流
展示如何使用 ExcelParser 提取并利用各种格式
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from extractors.excel_parser import ExcelContextExtractor
import json
import pandas as pd
from collections import defaultdict
import re


def demo_1_basic_extraction():
    """演示 1: 基本提取流程"""
    print("=" * 80)
    print("📝 演示 1: 从 Excel 文件提取所有格式")
    print("=" * 80)
    
    # 使用示例文件
    excel_file = "../../Margin Call.xlsm"
    
    if not Path(excel_file).exists():
        print(f"❌ 示例文件不存在: {excel_file}")
        print("💡 请将你的 Excel 文件放在项目根目录，或修改路径")
        return None
    
    print(f"\n🔍 正在解析: {excel_file}")
    
    # 创建解析器
    parser = ExcelContextExtractor(excel_file)
    
    # 提取所有上下文
    context = parser.extract_all()
    
    print(f"\n✅ 提取完成！")
    print(f"\n📊 提取的格式:")
    for key in context.keys():
        if key == 'metadata':
            continue
        print(f"  ✓ {key}")
    
    # 显示元数据
    metadata = context.get('metadata', {})
    print(f"\n📋 元数据:")
    print(f"  - 工作簿: {metadata.get('workbook_name')}")
    print(f"  - 工作表数: {metadata.get('sheet_count')}")
    print(f"  - 工作表列表: {', '.join(metadata.get('sheet_names', []))}")
    print(f"  - 是否含 VBA: {metadata.get('has_vba')}")
    
    return context


def demo_2_tables_by_row(context):
    """演示 2: 使用 tables_by_row 进行数据分析"""
    if not context:
        return
    
    print("\n" + "=" * 80)
    print("📊 演示 2: 使用 tables_by_row 进行数据分析")
    print("=" * 80)
    
    tables = context.get('tables_by_row', {})
    
    if not tables:
        print("⚠️  没有找到 tables_by_row 数据")
        return
    
    # 获取第一个工作表
    sheet_name = list(tables.keys())[0]
    table_data = tables[sheet_name]
    
    print(f"\n工作表: {sheet_name}")
    
    # 转换为 DataFrame
    sorted_rows = sorted(table_data.items(), key=lambda x: int(x[0].split('_')[1]))
    df_data = [row[1] for row in sorted_rows]
    df = pd.DataFrame(df_data)
    
    print(f"\n✓ DataFrame 形状: {df.shape[0]} 行 x {df.shape[1]} 列")
    
    # 显示前几行
    print(f"\n前 5 行数据:")
    print(df.head())
    
    # 数据分析
    print(f"\n📈 数据统计:")
    print(f"  - 总单元格: {df.shape[0] * df.shape[1]}")
    print(f"  - 非空单元格: {df.count().sum()}")
    print(f"  - 空单元格: {df.isna().sum().sum()}")
    
    # 检测数值列
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        print(f"\n  - 数值列: {len(numeric_cols)} 个")
        print(f"  - 数值列示例: {list(numeric_cols[:5])}")
    
    return df


def demo_3_formulas_by_column(context):
    """演示 3: 使用 formulas_by_column 分析公式逻辑"""
    if not context:
        return
    
    print("\n" + "=" * 80)
    print("🔍 演示 3: 使用 formulas_by_column 分析公式逻辑")
    print("=" * 80)
    
    formulas_by_col = context.get('formulas_by_column', {})
    
    if not formulas_by_col:
        print("⚠️  没有找到 formulas_by_column 数据")
        return
    
    # 获取第一个工作表
    sheet_name = list(formulas_by_col.keys())[0]
    columns = formulas_by_col[sheet_name]
    
    print(f"\n工作表: {sheet_name}")
    print(f"列数: {len(columns)}")
    
    # 分析每列
    total_formulas = 0
    total_values = 0
    
    for col in sorted(columns.keys()):
        items = columns[col]
        formulas = [item for item in items if item.get('type') == 'formula']
        values = [item for item in items if item.get('type') != 'formula']
        
        total_formulas += len(formulas)
        total_values += len(values)
        
        if formulas or values:
            print(f"\n列 {col}:")
            if values and values[0]['row'] == 1:
                print(f"  表头: {values[0]['value']}")
            if formulas:
                print(f"  公式数: {len(formulas)}")
                print(f"  首个公式: 行{formulas[0]['row']} = {formulas[0]['value']}")
            if values:
                print(f"  常量值: {len(values)} 个")
    
    print(f"\n📊 总计:")
    print(f"  - 总公式: {total_formulas}")
    print(f"  - 总常量: {total_values}")


def demo_4_compact_view(context):
    """演示 4: 使用 compact_view 快速预览"""
    if not context:
        return
    
    print("\n" + "=" * 80)
    print("👁️  演示 4: 使用 compact_view 快速预览")
    print("=" * 80)
    
    compact = context.get('compact_view', {})
    
    if not compact:
        print("⚠️  没有找到 compact_view 数据")
        return
    
    for sheet_name, info in compact.items():
        print(f"\n工作表: {sheet_name}")
        
        dims = info.get('dimensions', {})
        print(f"  规模: {dims.get('rows')} 行 x {dims.get('cols')} 列")
        
        summary = info.get('formula_summary', {})
        print(f"  公式数量: {summary.get('total')}")
        print(f"  唯一模式: {summary.get('unique_patterns')}")
        print(f"  公式分布: {summary.get('by_column')}")
        
        # 显示表头
        header = info.get('header', [])
        if header:
            print(f"  表头 (前10列): {', '.join(str(h) for h in header[:10])}")
        
        # 显示样本行
        sample_rows = info.get('sample_rows', [])
        if sample_rows:
            print(f"\n  前 3 行样本:")
            for idx, row in enumerate(sample_rows[:3], 1):
                row_preview = [str(cell)[:20] if cell is not None else 'None' 
                               for cell in row[:8]]
                print(f"    Row {idx}: {row_preview}")


def demo_5_vba_code(context):
    """演示 5: 提取 VBA 代码"""
    if not context:
        return
    
    print("\n" + "=" * 80)
    print("💻 演示 5: VBA 代码提取")
    print("=" * 80)
    
    vba = context.get('vba_code', {})
    
    if not vba or not vba.get('has_vba'):
        print("⚠️  该文件不包含 VBA 代码")
        return
    
    summary = vba.get('summary', {})
    print(f"\n📊 VBA 统计:")
    print(f"  - 模块数: {summary.get('module_count')}")
    print(f"  - 总代码行: {summary.get('total_lines')}")
    print(f"  - 过程数: {summary.get('procedure_count')}")
    
    procedures = summary.get('procedures', [])
    if procedures:
        print(f"  - 过程列表: {', '.join(procedures)}")
    
    # 显示模块详情
    modules = vba.get('modules', [])
    for mod in modules:
        print(f"\n模块: {mod.get('filename')}")
        print(f"  代码长度: {mod.get('code_length')} 字符")
        print(f"  包含过程: {', '.join(mod.get('procedures', []))}")
        
        # 显示代码片段
        code = mod.get('code', '')
        if code:
            lines = code.split('\n')[:10]
            print(f"\n  代码预览 (前10行):")
            for line in lines:
                print(f"    {line}")


def demo_6_formula_patterns(context):
    """演示 6: 分析公式模式"""
    if not context:
        return
    
    print("\n" + "=" * 80)
    print("🔬 演示 6: 公式模式分析")
    print("=" * 80)
    
    formulas_by_col = context.get('formulas_by_column', {})
    
    if not formulas_by_col:
        print("⚠️  没有找到公式数据")
        return
    
    # 提取所有公式模式
    patterns = defaultdict(list)
    
    for sheet_name, columns in formulas_by_col.items():
        for col, items in columns.items():
            for item in items:
                if item.get('type') == 'formula':
                    # 提取模式（数字替换为 N）
                    pattern = re.sub(r'\d+', 'N', item['value'])
                    patterns[pattern].append({
                        "sheet": sheet_name,
                        "col": col,
                        "row": item['row'],
                        "formula": item['value']
                    })
    
    print(f"\n发现 {len(patterns)} 种公式模式")
    
    # 显示重复的模式
    repeated = {p: locs for p, locs in patterns.items() if len(locs) > 1}
    
    if repeated:
        print(f"\n🔁 重复模式 ({len(repeated)} 种):")
        
        for pattern, locations in sorted(repeated.items(), 
                                        key=lambda x: len(x[1]), 
                                        reverse=True)[:5]:
            print(f"\n  模式: {pattern}")
            print(f"  出现: {len(locations)} 次")
            print(f"  示例: {locations[0]['sheet']}!{locations[0]['col']}{locations[0]['row']}")
    else:
        print("\n✓ 所有公式都是唯一的（没有重复模式）")


def demo_7_save_and_load(context):
    """演示 7: 保存和加载 JSON"""
    if not context:
        return
    
    print("\n" + "=" * 80)
    print("💾 演示 7: 保存和加载 JSON")
    print("=" * 80)
    
    output_file = "output/demo_output.json"
    
    # 确保输出目录存在
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    # 保存
    print(f"\n保存到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(context, f, ensure_ascii=False, indent=2)
    
    # 获取文件大小
    file_size = Path(output_file).stat().st_size
    print(f"✓ 文件大小: {file_size:,} 字节 ({file_size/1024:.2f} KB)")
    
    # 重新加载
    print(f"\n从文件加载...")
    with open(output_file, 'r', encoding='utf-8') as f:
        loaded_context = json.load(f)
    
    print(f"✓ 成功加载")
    print(f"✓ 包含格式: {', '.join(loaded_context.keys())}")
    
    return output_file


def demo_8_export_formats(context):
    """演示 8: 导出为不同格式"""
    if not context:
        return
    
    print("\n" + "=" * 80)
    print("📤 演示 8: 导出为不同格式")
    print("=" * 80)
    
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 导出 tables_by_row 为 CSV
    tables = context.get('tables_by_row', {})
    if tables:
        for sheet_name, table_data in tables.items():
            sorted_rows = sorted(table_data.items(), 
                               key=lambda x: int(x[0].split('_')[1]))
            df_data = [row[1] for row in sorted_rows]
            df = pd.DataFrame(df_data)
            
            csv_file = output_dir / f"{sheet_name}_data.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"✓ 导出 CSV: {csv_file}")
    
    # 2. 导出 formulas_by_column 为 JSON
    formulas = context.get('formulas_by_column', {})
    if formulas:
        formulas_file = output_dir / "formulas.json"
        with open(formulas_file, 'w', encoding='utf-8') as f:
            json.dump(formulas, f, ensure_ascii=False, indent=2)
        print(f"✓ 导出公式 JSON: {formulas_file}")
    
    # 3. 导出 compact_view 为 Markdown
    compact = context.get('compact_view', {})
    if compact:
        md_file = output_dir / "overview.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# Excel 工作簿概览\n\n")
            
            for sheet_name, info in compact.items():
                f.write(f"## 工作表: {sheet_name}\n\n")
                
                dims = info.get('dimensions', {})
                f.write(f"- 规模: {dims.get('rows')} 行 x {dims.get('cols')} 列\n")
                
                summary = info.get('formula_summary', {})
                f.write(f"- 公式数量: {summary.get('total')}\n")
                f.write(f"- 唯一模式: {summary.get('unique_patterns')}\n")
                f.write(f"- 公式分布: {summary.get('by_column')}\n\n")
        
        print(f"✓ 导出概览 Markdown: {md_file}")
    
    # 4. 导出 VBA 为 .bas 文件（已在 ExcelParser 中自动完成）
    vba = context.get('vba_code', {})
    if vba and vba.get('has_vba'):
        print(f"✓ VBA 模块已自动保存为 .bas 文件")


def main():
    """主函数"""
    print("\n" + "🎯" * 40)
    print("Excel Parser 完整演示")
    print("从 Excel 文件到各种格式的完整工作流")
    print("🎯" * 40 + "\n")
    
    # 演示 1: 基本提取
    context = demo_1_basic_extraction()
    
    if not context:
        print("\n❌ 提取失败，演示终止")
        return
    
    # 演示 2-8: 使用各种格式
    demo_2_tables_by_row(context)
    demo_3_formulas_by_column(context)
    demo_4_compact_view(context)
    demo_5_vba_code(context)
    demo_6_formula_patterns(context)
    output_file = demo_7_save_and_load(context)
    demo_8_export_formats(context)
    
    # 总结
    print("\n" + "=" * 80)
    print("🎉 演示完成！")
    print("=" * 80)
    print("\n💡 下一步:")
    print("  1. 查看 output/ 目录中的导出文件")
    print("  2. 阅读 FORMAT_GUIDE.md 了解更多格式细节")
    print("  3. 查看 README.md 了解完整 API")
    print("  4. 运行第二阶段 excel_to_code 生成 LLM Prompt")
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
