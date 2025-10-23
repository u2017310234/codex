#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Prompt 構建器
將提取的上下文格式化成適合 LLM 理解的 Prompt
"""

import json
from pathlib import Path
from typing import Dict, Any, List


class LLMPromptBuilder:
    """為 LLM 構建優化的 Prompt"""
    
    def __init__(self, context: Dict[str, Any]):
        """
        初始化
        
        Args:
            context: 從 ExcelContextExtractor 提取的完整上下文
        """
        self.context = context
        
    def build_prompt(self, focus: str = "full") -> str:
        """
        構建 LLM Prompt
        
        Args:
            focus: 焦點模式
                - "full": 完整轉換
                - "formulas": 只關注公式邏輯
                - "vba": 只關注 VBA 邏輯
                - "optimization": 關注性能優化
        
        Returns:
            完整的 Prompt 字符串
        """
        if focus == "full":
            return self._build_full_prompt()
        elif focus == "formulas":
            return self._build_formula_focused_prompt()
        elif focus == "vba":
            return self._build_vba_focused_prompt()
        elif focus == "optimization":
            return self._build_optimization_prompt()
        else:
            return self._build_full_prompt()
    
    def _build_full_prompt(self) -> str:
        """構建完整的轉換 Prompt"""
        sections = []
        
        # 1. 角色定義
        sections.append(self._get_role_definition())
        
        # 2. 任務描述
        sections.append(self._get_task_description())
        
        # 3. Excel 工作簿概覽
        sections.append(self._get_workbook_overview())
        
        # 4. 業務邏輯分析
        sections.append(self._get_business_logic_hints())
        
        # 5. 數據流程
        sections.append(self._get_data_flow_description())
        
        # 6. 公式詳情
        sections.append(self._get_formulas_detail())
        
        # 7. 重複模式（循環）
        sections.append(self._get_patterns_description())
        
        # 8. VBA 代碼
        if self.context["vba_code"]["has_vba"]:
            sections.append(self._get_vba_description())
        
        # 9. 依賴關係
        sections.append(self._get_dependencies_summary())
        
        # 10. 輸出要求
        sections.append(self._get_output_requirements())
        
        # 11. 代碼風格要求
        sections.append(self._get_code_style_requirements())
        
        # 12. 驗證要求
        sections.append(self._get_validation_requirements())
        
        return "\n\n".join(sections)
    
    def _get_role_definition(self) -> str:
        """角色定義"""
        return """# 角色定義

你是一位資深的金融工程師和 Python 專家，精通：
- 金融建模與風險管理
- Excel 複雜公式與 VBA
- Python 數據科學生態（NumPy, Pandas, SciPy）
- 軟體工程最佳實踐（設計模式、測試驅動開發）

你的任務是將 Excel 手工報表轉換為生產級的 Python 代碼。"""
    
    def _get_task_description(self) -> str:
        """任務描述"""
        return f"""# 任務描述

將以下 Excel 工作簿轉換為優雅的 Python 代碼：

**檔案**: {self.context['metadata']['filename']}
**作者**: {self.context['metadata'].get('author', 'Unknown')}
**最後修改**: {self.context['metadata'].get('modified', 'Unknown')}

**目標**:
1. 理解業務邏輯（不是機械轉換公式）
2. 識別計算模型類型（例如：期權定價、風險計算等）
3. 生成可維護、可測試的 Python 類
4. 優化重複計算（向量化、緩存）
5. 保持計算結果與 Excel 完全一致"""
    
    def _get_workbook_overview(self) -> str:
        """工作簿概覽"""
        structure = self.context['workbook_structure']
        cell_values = self.context['cell_values']
        formulas = self.context['cell_formulas']
        
        # 統計公式複雜度
        complexity_count = {"low": 0, "medium": 0, "high": 0}
        for formula_info in formulas.values():
            complexity_count[formula_info['complexity']] += 1
        
        return f"""# Excel 工作簿概覽

