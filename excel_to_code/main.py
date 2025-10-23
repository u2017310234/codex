#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel to Code - 主程序入口
"""

import argparse
from pathlib import Path
import sys

# 添加當前目錄到路徑
sys.path.insert(0, str(Path(__file__).parent))

from extractors.context_extractor import ExcelContextExtractor
from formatters.llm_prompt_builder import LLMPromptBuilder
import config


class ExcelToCodeConverter:
    """Excel 到 Python 代碼的完整轉換器"""
    
    def __init__(self, llm_provider: str = None):
        """
        初始化轉換器
        
        Args:
            llm_provider: LLM 提供商 (gemini, anthropic, openai)
        """
        self.llm_provider = llm_provider or config.LLM_PROVIDER
        self.context = None
        self.prompt = None
        self.generated_code = None
        
    def convert(self, excel_file: str, output_file: str = None, 
                generate_code: bool = False) -> dict:
        """
        轉換 Excel 文件
        
        Args:
            excel_file: Excel 文件路徑
            output_file: 輸出的 Python 文件路徑
            generate_code: 是否調用 LLM 生成代碼（需要 API key）
        
        Returns:
            包含所有結果的字典
        """
        print("=" * 80)
        print("🚀 Excel to Code - 智能報表轉換系統")
        print("=" * 80)
        print()
        
        # Step 1: 提取上下文
        print("📊 步驟 1/4: 提取完整上下文...")
        extractor = ExcelContextExtractor(excel_file)
        self.context = extractor.extract_all()
        
        # 保存上下文
        excel_name = Path(excel_file).stem
        context_file = f"{config.CONTEXTS_DIR}/{excel_name}_context.json"
        extractor.save_context(context_file)
        print()
        
        # Step 2: 構建 Prompt
        print("📝 步驟 2/4: 構建 LLM Prompt...")
        builder = LLMPromptBuilder(self.context)
        prompt_file = f"{config.PROMPTS_DIR}/{excel_name}_prompt.md"
        self.prompt = builder.save_prompt(prompt_file, focus="full")
        print()
        
        # Step 3: 生成代碼（可選）
        if generate_code:
            print("🤖 步驟 3/4: 調用 LLM 生成代碼...")
            print("⚠️  此功能需要配置 API key")
            print("提示: 你可以手動將 prompt 複製給 LLM，或配置 config.py 中的 API key")
            print()
            # TODO: 實現 LLM 調用
            self.generated_code = None
        else:
            print("⏭️  步驟 3/4: 跳過代碼生成（使用 --generate 啟用）")
            print()
        
        # Step 4: 驗證（如果有生成的代碼）
        if self.generated_code:
            print("✅ 步驟 4/4: 驗證結果...")
            # TODO: 實現驗證邏輯
        else:
            print("⏭️  步驟 4/4: 跳過驗證（需要先生成代碼）")
        
        print()
        print("=" * 80)
        print("✅ 轉換完成!")
        print("=" * 80)
        print()
        print("📁 輸出文件:")
        print(f"  - 上下文: {context_file}")
        print(f"  - Prompt: {prompt_file}")
        if output_file:
            print(f"  - 代碼: {output_file}")
        print()
        print("💡 下一步:")
        print("  1. 查看生成的 Prompt: ", prompt_file)
        print("  2. 複製 Prompt 內容到 LLM (Gemini, Claude, ChatGPT)")
        print("  3. 或配置 config.py 中的 API key 使用 --generate 自動生成")
        print("=" * 80)
        
        return {
            "context": self.context,
            "prompt": self.prompt,
            "generated_code": self.generated_code,
            "context_file": context_file,
            "prompt_file": prompt_file,
            "output_file": output_file,
        }


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="將 Excel 報表轉換為 Python 代碼",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法（提取上下文 + 生成 Prompt）
  python main.py --input ../Margin_Call.xlsm
  
  # 指定輸出文件
  python main.py --input ../Margin_Call.xlsm --output output/margin_call.py
  
  # 自動生成代碼（需要配置 API key）
  python main.py --input ../Margin_Call.xlsm --generate
  
  # 指定 LLM 提供商
  python main.py --input ../Margin_Call.xlsm --llm gemini --generate
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Excel 輸入文件路徑'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Python 輸出文件路徑（可選）'
    )
    
    parser.add_argument(
        '--generate', '-g',
        action='store_true',
        help='自動調用 LLM 生成代碼（需要配置 API key）'
    )
    
    parser.add_argument(
        '--llm',
        choices=['gemini', 'anthropic', 'openai', 'local'],
        default=config.LLM_PROVIDER,
        help=f'LLM 提供商（默認: {config.LLM_PROVIDER}）'
    )
    
    parser.add_argument(
        '--focus',
        choices=['full', 'formulas', 'vba', 'optimization'],
        default='full',
        help='轉換焦點（默認: full）'
    )
    
    args = parser.parse_args()
    
    # 檢查輸入文件
    input_file = Path(args.input)
    if not input_file.exists():
        print(f"❌ 錯誤: 文件不存在: {input_file}")
        sys.exit(1)
    
    # 執行轉換
    converter = ExcelToCodeConverter(llm_provider=args.llm)
    result = converter.convert(
        excel_file=str(input_file),
        output_file=args.output,
        generate_code=args.generate
    )
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
