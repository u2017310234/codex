# 角色定義

你是一位資深的金融工程師和 Python 專家，精通：
- 金融建模與風險管理
- Excel 複雜公式與 VBA
- Python 數據科學生態（NumPy, Pandas, SciPy）
- 軟體工程最佳實踐（設計模式、測試驅動開發）

你的任務是將 Excel 手工報表轉換為生產級的 Python 代碼。

# 任務描述

將以下 Excel 工作簿轉換為優雅的 Python 代碼：

**檔案**: Margin Call.xlsm
**作者**: lenovo
**最後修改**: 2022-07-04 23:13:13

**目標**:
1. 理解業務邏輯（不是機械轉換公式）
2. 識別計算模型類型（例如：期權定價、風險計算等）
3. 生成可維護、可測試的 Python 類
4. 優化重複計算（向量化、緩存）
5. 保持計算結果與 Excel 完全一致

# Excel 工作簿概覽

## 基本信息
- **工作表數量**: 1
- **工作表名稱**: Sheet1
- **總儲存格數**: 58
- **公式數量**: 13
- **包含 VBA**: 是

## 公式複雜度分佈
- **簡單**: 12 個
- **中等**: 0 個
- **複雜**: 1 個

# 業務邏輯分析

基於使用的 Excel 函數，推測可能的業務場景：

- 可能涉及 **期權定價**（Black-Scholes 模型）
- 可能涉及 **風險度量**（波動率、標準差）

**使用的主要函數**: EXP, LN, NORMSDIST, SQRT, STDEV

# 數據流程

**階段 1: 輸入參數** (45 個儲存格)
  - 示例: Sheet1!B3, Sheet1!C3, Sheet1!D3, Sheet1!E3, Sheet1!F3 ... (共 45 個)
**階段 2: 中間計算** (8 個儲存格)
  - 示例: Sheet1!I20, Sheet1!I21, Sheet1!I26, Sheet1!I31, Sheet1!I32 ... (共 8 個)
**階段 3: 輸出結果** (5 個儲存格)
  - 示例: Sheet1!E1, Sheet1!B7, Sheet1!I18, Sheet1!I27, Sheet1!I36

**建議**:
- 輸入參數應作為類的構造函數參數或 setter 方法
- 中間計算可以是私有方法或屬性（使用 @property 或 @cached_property）
- 輸出結果應作為公開方法或屬性

# 關鍵公式詳情

以下是最重要/複雜的公式（前 10 個）：

### Sheet1!I31
```excel
=LN(I24/(I20*EXP(-I19*I15)))/(I25*SQRT(I15))+I25*SQRT(I15)/2
```
- **依賴**: I20, I15, I25, I24, I19
- **函數**: SQRT, EXP, LN
- **複雜度**: high

### Sheet1!I35
```excel
=I24*I33-I20*EXP(-I15*I19)*I34
```
- **依賴**: I20, I15, I34, I33, I24
- **函數**: EXP
- **複雜度**: low

### Sheet1!I18
```excel
=STDEV(U12:U35)*SQRT(12)
```
- **依賴**: U12:U35
- **函數**: SQRT, STDEV
- **複雜度**: low

### Sheet1!I27
```excel
=(1-NORMSDIST(I26))/2
```
- **依賴**: I26
- **函數**: NORMSDIST
- **複雜度**: low

### Sheet1!I26
```excel
=(I24-I20)/(I24*I25)
```
- **依賴**: I24, I20, I25
- **函數**: 
- **複雜度**: low

### Sheet1!I32
```excel
=I31-I25*SQRT(I15)
```
- **依賴**: I15, I31, I25
- **函數**: SQRT
- **複雜度**: low

### Sheet1!I33
```excel
=NORMSDIST(I31)
```
- **依賴**: I31
- **函數**: NORMSDIST
- **複雜度**: low

### Sheet1!I34
```excel
=NORMSDIST(I32)
```
- **依賴**: I32
- **函數**: NORMSDIST
- **複雜度**: low

### Sheet1!B7
```excel
=(B3+B4)/B5
```
- **依賴**: B5, B3, B4
- **函數**: 
- **複雜度**: low

### Sheet1!I20
```excel
=I13+I14/2
```
- **依賴**: I14, I13
- **函數**: 
- **複雜度**: low


**完整公式列表**: 共 13 個公式（已省略部分簡單公式）

# 重複模式分析

未檢測到明顯的重複模式。所有公式都是獨立計算。

# VBA 代碼

**包含 VBA**: 是

VBA 代碼已檢測到，詳細分析需要 python-vba 庫

**建議**:
- 將 VBA 的業務邏輯整合到 Python 類的方法中
- VBA 的 Sub/Function 可以轉換為 Python 方法
- 注意 VBA 可能修改的儲存格（副作用）

# 依賴關係分析

## 計算順序
共 25 個計算步驟（已按依賴順序排列）

**前 10 步**:
Sheet1!E1, Sheet1!B5, Sheet1!B3, Sheet1!B4, Sheet1!B7, Sheet1!U12:U35, Sheet1!I18, Sheet1!I14, Sheet1!I13, Sheet1!I20

## 核心節點（被多次引用）
- **Sheet1!I20**: 被 3 個儲存格依賴
- **Sheet1!I24**: 被 3 個儲存格依賴
- **Sheet1!I25**: 被 3 個儲存格依賴
- **Sheet1!I15**: 被 3 個儲存格依賴
- **Sheet1!I31**: 被 2 個儲存格依賴

**建議**:
- 按照計算順序組織代碼邏輯
- 核心節點應該用 `@cached_property` 緩存結果

# 輸出要求

請生成以下內容：

## 1. Python 類定義

```python
class [ModelName]:
    """
    描述這個模型的業務含義
    
    原始來源: Excel 工作簿 [filename]
    """
    
    def __init__(self, ...):
        """初始化輸入參數"""
        pass
    
    @property
    def result(self):
        """主要計算結果"""
        pass
```

## 2. 關鍵方法

為每個重要的計算步驟創建方法，附上清晰的 docstring。

## 3. 單元測試

```python
def test_against_excel():
    """使用 Excel 的實際值驗證結果"""
    model = [ModelName](...)
    assert np.isclose(model.result, [excel_value], rtol=1e-5)
```

## 4. 使用示例

展示如何使用這個類。

# 代碼風格要求

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
   - 每個方法只做一件事

# 驗證要求

生成的 Python 代碼必須產生與 Excel 完全一致的結果。

## 關鍵驗證點

以下儲存格的計算結果必須與 Excel 一致（誤差 < 0.01%）：

- **Sheet1!E1**: `=1+1+2...`
- **Sheet1!B7**: `=(B3+B4)/B5...`
- **Sheet1!I18**: `=STDEV(U12:U35)*SQRT(12)...`
- **Sheet1!I20**: `=I13+I14/2...`
- **Sheet1!I21**: `=I16*I17...`

## 測試數據

使用 Excel 中的實際輸入值進行測試，確保：
1. 數值精度一致（建議使用 `np.isclose` 比較浮點數）
2. 邊界情況處理正確
3. 錯誤情況有適當的異常處理

## 性能要求

- 單次計算應在 < 100ms 內完成
- 批量計算應使用向量化，支持 10000+ 行數據