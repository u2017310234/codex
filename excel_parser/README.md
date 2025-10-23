# Excel Parser - 第一阶段：机械化提取

## 🎯 项目定位

**纯技术的 Excel 结构提取器**

- ✅ 无 AI 依赖
- ✅ 高确定性
- ✅ 快速可靠
- ✅ 完整的结构化输出

## 📦 核心功能

### 提取内容

1. **元数据** - 文件信息、作者、时间
2. **工作簿结构** - 工作表、范围
3. **单元格数据** - 值、类型、格式
4. **公式** - 原始公式、函数、引用
5. **依赖关系** - 计算图、拓扑排序
6. **VBA 代码** - 完整提取宏代码（使用 oletools）
   - 自动检测 VBA 存在性
   - 提取所有模块（Standard Module, Class Module, Form）
   - 解析过程/函数列表
   - 保存为独立 `.bas` 文件
7. **命名范围** - 变量定义
8. **数据验证** - 验证规则
9. **条件格式** - 格式规则
10. **外部链接** - 外部数据源

### 不做的事

- ❌ 不做语义理解
- ❌ 不做业务推测
- ❌ 不做自然语言生成
- ❌ 不调用 LLM

## 🚀 快速开始

### 安装

```bash
cd excel_parser
pip install -r requirements.txt
```

### 基本使用

```python
from extractors.excel_parser import ExcelContextExtractor

# 解析 Excel
parser = ExcelContextExtractor('your_file.xlsx')
context = parser.extract_all()

# 保存为 JSON
parser.save_context('output/context.json')
```

### 命令行

```bash
python main.py --input your_file.xlsx --output result.json
```

### 🎬 完整演示

查看完整的工作流演示（从 Excel 到各种格式）：

```bash
cd examples
python demo_complete.py
```

这个演示会展示：
1. ✅ 从 Excel 文件提取所有格式
2. ✅ 使用 `tables_by_row` 进行数据分析（转换为 DataFrame）
3. ✅ 使用 `formulas_by_column` 分析公式逻辑
4. ✅ 使用 `compact_view` 快速预览
5. ✅ 提取 VBA 代码
6. ✅ 分析公式模式（识别重复逻辑）
7. ✅ 保存和加载 JSON
8. ✅ 导出为多种格式（CSV, JSON, Markdown）

**输出文件**（在 `examples/output/` 目录）：
- `Sheet1_data.csv` - 表格数据
- `formulas.json` - 公式详情
- `overview.md` - Markdown 概览
- `demo_output.json` - 完整 JSON
- `*.bas` - VBA 模块文件

## 📊 输出格式

### JSON 结构

```json
{
  "metadata": {
    "filename": "example.xlsx",
    "author": "...",
    "created": "..."
  },
  "workbook_structure": {
    "sheets": ["Sheet1", "Sheet2"],
    "has_vba": false
  },
  "cell_values": {
    "Sheet1!A1": {
      "value": 100,
      "type": "number",
      "is_formula": false
    }
  },
  "cell_formulas": {
    "Sheet1!B1": {
      "raw_formula": "=A1*2",
      "depends_on": ["A1"],
      "used_functions": []
    }
  },
  "dependencies": {
    "Sheet1!B1": {
      "direct_depends": ["Sheet1!A1"],
      "depended_by": []
    }
  },
  "calculation_order": ["Sheet1!A1", "Sheet1!B1"],
  "vba_code": {
    "has_vba": true,
    "modules": [
      {
        "filename": "Module1.bas",
        "stream_path": "VBA/Module1",
        "code": "Sub MyMacro()\n  MsgBox \"Hello\"\nEnd Sub",
        "code_length": 35,
        "procedures": ["MyMacro"]
      }
    ],
    "summary": {
      "module_count": 1,
      "total_lines": 3,
      "procedure_count": 1,
      "procedures": ["MyMacro"]
    }
  }
}
```

### VBA 代码文件

除了 JSON 中包含 VBA 代码外，每个模块还会保存为独立的 `.bas` 文件：

```
excel_parser/output/
├── margin_call.json          # JSON 上下文
└── vba/                      # VBA 模块目录
    ├── Margin Call_模块1.bas        # 标准模块
    ├── Margin Call_ThisWorkbook.cls.bas  # 工作簿类模块
    └── Margin Call_Sheet1.cls.bas        # 工作表类模块
```

**VBA 文件示例**：

```vb
' Margin Call_模块1.bas
Attribute VB_Name = "模块1"

Sub Margin_Call()
    Dim datet As Integer
    datet = ThisWorkbook.A1.Value
    
    ' 复制文件到指定文件夹
    ActiveWorkbook.SaveAs Filename:= _
        "credit/" & datet & "raw/" & a & datet & ".xlsx", _
        FileFormat:=xlOpenXMLWorkbook, CreateBackup:=False
    
    ' ...更多代码
End Sub
```

## 🔧 技术栈

- **openpyxl** - Excel 读取（核心依赖）
- **oletools** - VBA 提取（推荐，可选）
- **pandas/numpy** - 数据处理
- **Python 3.8+** - 标准库
- **无 AI 依赖** - 纯算法实现

### VBA 提取说明

