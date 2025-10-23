# Excel Parser 输出格式指南

## 🎯 设计理念

Excel Parser 提供**多种输出格式**，适用于不同的使用场景：

1. **完整格式** - 详细的单元格信息（`cell_values`, `cell_formulas`）
2. **行式格式** - 按行组织，便于数据分析（`tables_by_row`）
3. **列式格式** - 按列组织，便于逻辑提取（`formulas_by_column`）
4. **紧凑格式** - 高度压缩，快速预览（`compact_view`）

---

## 📊 输出格式详解

### 1. tables_by_row - 按行输出（用于 DataFrame）

**特点**：
- ✅ 只包含表面值（不含公式本身）
- ✅ 按行组织，直接可转 DataFrame
- ✅ 紧凑格式，节省 token
- ✅ 适合数据分析和数值计算

**格式**：
```json
{
  "tables_by_row": {
    "Sheet1": {
      "row_1": [val1, val2, val3, ...],
      "row_2": [val1, val2, val3, ...],
      ...
    }
  }
}
```

**使用示例**：
```python
import json
import pandas as pd

# 加载数据
data = json.load(open('output.json'))
tables = data['tables_by_row']

# 转换为 DataFrame
sheet_data = tables['Sheet1']
df_data = [sheet_data[f'row_{i}'] for i in range(1, len(sheet_data) + 1)]
df = pd.DataFrame(df_data)

# 设置列名（使用第一行作为表头）
df.columns = df.iloc[0]
df = df[1:]  # 删除表头行

# 数据分析
print(df.describe())
print(df.info())
```

**适用场景**：
- 数据清洗和转换
- 统计分析
- 数据可视化
- 批量数据处理

---

### 2. formulas_by_column - 按列输出（用于逻辑提取）

**特点**：
- ✅ 有公式则保存公式，无公式则保存原值
- ✅ 按列组织，便于识别重复逻辑模式
- ✅ 包含行号和类型信息
- ✅ 适合逻辑分析和模式识别

**格式**：
```json
{
  "formulas_by_column": {
    "Sheet1": {
      "A": [
        {"row": 1, "value": "Header", "type": "string"},
        {"row": 2, "value": 100, "type": "number"},
        {"row": 3, "value": "=B3*C3", "type": "formula"},
        ...
      ],
      "B": [...]
    }
  }
}
```

**使用示例**：
```python
import json
from collections import defaultdict

data = json.load(open('output.json'))
formulas = data['formulas_by_column']['Sheet1']

# 1. 提取某列的所有公式
col_a_formulas = [
    item for item in formulas['A'] 
    if item['type'] == 'formula'
]

print(f"列 A 有 {len(col_a_formulas)} 个公式")
for f in col_a_formulas:
    print(f"  行{f['row']}: {f['value']}")

# 2. 检测公式模式
def extract_pattern(formula):
    import re
    # 将数字替换为占位符
    return re.sub(r'\d+', 'N', formula)

patterns = defaultdict(list)
for col, items in formulas.items():
    for item in items:
        if item['type'] == 'formula':
            pattern = extract_pattern(item['value'])
            patterns[pattern].append((col, item['row']))

print("\n公式模式分析:")
for pattern, locations in patterns.items():
    if len(locations) > 1:  # 重复模式
        print(f"  模式: {pattern}")
        print(f"  出现次数: {len(locations)}")
        print(f"  位置: {locations[:3]}...")

# 3. 提取表头
headers = {}
for col, items in formulas.items():
    if items and items[0]['type'] == 'string':
        headers[col] = items[0]['value']

print(f"\n表头: {headers}")
```

**适用场景**：
- 业务逻辑提取
- 公式模式识别
- 循环结构检测
- 自动化代码生成

---

### 3. compact_view - 紧凑视图（用于快速预览）

**特点**：
- ✅ 高度压缩的表格概览
- ✅ 只包含关键信息
- ✅ 最小化 token 使用
- ✅ 适合快速理解表格结构