## 基本信息
- **工作表數量**: {structure['sheet_count']}
- **工作表名稱**: {', '.join(structure['sheet_names'])}
- **總儲存格數**: {len(cell_values)}
- **公式數量**: {len(formulas)}
- **包含 VBA**: {'是' if structure['has_vba'] else '否'}

## 公式複雜度分佈
- **簡單**: {complexity_count['low']} 個
- **中等**: {complexity_count['medium']} 個
- **複雜**: {complexity_count['high']} 個"""
    
    def _get_business_logic_hints(self) -> str:
        """業務邏輯提示"""
        formulas = self.context['cell_formulas']
        
        # 分析使用的函數，推測業務類型
        all_functions = set()
        for formula_info in formulas.values():
            all_functions.update(formula_info['used_functions'])
        
        business_hints = []
        
        if any(f in all_functions for f in ['NORMSDIST', 'NORMDIST', 'LN', 'EXP']):
            business_hints.append("- 可能涉及 **期權定價**（Black-Scholes 模型）")
        
        if any(f in all_functions for f in ['STDEV', 'VAR', 'SQRT']):
            business_hints.append("- 可能涉及 **風險度量**（波動率、標準差）")
        
        if any(f in all_functions for f in ['NPV', 'IRR', 'PMT', 'PV', 'FV']):
            business_hints.append("- 可能涉及 **財務分析**（現金流折現）")
        
        if any(f in all_functions for f in ['VLOOKUP', 'HLOOKUP', 'INDEX', 'MATCH']):
            business_hints.append("- 使用 **查找函數**（建議用 Pandas merge/join）")
        
        hints_text = "\n".join(business_hints) if business_hints else "- 無明顯業務邏輯特徵"
        
        return f"""# 業務邏輯分析

基於使用的 Excel 函數，推測可能的業務場景：

{hints_text}

**使用的主要函數**: {', '.join(sorted(all_functions)[:15])}"""
    
    def _get_data_flow_description(self) -> str:
        """數據流程描述"""
        data_flow = self.context['data_flow']
        
        flow_text = []
        for stage in data_flow:
            cells_preview = ', '.join(stage['cells'][:5])
            if len(stage['cells']) > 5:
                cells_preview += f" ... (共 {stage['count']} 個)"
            
            flow_text.append(f"**階段 {stage['stage']}: {stage['description']}** ({stage['count']} 個儲存格)")
            flow_text.append(f"  - 示例: {cells_preview}")
        
        return f"""# 數據流程

{chr(10).join(flow_text)}

**建議**:
- 輸入參數應作為類的構造函數參數或 setter 方法
- 中間計算可以是私有方法或屬性（使用 @property 或 @cached_property）
- 輸出結果應作為公開方法或屬性"""
    
    def _get_formulas_detail(self) -> str:
        """公式詳情"""
        formulas = self.context['cell_formulas']
        
        # 選擇最複雜的公式展示
        sorted_formulas = sorted(
            formulas.items(),
            key=lambda x: (x[1]['complexity'] != 'high', -x[1]['length'])
        )[:10]
        
        formula_details = []
        for cell_ref, formula_info in sorted_formulas:
            formula_details.append(f"### {cell_ref}")
            formula_details.append(f"```excel")
            formula_details.append(formula_info['raw_formula'])
            formula_details.append(f"```")
            formula_details.append(f"- **依賴**: {', '.join(formula_info['depends_on'][:5])}")
            formula_details.append(f"- **函數**: {', '.join(formula_info['used_functions'])}")
            formula_details.append(f"- **複雜度**: {formula_info['complexity']}")
            formula_details.append("")
        
        return f"""# 關鍵公式詳情

以下是最重要/複雜的公式（前 10 個）：

{chr(10).join(formula_details)}

**完整公式列表**: 共 {len(formulas)} 個公式（已省略部分簡單公式）"""
    
    def _get_patterns_description(self) -> str:
        """重複模式描述"""
        patterns = self.context['patterns']
        
        if not patterns:
            return """# 重複模式分析

