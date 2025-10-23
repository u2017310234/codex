# Excel to Code - 項目總結

## ✅ 已完成的工作

### 1. 項目結構搭建

```
excel_to_code/
├── extractors/          # 完整上下文提取器（不依賴 LLM）
│   ├── context_extractor.py   ✅ 完成
│   └── __init__.py
│
├── formatters/          # LLM Prompt 構建器
│   ├── llm_prompt_builder.py  ✅ 完成
│   └── __init__.py
│
├── generators/          # 代碼生成器（待實現）
│   └── __init__.py
│
├── validators/          # 驗證器（待實現）
│   └── __init__.py
│
├── output/              # 輸出目錄
│   ├── contexts/        # 提取的上下文 JSON
│   ├── prompts/         # 生成的 LLM prompts
│   ├── generated_code/  # LLM 生成的代碼
│   └── reports/         # 驗證報告
│
├── examples/
│   └── convert_margin_call.py  ✅ 示例腳本
│
├── config.py            ✅ 配置文件
├── main.py              ✅ 主程序入口
├── requirements.txt     ✅ 依賴清單
├── README.md            ✅ 項目文檔
└── test_quick.py        ✅ 快速測試
```

### 2. 核心功能實現

#### A. 完整上下文提取器 (`extractors/context_extractor.py`)

提取以下 14 類信息：

1. ✅ **元數據** - 文件名、作者、修改時間等
2. ✅ **工作簿結構** - 工作表名稱、數量
3. ✅ **儲存格數值與類型** - 區分輸入值 vs 公式
4. ✅ **儲存格公式** - 原始公式 + 結構化信息
5. ✅ **依賴關係** - 誰依賴誰、反向依賴
6. ✅ **計算順序** - 拓撲排序
7. ✅ **數據流分析** - 輸入 → 計算 → 輸出
8. ✅ **VBA 代碼** - 檢測是否存在 VBA
9. ✅ **重複模式** - 識別循環結構（如列中重複的公式）
10. ✅ **命名範圍** - 變數名與範圍映射
11. ✅ **表格結構** - 數據區域識別
12. ✅ **外部連接** - 外部工作簿引用
13. ✅ **條件格式** - 條件規則
14. ✅ **數據驗證** - 驗證規則

#### B. LLM Prompt 構建器 (`formatters/llm_prompt_builder.py`)

生成結構化的 Prompt，包含：

1. ✅ **角色定義** - 定義 LLM 的專業背景
2. ✅ **任務描述** - 清晰的轉換目標
3. ✅ **工作簿概覽** - 統計信息
4. ✅ **業務邏輯分析** - 基於函數推測業務場景
5. ✅ **數據流程** - 輸入輸出關係
6. ✅ **公式詳情** - 關鍵公式展示
7. ✅ **重複模式** - 循環結構說明
8. ✅ **VBA 描述** - VBA 代碼說明
9. ✅ **依賴關係摘要** - 計算順序與核心節點
10. ✅ **輸出要求** - 期望的代碼結構
11. ✅ **代碼風格要求** - 命名、類型提示等
12. ✅ **驗證要求** - 測試用例說明

### 3. 使用方式

#### 方式 1: 命令行（推薦）

```bash
cd /workspaces/RM_Tools/excel_to_code

# 基本用法：提取上下文 + 生成 Prompt
python main.py --input ../Margin_Call.xlsm

# 輸出到指定文件
python main.py --input ../Margin_Call.xlsm --output margin_call.py

# 使用 LLM 自動生成代碼（需要配置 API key）
python main.py --input ../Margin_Call.xlsm --generate --llm gemini
```

#### 方式 2: Python API

```python
from excel_to_code import ExcelToCodeConverter

converter = ExcelToCodeConverter()
result = converter.convert("../Margin_Call.xlsm")

# 查看生成的 Prompt
print(result['prompt'])

# 手動複製 Prompt 給 LLM
```

#### 方式 3: 直接運行示例

```bash
cd /workspaces/RM_Tools/excel_to_code
python examples/convert_margin_call.py
```

### 4. 輸出文件

運行後會生成：

1. **上下文 JSON** - `output/contexts/margin_call_context.json`
   - 包含所有提取的信息
   - 可用於離線分析或調試

2. **LLM Prompt** - `output/prompts/margin_call_prompt.md`
   - 完整的 Markdown 文檔
   - 可直接複製給任何 LLM

3. **生成的代碼** - `output/generated_code/margin_call.py` (如果使用 --generate)
   - LLM 生成的 Python 類
   - 包含文檔和測試