**格式**：
```json
{
  "compact_view": {
    "Sheet1": {
      "dimensions": {"rows": 100, "cols": 10},
      "header": ["A", "B", "C", ...],
      "sample_rows": [
        [val1, val2, ...],
        [val1, val2, ...],
        ...
      ],
      "formula_summary": {
        "total": 50,
        "by_column": {"A": 10, "B": 20, ...},
        "unique_patterns": 5
      }
    }
  }
}
```

**使用示例**：
```python
import json

data = json.load(open('output.json'))
compact = data['compact_view']['Sheet1']

# 快速了解表格结构
print(f"表格规模: {compact['dimensions']['rows']} 行 x {compact['dimensions']['cols']} 列")
print(f"表头: {compact['header']}")
print(f"前几行数据:")
for idx, row in enumerate(compact['sample_rows'], 1):
    print(f"  行{idx}: {row}")

# 公式分析
summary = compact['formula_summary']
print(f"\n公式统计:")
print(f"  总公式数: {summary['total']}")
print(f"  唯一模式数: {summary['unique_patterns']}")
print(f"  公式最多的列: {max(summary['by_column'].items(), key=lambda x: x[1])}")

# 快速判断表格类型
if summary['total'] > compact['dimensions']['rows'] * compact['dimensions']['cols'] * 0.1:
    print("\n表格类型: 计算密集型（公式占比 > 10%）")
else:
    print("\n表格类型: 数据存储型（公式占比较低）")
```

**适用场景**：
- 快速预览表格内容
- 评估表格复杂度
- 选择合适的处理策略
- 生成表格摘要报告

---

## 📈 格式对比

| 维度 | 完整格式 | tables_by_row | formulas_by_column | compact_view |
|------|---------|---------------|-------------------|--------------|
| **大小** | 大 | 中 | 中 | 小 |
| **详细度** | 高 | 中 | 高 | 低 |
| **可读性** | 低 | 高 | 高 | 高 |
| **适合分析** | 技术分析 | 数据分析 | 逻辑分析 | 快速预览 |
| **Token 消耗** | 高 | 中 | 中 | 低 |

### 实际测试（Margin Call.xlsm）

```
文件: Margin Call.xlsm (58 个单元格, 13 个公式)

完整格式 (cell_values + cell_formulas):
  大小: 11,413 字符
  
新格式合计 (三种格式):
  tables_by_row:      4,593 字符
  formulas_by_column: 3,199 字符
  compact_view:         919 字符
  合计:               8,711 字符
  
压缩率: 23.7% 更小（新格式）
```

---

## 🎯 使用建议

### 场景 1: 数据分析任务

**推荐**: `tables_by_row`

```python
# 快速转换为 DataFrame
df = pd.DataFrame(data['tables_by_row']['Sheet1'].values())

# 数据清洗
df = df.dropna()
df = df.astype({'col1': 'float', 'col2': 'int'})

# 统计分析
print(df.describe())
```

### 场景 2: 公式逻辑提取

**推荐**: `formulas_by_column` + `compact_view`

```python
# 先用 compact_view 了解结构
compact = data['compact_view']['Sheet1']
formula_columns = [col for col, count in compact['formula_summary']['by_column'].items() if count > 0]

# 再用 formulas_by_column 提取具体逻辑
formulas = data['formulas_by_column']['Sheet1']
for col in formula_columns:
    print(f"列 {col} 的公式:")
    for item in formulas[col]:
        if item['type'] == 'formula':
            print(f"  {item['value']}")
```

### 场景 3: LLM 代码生成

**推荐**: `compact_view` + `formulas_by_column`

```python
# 1. 使用 compact_view 生成摘要
prompt = f"""
这是一个 Excel 表格，包含:
- 规模: {compact['dimensions']['rows']} 行 x {compact['dimensions']['cols']} 列
- 表头: {compact['header']}
- 公式数: {compact['formula_summary']['total']}
- 主要公式列: {list(compact['formula_summary']['by_column'].keys())}

样本数据:
{compact['sample_rows'][:3]}
"""

# 2. 使用 formulas_by_column 提供详细逻辑
prompt += "\n\n公式详情:\n"
for col, items in data['formulas_by_column']['Sheet1'].items():
    formulas_list = [item['value'] for item in items if item['type'] == 'formula']
    if formulas_list:
        prompt += f"列 {col}: {formulas_list[:3]}\n"

# 3. 发送给 LLM
# response = llm.generate(prompt)
```

