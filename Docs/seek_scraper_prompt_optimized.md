# 澳洲 SEEK 求職網站爬蟲專案

## 📋 專案概述

本專案旨在開發一個企業級的 Python 爬蟲系統，用於從澳洲 SEEK 求職網站 (seek.com.au) 高效、穩定地提取職位列表資訊。系統設計目標是支援大規模資料收集、結構化處理與多格式輸出。

### 核心目標

- **自動化資料提取**: 每日自動爬取最新的職位資訊。
- **高品質資料**: 確保資料的準確性、完整性與一致性。
- **高擴展性架構**: 支援分散式部署與大規模爬取任務。
- **健壯性與容錯**: 具備企業級的錯誤處理、重試與監控機制。

---

## 📑 專案規格文件

為了確保專案的模組化與可維護性，詳細的技術規格已拆分到以下獨立文件中：

1. **[使用者搜尋參數 (`search_parameters_spec.json`)]](./search_parameters_spec.json)**
   - 定義了使用者可以自訂的搜尋條件，如關鍵字、地點、薪資範圍等。

2. **[資料結構規範 (`data_schema_spec.json`)]](./data_schema_spec.json)**
   - 使用 JSON Schema 精確定義了爬取資料的欄位、類型和約束。

3. **[專案結構與命名 (`project_structure_spec.md`)]](./project_structure_spec.md)**
   - 詳細說明了專案的目錄結構和檔案命名慣例。

4. **[技術棧與依賴 (`tech_stack_spec.md`)]](./tech_stack_spec.md)**
   - 列出了專案所需的核心 Python 套件和建議的進階技術選項。

5. **[系統架構設計 (`system_design_spec.md`)]](./system_design_spec.md)**
   - 闡述了系統的模組化架構、錯誤處理策略、反爬蟲機制和日誌系統。

---

## 🚀 快速開始

1. **安裝依賴**:

   ```bash
   pip install -r requirements.txt
   ```

2. **設定環境變數**:
   複製 `.env.example` 為 `.env` 並填寫必要的設定 (如資料庫連接字串、代理伺服器等)。

3. **執行爬蟲**:

   ```bash
   python src/main.py --keyword "Data Scientist" --location "Sydney"
   ```
