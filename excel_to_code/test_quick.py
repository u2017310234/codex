#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速測試腳本
"""

import sys
import os
from pathlib import Path

# 確保可以導入模組
sys.path.insert(0, str(Path(__file__).parent))

# 創建輸出目錄
os.makedirs('output/contexts', exist_ok=True)
os.makedirs('output/prompts', exist_ok=True)

print("=" * 80)
print("測試 Excel to Code 系統")
print("=" * 80)
print()

# 測試 1: 上下文提取
print("✅ 測試 1: 上下文提取")
try:
    from extractors.context_extractor import ExcelContextExtractor
    
    excel_file = "../Margin Call.xlsm"
    print(f"   提取文件: {excel_file}")
    
    extractor = ExcelContextExtractor(excel_file)
    context = extractor.extract_all()
    
    output_file = "output/contexts/margin_call_context.json"
    extractor.save_context(output_file)
    
    print(f"   ✓ 成功提取 {len(context['cell_formulas'])} 個公式")
    print(f"   ✓ 檢測到 {len(context['patterns'])} 個模式")
    print()
    
except Exception as e:
    print(f"   ✗ 失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 測試 2: Prompt 生成
print("✅ 測試 2: Prompt 生成")
try:
    from formatters.llm_prompt_builder import LLMPromptBuilder
    
    builder = LLMPromptBuilder(context)
    prompt_file = "output/prompts/margin_call_prompt.md"
    prompt = builder.save_prompt(prompt_file, focus="full")
    
    print(f"   ✓ 成功生成 Prompt ({len(prompt)} 字符)")
    print()
    
except Exception as e:
    print(f"   ✗ 失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 80)
print("✅ 所有測試通過!")
print("=" * 80)
print()
print("📁 生成的文件:")
print(f"   - {output_file}")
print(f"   - {prompt_file}")
print()
print("💡 下一步:")
print(f"   1. 查看 Prompt: cat {prompt_file}")
print(f"   2. 複製到 LLM 生成代碼")
print("=" * 80)