未檢測到明顯的重複模式。所有公式都是獨立計算。"""
        
        pattern_details = []
        for i, pattern in enumerate(patterns, 1):
            pattern_details.append(f"## 模式 {i}: {pattern['description']}")
            pattern_details.append(f"- **類型**: {pattern['type']}")
            pattern_details.append(f"- **範圍**: {pattern['range']}")
            pattern_details.append(f"- **重複次數**: {pattern['count']}")
            pattern_details.append(f"- **公式模板**: `{pattern['formula_template']}`")
            pattern_details.append(f"- **建議**: 這是一個循環結構，應該用 Pandas 的向量化操作代替逐行計算")
            pattern_details.append("")
        
        return f"""# 重複模式分析

檢測到 {len(patterns)} 個重複模式（循環結構）：

{chr(10).join(pattern_details)}

**重要提示**: 
- Excel 中多行重複相同公式 = Python 中的向量化操作
- 使用 `df['column'] = expression` 代替 for 循環
- 可以提升性能 10-100 倍"""
    
    def _get_vba_description(self) -> str:
        """VBA 描述"""
        vba = self.context['vba_code']
        
        return f"""# VBA 代碼

**包含 VBA**: {'是' if vba['has_vba'] else '否'}

{vba.get('note', '')}

**建議**:
- 將 VBA 的業務邏輯整合到 Python 類的方法中
- VBA 的 Sub/Function 可以轉換為 Python 方法
- 注意 VBA 可能修改的儲存格（副作用）"""
    
    def _get_dependencies_summary(self) -> str:
        """依賴關係摘要"""
        dependencies = self.context['dependencies']
        calc_order = self.context['calculation_order']
        
        # 找出核心節點（被多個儲存格依賴）
        dep_count = {}
        for cell, info in dependencies.items():
            dep_count[cell] = len(info.get('depended_by', []))
        
        top_dependencies = sorted(dep_count.items(), key=lambda x: -x[1])[:5]
        
        dep_details = []
        for cell, count in top_dependencies:
            if count > 0:
                dep_details.append(f"- **{cell}**: 被 {count} 個儲存格依賴")
        
        return f"""# 依賴關係分析

## 計算順序
共 {len(calc_order)} 個計算步驟（已按依賴順序排列）

**前 10 步**:
{', '.join(calc_order[:10])}

## 核心節點（被多次引用）
{chr(10).join(dep_details) if dep_details else '無明顯核心節點'}

**建議**:
- 按照計算順序組織代碼邏輯
- 核心節點應該用 `@cached_property` 緩存結果"""
    
    def _get_output_requirements(self) -> str:
        """輸出要求"""
        return """# 輸出要求

請生成以下內容：

## 1. Python 類定義

```python
class [ModelName]:
    \"\"\"
    描述這個模型的業務含義
    
    原始來源: Excel 工作簿 [filename]
    \"\"\"
    
    def __init__(self, ...):
        \"\"\"初始化輸入參數\"\"\"
        pass
    
    @property
    def result(self):
        \"\"\"主要計算結果\"\"\"
        pass
```

## 2. 關鍵方法

為每個重要的計算步驟創建方法，附上清晰的 docstring。

## 3. 單元測試

```python
def test_against_excel():
    \"\"\"使用 Excel 的實際值驗證結果\"\"\"
    model = [ModelName](...)
    assert np.isclose(model.result, [excel_value], rtol=1e-5)
```

## 4. 使用示例

展示如何使用這個類。"""
    
    def _get_code_style_requirements(self) -> str:
        """代碼風格要求"""
        return """# 代碼風格要求

1. **命名規範**
   - 類名: PascalCase (如 `BlackScholesModel`)
   - 方法名: snake_case (如 `calculate_volatility`)
   - 常數: UPPER_CASE (如 `TRADING_DAYS_PER_YEAR`)
   - 變數名要有業務含義，不要用 `cell_i31` 這種

