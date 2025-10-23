# Excel to Code - 智能報表轉換系統

## 🎯 專案目標

將金融機構的手工 Excel 報表（包含數據、公式、VBA）轉換為可維護的 Python 代碼，實現自動化並支持智能體操作。

## 🏗️ 核心理念

**不做機械轉換，而是理解業務邏輯**

1. **完整上下文提取**（無需 LLM）- 提取所有相關信息
2. **智能格式化** - 整理成 LLM 友好的格式
3. **LLM 生成代碼** - 生成優雅、可維護的 Python 代碼
4. **自動驗證** - 確保結果與 Excel 一致

## 📁 專案結構

```
excel_to_code/
├── extractors/          # 上下文提取器（不依賴 LLM）
│   ├── cell_extractor.py         # 儲存格值與類型
│   ├── formula_extractor.py      # 公式與依賴關係
│   ├── dependency_analyzer.py    # 依賴圖與計算順序
│   ├── vba_extractor.py          # VBA 代碼分析
│   ├── pattern_detector.py       # 重複模式與循環識別
│   ├── semantic_analyzer.py      # 語義與業務邏輯分析
│   └── context_extractor.py      # 主提取器（整合所有）
│
├── formatters/          # 上下文格式化器
│   ├── llm_prompt_builder.py    # 為 LLM 構建 prompt
│   ├── markdown_formatter.py    # Markdown 文檔生成
│   └── context_optimizer.py     # 優化上下文大小
│
├── generators/          # 代碼生成器
│   ├── llm_client.py            # LLM API 客戶端
│   ├── code_generator.py        # Python 代碼生成
│   └── test_generator.py        # 單元測試生成
│
├── validators/          # 驗證器
│   ├── result_validator.py      # 結果一致性驗證
│   └── code_quality.py          # 代碼品質檢查
│
├── output/              # 輸出目錄
│   ├── contexts/        # 提取的上下文
│   ├── prompts/         # 生成的 prompts
│   ├── generated_code/  # 生成的代碼
│   └── reports/         # 驗證報告
│
├── examples/            # 示例與演示
│   └── convert_margin_call.py
│
├── config.py            # 配置文件
├── main.py              # 主程序入口
└── requirements.txt     # 依賴清單
```

## 🚀 快速開始

### 1. 安裝依賴

```bash
cd excel_to_code
pip install -r requirements.txt
```

### 2. 配置 LLM API

編輯 `config.py`：

```python
LLM_PROVIDER = "gemini"  # 或 "anthropic", "openai"
API_KEY = "your-api-key"
```

### 3. 轉換 Excel 報表

```bash
python main.py --input ../Margin_Call.xlsm --output output/margin_call.py
```

或使用 Python API：

```python
from excel_to_code import ExcelToCodeConverter

converter = ExcelToCodeConverter()
result = converter.convert("../Margin_Call.xlsm")

# 查看生成的代碼
print(result.python_code)

# 驗證結果
result.validate()
```

## 📊 工作流程

### Phase 1: 完整上下文提取（不依賴 LLM）

提取以下信息：

- ✅ 儲存格數值與類型
- ✅ 儲存格公式（原始 + 結構化）
- ✅ 儲存格依賴關係與計算順序
- ✅ VBA 代碼與調用關係
- ✅ 重複模式識別（循環結構）
- ✅ 命名範圍與變數語義
- ✅ 表格結構與業務分區
- ✅ 外部數據源與連接
- ✅ 條件格式與驗證規則
- ✅ 元數據（作者、版本等）

### Phase 2: 智能格式化

將提取的上下文整理成：

- 📄 結構化 JSON
- 📝 Markdown 文檔（業務邏輯說明）
- 🎯 LLM Prompt（引導生成優質代碼）

### Phase 3: LLM 代碼生成

使用 LLM 生成：

- 🐍 優雅的 Python 類（非逐行翻譯）
- 📚 完整的文檔字符串
- 🧪 單元測試（使用 Excel 實際值驗證）
- 🔍 業務邏輯識別（例如「這是 Black-Scholes 模型」）

### Phase 4: 自動驗證

- ✅ 計算結果與 Excel 一致性檢查
- ✅ 代碼品質檢查（linting）
- ✅ 測試覆蓋率報告

## 🎨 特色功能

### 1. 智能模式識別

自動識別 Excel 中的重複模式：

```python
# Excel: A2:A100 每行都是 =B2*C2, =B3*C3, ...
# 轉換為：
df['A'] = df['B'] * df['C']
```

### 2. 業務邏輯理解

不只是翻譯公式，還理解業務含義：

```python
# Excel: =LN(S/(K*EXP(-r*T)))/(σ*SQRT(T))+σ*SQRT(T)/2
# 轉換為：
def calculate_d1(spot_price, strike_price, rate, time, volatility):
    """Calculate d1 parameter in Black-Scholes formula"""
    return (np.log(spot_price / strike_price) + 
            (rate + 0.5 * volatility**2) * time) / (volatility * np.sqrt(time))
```

### 3. VBA 邏輯整合

將 VBA 的業務邏輯融入 Python 類：

```python
class MarginCallCalculator:
    """原始 VBA 的 CalculateMarginCall 子程序"""
    
    def calculate(self):
        # VBA 邏輯轉換為 Python
        pass
```

## 🔧 高級配置

### 自定義 LLM Prompt 模板

編輯 `formatters/llm_prompt_builder.py` 的模板來調整生成風格。

### 添加自定義模式檢測

在 `extractors/pattern_detector.py` 中添加新的模式識別規則。

### 調整驗證閾值

在 `validators/result_validator.py` 中配置數值誤差容忍度。

## 📝 示例

查看 `examples/convert_margin_call.py` 了解完整使用示例。

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License
