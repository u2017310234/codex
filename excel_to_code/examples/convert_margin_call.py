#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例: 轉換 Margin Call 表格
"""

import sys
from pathlib import Path

# 添加父目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import ExcelToCodeConverter


def main():
    """運行完整的轉換流程"""
    
    # Excel 文件路徑
    excel_file = "/workspaces/RM_Tools/Margin Call.xlsm"
    
    # 創建轉換器
    converter = ExcelToCodeConverter(llm_provider="gemini")
    
    # 執行轉換（不自動生成代碼）
    result = converter.convert(
        excel_file=excel_file,
        output_file="output/generated_code/margin_call.py",
        generate_code=False  # 改為 True 需要配置 API key
    )
    
    print("\n" + "=" * 80)
    print("📊 轉換結果摘要")
    print("=" * 80)
    
    context = result['context']
    print(f"工作表: {len(context['workbook_structure']['sheet_names'])} 個")
    print(f"儲存格: {len(context['cell_values'])} 個")
    print(f"公式: {len(context['cell_formulas'])} 個")
    print(f"依賴關係: {len(context['dependencies'])} 個")
    print(f"檢測模式: {len(context['patterns'])} 個")
    
    print("\n📁 生成的文件:")
    print(f"  - 上下文: {result['context_file']}")
    print(f"  - Prompt: {result['prompt_file']}")
    
    print("\n💡 使用方式:")
    print(f"  1. 打開 Prompt 文件: {result['prompt_file']}")
    print(f"  2. 複製內容到 Gemini/Claude/ChatGPT")
    print(f"  3. LLM 會生成優雅的 Python 代碼")
    print(f"  4. 將生成的代碼保存並運行測試")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