### 场景 4: 快速预览

**推荐**: `compact_view`

```python
# 只加载紧凑视图
import json
data = json.load(open('output.json'))
compact = data['compact_view']

# 快速遍历所有工作表
for sheet, info in compact.items():
    print(f"\n工作表: {sheet}")
    print(f"  规模: {info['dimensions']['rows']} x {info['dimensions']['cols']}")
    print(f"  公式: {info['formula_summary']['total']} 个")
```

---

## 💡 最佳实践

### 1. 组合使用

```python
# 步骤 1: 用 compact_view 快速筛选
for sheet, info in data['compact_view'].items():
    if info['formula_summary']['total'] > 10:  # 有大量公式
        # 步骤 2: 用 formulas_by_column 分析逻辑
        analyze_formulas(data['formulas_by_column'][sheet])
    else:  # 主要是数据
        # 步骤 3: 用 tables_by_row 处理数据
        process_data(data['tables_by_row'][sheet])
```

### 2. 按需加载

```python
import json

# 只加载需要的部分
with open('output.json', 'r') as f:
    full_data = json.load(f)
    
    # 场景 1: 只需要数据
    data_only = {
        'tables_by_row': full_data['tables_by_row']
    }
    
    # 场景 2: 只需要逻辑
    logic_only = {
        'formulas_by_column': full_data['formulas_by_column'],
        'compact_view': full_data['compact_view']
    }
```

### 3. 缓存策略

```python
import json
from functools import lru_cache

@lru_cache(maxsize=10)
def load_compact_view(file_path):
    """只加载紧凑视图（最小开销）"""
    data = json.load(open(file_path))
    return data['compact_view']

@lru_cache(maxsize=5)
def load_for_analysis(file_path, sheet_name):
    """加载分析所需数据"""
    data = json.load(open(file_path))
    return {
        'tables': data['tables_by_row'][sheet_name],
        'formulas': data['formulas_by_column'][sheet_name]
    }
```

---

## 🔧 工具函数

### 将 tables_by_row 转换为 DataFrame

```python
import pandas as pd
import json

def to_dataframe(json_file, sheet_name, has_header=True):
    """
    将 tables_by_row 转换为 pandas DataFrame
    
    Args:
        json_file: JSON 文件路径
        sheet_name: 工作表名称
        has_header: 是否使用第一行作为列名
    
    Returns:
        pandas.DataFrame
    """
    data = json.load(open(json_file))
    sheet_data = data['tables_by_row'][sheet_name]
    
    # 按行号排序
    sorted_rows = sorted(sheet_data.items(), key=lambda x: int(x[0].split('_')[1]))
    df_data = [row[1] for row in sorted_rows]
    
    df = pd.DataFrame(df_data)
    
    if has_header:
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)
    
    return df
```

### 提取公式模式

```python
import re
from collections import defaultdict

def extract_formula_patterns(json_file, sheet_name):
    """
    提取公式模式
    
    Returns:
        dict: {pattern: [(col, row), ...]}
    """
    data = json.load(open(json_file))
    formulas = data['formulas_by_column'][sheet_name]
    
    patterns = defaultdict(list)
    
    for col, items in formulas.items():
        for item in items:
            if item['type'] == 'formula':
                # 提取模式（数字替换为 N）
                pattern = re.sub(r'\d+', 'N', item['value'])
                patterns[pattern].append((col, item['row']))
    
    return dict(patterns)
```

---

## 📚 参考

- [excel_parser/README.md](README.md) - 项目文档
- [examples/](examples/) - 使用示例
- [PROJECT_ARCHITECTURE.md](../PROJECT_ARCHITECTURE.md) - 架构设计

---

**Excel Parser** - 提供多种格式，满足不同需求 🚀