VBA 提取依赖 `oletools` 库：

```bash
pip install oletools>=0.60
```

**如果未安装 oletools**：
- 仍会检测 VBA 是否存在（`has_vba: true/false`）
- 但无法提取具体代码
- JSON 中会包含安装提示

**安装 oletools 后**：
- ✅ 自动提取所有 VBA 模块
- ✅ 解析过程/函数列表
- ✅ 保存为独立 `.bas` 文件
- ✅ 统计代码行数和复杂度

## 📈 性能

- 1000 行 Excel: ~2 秒
- 10000 行 Excel: ~15 秒
- 内存占用: < 100MB

## 🔗 与第二阶段集成

输出的 JSON 可以直接作为 `excel_to_code` 项目的输入：

```bash
# 第一阶段：提取
cd excel_parser
python main.py --input data.xlsx --output ../excel_to_code/input/data.json

# 第二阶段：生成代码
cd ../excel_to_code
python main.py --input input/data.json --output generated_code.py
```

## 📝 示例

### 完整示例：Margin Call.xlsm

```bash
python main.py --input "../Margin Call.xlsm" --output output/margin_call.json
```

**输出**：

```
🔍 開始提取: Margin Call.xlsm
✅ 提取完成
✅ 上下文已保存: output/margin_call.json
   ✓ VBA 模塊已保存: Margin Call_模块1.bas
   ✓ VBA 模塊已保存: Margin Call_ThisWorkbook.cls.bas
   ✓ VBA 模塊已保存: Margin Call_Sheet1.cls.bas
✅ 完成! 输出: output/margin_call.json
```

**统计信息**：

```
文件名: Margin Call.xlsm
文件大小: 19.91 KB
工作表数: 1
单元格数: 58
公式数: 13
依赖关系: 25

VBA 代码:
  • 包含 VBA: True
  • 模块数: 3
  • 总代码行数: 122
  • 过程数: 2
  • 过程列表: ['Margin_Call', '宏2']
```

### Python API 示例

```python
from extractors.excel_parser import ExcelContextExtractor

# 创建提取器
extractor = ExcelContextExtractor("your_file.xlsm")

# 提取所有内容
context = extractor.extract_all()

# 查看 VBA 信息
vba = context['vba_code']
if vba['has_vba']:
    print(f"检测到 {vba['summary']['module_count']} 个 VBA 模块")
    print(f"总代码行数: {vba['summary']['total_lines']}")
    print(f"过程列表: {vba['summary']['procedures']}")
    
    # 查看具体模块
    for module in vba['modules']:
        print(f"\n模块: {module['filename']}")
        print(f"代码长度: {module['code_length']} 字符")
        print(f"包含过程: {module['procedures']}")

# 保存（会自动保存 VBA 文件）
extractor.save_context("output/result.json")
```

## 📚 示例脚本

项目提供了多个演示脚本，展示不同的使用场景：

### 1. 简单示例 (`examples/demo_simple.py`)

最基本的使用：提取 → 保存 → 查看摘要

```bash
cd examples
python demo_simple.py
```

**展示内容**:
- 基本提取流程
- 快速查看工作表概览
- 查看 VBA 代码摘要

### 2. 完整演示 (`examples/demo_complete.py`)

展示所有功能的完整工作流

```bash
cd examples
python demo_complete.py
```

**演示内容**:
1. ✅ 从 Excel 文件提取所有格式
2. ✅ 使用 `tables_by_row` 进行数据分析（转为 pandas DataFrame）
3. ✅ 使用 `formulas_by_column` 分析公式逻辑
4. ✅ 使用 `compact_view` 快速预览
5. ✅ 提取和查看 VBA 代码
6. ✅ 分析公式模式（识别重复逻辑）
7. ✅ 保存和加载 JSON
8. ✅ 导出为多种格式（CSV, JSON, Markdown）

**生成文件**（在 `examples/output/`）:
- `Sheet1_data.csv` - 数据表格
- `formulas.json` - 公式详情
- `overview.md` - Markdown 概览
- `demo_output.json` - 完整 JSON
- `*.bas` - VBA 模块文件

### 3. 格式演示 (`examples/demo_formats.py`)

专门演示如何使用新的优化格式

```bash
cd examples
python demo_formats.py output/your_file.json
```

**展示**:
- `tables_by_row`: 快速转换为 DataFrame
- `formulas_by_column`: 按列分析公式
- `compact_view`: 紧凑预览
- 组合使用策略

详见 [FORMAT_GUIDE.md](FORMAT_GUIDE.md)

### 批量处理

```bash
# 批量提取多个 Excel 文件
for file in ../examples/*.xlsx; do
    basename=$(basename "$file" .xlsx)
    python main.py --input "$file" --output "output/${basename}.json"
done
```

## 📖 文档

- [FORMAT_GUIDE.md](FORMAT_GUIDE.md) - 详细的格式使用指南
- [examples/](examples/) - 完整的示例代码
- [../excel_to_code/README.md](../excel_to_code/README.md) - 第二阶段文档

## 🤝 贡献

这是一个纯技术项目，欢迎提交：
- 新的提取功能
- 性能优化
- Bug 修复

## 📄 许可

MIT License