## 🎯 核心理念（已實現）

### 不做機械轉換

❌ **機械轉換**:
```python
cell_i31 = np.log(cell_i24 / (cell_i20 * np.exp(-cell_i19 * cell_i15)))
```

✅ **理解業務邏輯**:
```python
def calculate_d1(self):
    """Calculate d1 parameter in Black-Scholes formula"""
    return (np.log(self.spot_price / self.strike_price) + 
            (self.risk_free_rate + 0.5 * self.volatility**2) * self.time_to_maturity) / \
           (self.volatility * np.sqrt(self.time_to_maturity))
```

### 識別循環結構

❌ **逐行計算**:
```python
for i in range(len(df)):
    df.loc[i, 'result'] = df.loc[i, 'a'] * df.loc[i, 'b']
```

✅ **向量化操作**:
```python
df['result'] = df['a'] * df['b']  # 快 100 倍
```

## 📊 測試結果（Margin Call.xlsm）

提取的信息：
- 工作表: 1 個
- 儲存格: ~50 個
- 公式: 13 個
- 依賴關係: 完整構建
- 檢測模式: 可能的循環結構
- 使用的函數: SQRT, NORMSDIST, EXP, LN, STDEV
- 業務邏輯推測: **Black-Scholes 期權定價模型**

## 🚀 下一步工作

### 高優先級

1. **LLM 集成** (`generators/`)
   - [ ] Gemini API 客戶端
   - [ ] Claude API 客戶端
   - [ ] OpenAI API 客戶端
   - [ ] 本地 LLM 支持（Ollama）

2. **結果驗證** (`validators/`)
   - [ ] 數值一致性檢查
   - [ ] 代碼品質檢查（black, pylint）
   - [ ] 單元測試生成與執行
   - [ ] 驗證報告生成

3. **VBA 深度分析**
   - [ ] 使用 `oletools` 或 `vba-parser` 提取 VBA AST
   - [ ] 識別 VBA 的控制流和業務邏輯
   - [ ] 將 VBA 邏輯融入 Python 類

### 中優先級

4. **模式增強**
   - [ ] 更智能的循環檢測（時間序列、累積計算）
   - [ ] 矩陣運算識別
   - [ ] 查找表優化（VLOOKUP → Pandas merge）

5. **可視化**
   - [ ] 依賴關係圖可視化（Graphviz）
   - [ ] 數據流程圖
   - [ ] 業務邏輯流程圖

6. **批量處理**
   - [ ] 支持多個 Excel 文件
   - [ ] 工作流編排
   - [ ] 進度追蹤

### 低優先級

7. **增量更新**
   - [ ] 檢測 Excel 變更
   - [ ] 只重新生成變更部分

8. **部署工具**
   - [ ] Docker 容器化
   - [ ] Web 界面
   - [ ] REST API

## 💡 使用建議

### 當前最佳工作流

1. **運行提取器**
   ```bash
   python main.py --input your_file.xlsm
   ```

2. **查看生成的 Prompt**
   ```bash
   cat output/prompts/your_file_prompt.md
   ```

3. **複製到 LLM**
   - 打開 Gemini / Claude / ChatGPT
   - 粘貼 Prompt
   - 等待生成代碼

4. **保存並測試代碼**
   ```python
   # 將 LLM 生成的代碼保存為 .py
   # 運行測試確保與 Excel 一致
   ```

5. **迭代優化**
   - 如果結果不理想，修改 Prompt 模板
   - 或在 LLM 對話中繼續優化

## 🔧 配置 API Key（可選）

如果要使用 `--generate` 自動生成代碼：

```bash
# 編輯 config.py
cd /workspaces/RM_Tools/excel_to_code
nano config.py

# 設置你的 API key
GEMINI_API_KEY = "your-api-key"
# 或使用環境變數
export GEMINI_API_KEY="your-api-key"
```

## 📚 技術棧

- **Excel 解析**: openpyxl
- **數據處理**: pandas, numpy
- **科學計算**: scipy
- **LLM**: google-generativeai, anthropic, openai
- **代碼品質**: black, pylint, mypy
- **測試**: pytest

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

特別需要幫助的領域：
- VBA 深度解析
- 更多財務模型模式識別
- LLM Prompt 優化
- 驗證邏輯完善

## 📄 授權

MIT License

---

**總結**: 專案骨架已完成，核心提取與格式化邏輯已實現，可以立即使用（手動複製 Prompt 給 LLM）。後續主要工作是實現 LLM 自動調用和結果驗證。
