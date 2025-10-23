#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三层 Agent 架构 - 借鉴图中设计
将提取过程分为：结构分析 → 数据提取 → 语义生成
"""

from typing import Dict, Any, List
import json
from pathlib import Path


class TableAnalyzerAgent:
    """
    Agent 1: 表格结构分析器
    
    职责：
    - 识别表格类型（数据表、计算表、报告模板）
    - 分析表格布局（标题区、输入区、计算区、输出区）
    - 检测数据流向
    """
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析表格结构"""
        print("🔍 Agent 1: 分析表格结构...")
        
        # 识别区域类型
        regions = self._identify_regions(context)
        
        # 分析数据流
        data_flow = self._analyze_data_flow(context)
        
        # 识别表格类型
        table_type = self._classify_table_type(context)
        
        return {
            "table_type": table_type,  # "financial_model", "data_report", "calculation_sheet"
            "regions": regions,
            "data_flow": data_flow,
            "layout_pattern": self._detect_layout_pattern(context),
        }
    
    def _identify_regions(self, context: Dict) -> List[Dict]:
        """识别表格区域"""
        formulas = context.get('cell_formulas', {})
        cell_values = context.get('cell_values', {})
        
        regions = []
        
        # 输入区：没有公式的数值单元格
        input_cells = [
            cell for cell, info in cell_values.items()
            if info['is_input'] and info['type'] == 'number'
        ]
        
        if input_cells:
            regions.append({
                "type": "input",
                "description": "输入参数区",
                "cells": input_cells[:10],  # 示例
                "characteristics": "包含用户可修改的原始数据"
            })
        
        # 计算区：有公式的单元格
        calc_cells = list(formulas.keys())
        if calc_cells:
            regions.append({
                "type": "calculation",
                "description": "计算逻辑区",
                "cells": calc_cells[:10],
                "characteristics": "包含业务计算公式"
            })
        
        # 输出区：被依赖少的公式单元格
        deps = context.get('dependencies', {})
        output_cells = [
            cell for cell in calc_cells
            if len(deps.get(cell, {}).get('depended_by', [])) == 0
        ]
        
        if output_cells:
            regions.append({
                "type": "output",
                "description": "结果输出区",
                "cells": output_cells,
                "characteristics": "最终计算结果，无其他单元格依赖"
            })
        
        return regions
    
    def _analyze_data_flow(self, context: Dict) -> Dict:
        """分析数据流向"""
        calc_order = context.get('calculation_order', [])
        
        # 分层：输入 → 中间层 → 输出
        layers = []
        if len(calc_order) > 0:
            # 简化：按依赖深度分层
            layers = [
                {"level": 0, "description": "数据源", "cells": []},
                {"level": 1, "description": "一级计算", "cells": []},
                {"level": 2, "description": "二级计算", "cells": []},
            ]
        
        return {
            "flow_direction": "top_to_bottom",  # 或 "left_to_right"
            "layers": layers,
            "critical_path": calc_order[:5] if calc_order else [],
        }
    
    def _classify_table_type(self, context: Dict) -> str:
        """分类表格类型"""
        formulas = context.get('cell_formulas', {})
        
        # 基于函数使用判断
        all_functions = set()
        for formula_info in formulas.values():
            all_functions.update(formula_info.get('used_functions', []))
        
        if any(f in all_functions for f in ['NORMSDIST', 'LN', 'EXP']):
            return "financial_model"  # 金融模型
        elif any(f in all_functions for f in ['VLOOKUP', 'INDEX', 'MATCH']):
            return "data_lookup_table"  # 查找表
        elif any(f in all_functions for f in ['SUM', 'AVERAGE', 'COUNT']):
            return "summary_report"  # 汇总报表
        else:
            return "general_calculation"  # 通用计算表
    
    def _detect_layout_pattern(self, context: Dict) -> str:
        """检测布局模式"""
        # 简化：基于单元格分布
        return "vertical_flow"  # 或 "horizontal_flow", "matrix"