2. **類型提示**
   - 所有公開方法都要有類型提示
   - 使用 `from typing import ...`

3. **文檔字符串**
   - 每個類、方法都要有 docstring
   - 說明業務含義，不只是技術實現

4. **錯誤處理**
   - 驗證輸入參數的合理性
   - 使用自定義異常類

5. **性能優化**
   - 優先使用 NumPy/Pandas 的向量化操作
   - 避免 Python for 循環
   - 使用 `@cached_property` 緩存計算結果

6. **可測試性**
   - 避免全局狀態
   - 依賴注入而非硬編碼
   - 每個方法只做一件事"""
    
    def _get_validation_requirements(self) -> str:
        """驗證要求"""
        # 提取一些實際的儲存格值作為測試用例
        cell_values = self.context['cell_values']
        formulas = self.context['cell_formulas']
        
        # 選擇一些有公式的儲存格作為驗證點
        validation_cells = []
        for cell_ref in list(formulas.keys())[:5]:
            if cell_ref in cell_values:
                validation_cells.append({
                    "cell": cell_ref,
                    "formula": formulas[cell_ref]['raw_formula'],
                })
        
        validation_examples = []
        for vc in validation_cells:
            validation_examples.append(f"- **{vc['cell']}**: `{vc['formula'][:60]}...`")
        
        return f"""# 驗證要求

生成的 Python 代碼必須產生與 Excel 完全一致的結果。

## 關鍵驗證點

以下儲存格的計算結果必須與 Excel 一致（誤差 < 0.01%）：

{chr(10).join(validation_examples)}

## 測試數據

使用 Excel 中的實際輸入值進行測試，確保：
1. 數值精度一致（建議使用 `np.isclose` 比較浮點數）
2. 邊界情況處理正確
3. 錯誤情況有適當的異常處理

## 性能要求

- 單次計算應在 < 100ms 內完成
- 批量計算應使用向量化，支持 10000+ 行數據"""
    
    def _build_formula_focused_prompt(self) -> str:
        """構建公式重點 Prompt"""
        # 簡化版，只關注公式轉換
        sections = [
            self._get_role_definition(),
            "# 任務: 將以下 Excel 公式轉換為 Python 表達式\n",
            self._get_formulas_detail(),
            self._get_output_requirements(),
        ]
        return "\n\n".join(sections)
    
    def _build_vba_focused_prompt(self) -> str:
        """構建 VBA 重點 Prompt"""
        sections = [
            self._get_role_definition(),
            "# 任務: 將 VBA 代碼轉換為 Python\n",
            self._get_vba_description(),
            self._get_output_requirements(),
        ]
        return "\n\n".join(sections)
    
    def _build_optimization_prompt(self) -> str:
        """構建優化重點 Prompt"""
        sections = [
            self._get_role_definition(),
            "# 任務: 優化現有代碼的性能\n",
            self._get_patterns_description(),
            "# 優化建議\n\n使用 NumPy/Pandas 向量化操作代替循環。",
        ]
        return "\n\n".join(sections)
    
    def save_prompt(self, output_file: str, focus: str = "full"):
        """保存 Prompt 到文件"""
        prompt = self.build_prompt(focus)
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        print(f"✅ Prompt 已保存: {output_path}")
        return prompt


def main():
    """示範用法"""
    # 加載之前提取的上下文
    context_file = "/workspaces/RM_Tools/excel_to_code/output/contexts/margin_call_context.json"
    
    with open(context_file, 'r', encoding='utf-8') as f:
        context = json.load(f)
    
    # 構建 Prompt
    builder = LLMPromptBuilder(context)
    
    # 保存完整 Prompt
    output_file = "/workspaces/RM_Tools/excel_to_code/output/prompts/margin_call_prompt.md"
    prompt = builder.save_prompt(output_file, focus="full")
    
    print("\n" + "=" * 80)
    print("📝 Prompt 生成完成")
    print("=" * 80)
    print(f"長度: {len(prompt)} 字符")
    print(f"檔案: {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    main()