class DataExtractorAgent:
    """
    Agent 2: 数据结构化提取器
    
    职责：
    - 将原始数据转为结构化 JSON
    - 标注每个字段的语义
    - 提取关键业务实体
    """
    
    def extract(self, context: Dict[str, Any], 
                structure_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """提取结构化数据"""
        print("📊 Agent 2: 提取结构化数据...")
        
        # 提取业务实体
        entities = self._extract_entities(context, structure_analysis)
        
        # 结构化公式
        structured_formulas = self._structure_formulas(context)
        
        # 提取参数定义
        parameters = self._extract_parameters(context, structure_analysis)
        
        return {
            "entities": entities,
            "formulas": structured_formulas,
            "parameters": parameters,
            "relationships": self._extract_relationships(context),
        }
    
    def _extract_entities(self, context: Dict, analysis: Dict) -> List[Dict]:
        """提取业务实体"""
        entities = []
        
        table_type = analysis.get('table_type')
        
        if table_type == 'financial_model':
            # 识别金融模型实体
            entities.append({
                "name": "OptionPricing",
                "type": "FinancialModel",
                "description": "期权定价模型",
                "attributes": ["spot_price", "strike_price", "volatility", "time_to_maturity"]
            })
        
        return entities
    
    def _structure_formulas(self, context: Dict) -> List[Dict]:
        """结构化公式（带语义标签）"""
        formulas = context.get('cell_formulas', {})
        structured = []
        
        for cell_ref, formula_info in formulas.items():
            structured.append({
                "cell": cell_ref,
                "raw_formula": formula_info['raw_formula'],
                "semantic_type": self._infer_formula_type(formula_info),  # ⭐ 关键
                "business_meaning": self._guess_business_meaning(formula_info),  # ⭐ 关键
                "dependencies": formula_info['depends_on'],
                "complexity": formula_info['complexity'],
            })
        
        return structured
    
    def _infer_formula_type(self, formula_info: Dict) -> str:
        """推断公式类型"""
        functions = formula_info.get('used_functions', [])
        
        if 'NORMSDIST' in functions or 'NORMINV' in functions:
            return "probability_calculation"
        elif 'LN' in functions and 'EXP' in functions:
            return "exponential_growth"
        elif 'SQRT' in functions and 'STDEV' in functions:
            return "volatility_calculation"
        elif 'SUM' in functions or 'AVERAGE' in functions:
            return "aggregation"
        else:
            return "arithmetic"
    
    def _guess_business_meaning(self, formula_info: Dict) -> str:
        """猜测业务含义"""
        formula = formula_info.get('raw_formula', '')
        functions = formula_info.get('used_functions', [])
        
        # 基于模式匹配
        if 'LN' in functions and 'SQRT' in functions:
            return "可能是 Black-Scholes d1/d2 参数计算"
        elif 'STDEV' in functions and 'SQRT' in functions:
            return "年化波动率计算"
        elif 'NORMSDIST' in functions:
            return "累积概率分布计算"
        else:
            return "通用计算"
    
    def _extract_parameters(self, context: Dict, analysis: Dict) -> List[Dict]:
        """提取参数定义"""
        parameters = []
        
        # 从输入区提取参数
        regions = analysis.get('regions', [])
        input_region = next((r for r in regions if r['type'] == 'input'), None)
        
        if input_region:
            for cell in input_region['cells'][:5]:
                cell_info = context['cell_values'].get(cell, {})
                parameters.append({
                    "cell": cell,
                    "value": cell_info.get('value'),
                    "type": cell_info.get('type'),
                    "inferred_name": self._infer_parameter_name(cell),  # ⭐ 推测变量名
                })
        
        return parameters
    
    def _infer_parameter_name(self, cell_ref: str) -> str:
        """推测参数名称（未来可用 LLM 增强）"""
        # 简化版：基于位置
        mapping = {
            'B3': 'parameter_1',
            'B4': 'parameter_2',
            'I15': 'time_to_maturity',
            'I19': 'risk_free_rate',
        }
        return mapping.get(cell_ref, f'param_{cell_ref}')
    
    def _extract_relationships(self, context: Dict) -> List[Dict]:
        """提取实体关系"""
        deps = context.get('dependencies', {})
        relationships = []
        
        for cell, dep_info in list(deps.items())[:5]:
            for depends_on in dep_info.get('direct_depends', []):
                relationships.append({
                    "from": depends_on,
                    "to": cell,
                    "type": "calculates",
                })
        
        return relationships


class InsightGeneratorAgent:
    """
    Agent 3: 洞察生成器
    
    职责：
    - 用自然语言描述业务逻辑
    - 生成数据分析洞察
    - 提供优化建议
    """
    
    def generate(self, context: Dict[str, Any], 
                 structure: Dict[str, Any], 
                 data: Dict[str, Any]) -> Dict[str, Any]:
        """生成语义化洞察"""
        print("💡 Agent 3: 生成业务洞察...")
        
        # 生成自然语言描述
        nl_description = self._generate_description(context, structure, data)
        
        # 分析洞察
        insights = self._generate_insights(data)
        
        # 优化建议
        suggestions = self._generate_suggestions(context, data)
        
        return {
            "natural_language_description": nl_description,
            "insights": insights,
            "suggestions": suggestions,
            "summary": self._generate_summary(context, structure, data),
        }
    
    def _generate_description(self, context: Dict, structure: Dict, data: Dict) -> str:
        """生成自然语言描述"""
        table_type = structure.get('table_type', 'unknown')
        formulas_count = len(context.get('cell_formulas', {}))
        
        desc_parts = []
        
        # 表格类型描述
        type_desc = {
            'financial_model': '这是一个金融定价模型',
            'data_lookup_table': '这是一个数据查找表',
            'summary_report': '这是一个数据汇总报表',
            'general_calculation': '这是一个通用计算表格',
        }
        desc_parts.append(type_desc.get(table_type, '这是一个 Excel 表格'))
        
        # 复杂度描述
        if formulas_count > 20:
            desc_parts.append(f"包含 {formulas_count} 个计算公式，逻辑较为复杂")
        elif formulas_count > 5:
            desc_parts.append(f"包含 {formulas_count} 个计算公式，逻辑中等复杂度")
        else:
            desc_parts.append(f"包含 {formulas_count} 个简单计算公式")
        
        # 业务逻辑描述
        entities = data.get('entities', [])
        if entities:
            entity_names = [e['description'] for e in entities]
            desc_parts.append(f"主要涉及：{', '.join(entity_names)}")
        
        return '。'.join(desc_parts) + '。'
    
    def _generate_insights(self, data: Dict) -> List[str]:
        """生成数据洞察"""
        insights = []
        
        formulas = data.get('formulas', [])
        
        # 统计公式类型
        types_count = {}
        for f in formulas:
            semantic_type = f.get('semantic_type', 'unknown')
            types_count[semantic_type] = types_count.get(semantic_type, 0) + 1
        
        if types_count.get('probability_calculation', 0) > 0:
            insights.append("✅ 检测到概率计算，可能用于风险评估或期权定价")
        
        if types_count.get('volatility_calculation', 0) > 0:
            insights.append("✅ 检测到波动率计算，这是金融风险度量的核心指标")
        
        # 复杂度洞察
        complex_formulas = [f for f in formulas if f.get('complexity') == 'high']
        if complex_formulas:
            insights.append(f"⚠️  有 {len(complex_formulas)} 个高复杂度公式，转换时需特别注意")
        
        return insights
    
    def _generate_suggestions(self, context: Dict, data: Dict) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        patterns = context.get('patterns', [])
        if patterns:
            suggestions.append("🚀 检测到重复模式，建议使用 Pandas 向量化操作替代逐行计算")
        
        vba_exists = context.get('vba_code', {}).get('has_vba', False)
        if vba_exists:
            suggestions.append("📌 包含 VBA 代码，建议分析其业务逻辑并整合到 Python 类中")
        
        formulas = data.get('formulas', [])
        if len(formulas) > 10:
            suggestions.append("💡 公式较多，建议按业务模块拆分为多个 Python 类")
        
        return suggestions
    
    def _generate_summary(self, context: Dict, structure: Dict, data: Dict) -> str:
        """生成总结"""
        return f"""
【表格类型】{structure.get('table_type')}
【公式数量】{len(context.get('cell_formulas', {}))} 个
【业务实体】{len(data.get('entities', []))} 个
【建议】{len(self._generate_suggestions(context, data))} 条优化建议
        """.strip()


# 整合三层 Agent
class EnhancedContextExtractor:
    """增强版上下文提取器 - 集成三层 Agent"""
    
    def __init__(self, excel_file: str):
        self.excel_file = excel_file
        self.analyzer = TableAnalyzerAgent()
        self.extractor = DataExtractorAgent()
        self.insight_generator = InsightGeneratorAgent()
    
    def extract_all(self) -> Dict[str, Any]:
        """完整提取流程"""
        print("=" * 80)
        print("🚀 三层 Agent 提取流程")
        print("=" * 80)
        
        # 第一步：技术提取（原有逻辑）
        from extractors.context_extractor import ExcelContextExtractor
        base_extractor = ExcelContextExtractor(self.excel_file)
        base_context = base_extractor.extract_all()
        
        # 第二步：结构分析
        structure_analysis = self.analyzer.analyze(base_context)
        
        # 第三步：数据提取
        structured_data = self.extractor.extract(base_context, structure_analysis)
        
        # 第四步：洞察生成
        insights = self.insight_generator.generate(
            base_context, 
            structure_analysis, 
            structured_data
        )
        
        # 整合结果
        return {
            # 原始技术数据
            "raw_context": base_context,
            
            # 结构化语义数据
            "structure_analysis": structure_analysis,
            "structured_data": structured_data,
            "business_insights": insights,
            
            # 元信息
            "extraction_method": "three_layer_agents",
            "agents_used": ["TableAnalyzer", "DataExtractor", "InsightGenerator"],
        }


def demo():
    """演示三层 Agent"""
    excel_file = "/workspaces/RM_Tools/Margin Call.xlsm"
    
    extractor = EnhancedContextExtractor(excel_file)
    result = extractor.extract_all()
    
    print("\n" + "=" * 80)
    print("📊 提取结果摘要")
    print("=" * 80)
    
    # 显示业务洞察
    insights = result['business_insights']
    print("\n💡 业务洞察:")
    print(insights['natural_language_description'])
    
    print("\n✅ 关键发现:")
    for insight in insights['insights']:
        print(f"  {insight}")
    
    print("\n🚀 优化建议:")
    for suggestion in insights['suggestions']:
        print(f"  {suggestion}")
    
    # 保存结果
    output_file = "/workspaces/RM_Tools/excel_to_code/output/contexts/enhanced_context.json"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        # 只保存可序列化的部分
        json.dump({
            "structure_analysis": result['structure_analysis'],
            "structured_data": result['structured_data'],
            "business_insights": result['business_insights'],
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 增强上下文已保存: {output_file}")


if __name__ == '__main__':
    demo()
