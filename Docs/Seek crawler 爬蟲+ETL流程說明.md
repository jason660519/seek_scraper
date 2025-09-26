# Seek Crawler 爬蟲 + ETL 流程說明

## 系統架構概覽

本系統採用模組化設計，包含三個主要元件：URL 建構器、爬蟲引擎、ETL 處理器，確保高可維護性與擴展性。

## 核心元件

### 1. 代理 IP 池管理
- **位置**: `proxy_management/` 目錄
- **功能**: 自動抓取並驗證有效代理 IP
- **更新頻率**: 定時任務自動更新
- **整合方式**: 爬蟲自動從池中獲取可用代理

### 2. 指紋池系統

#### 2.1 瀏覽器指紋池
- **工具**: [`scrapfly/fingerprint-generator`](https://github.com/scrapfly/fingerprint-generator)
- **目的**: 生成真實的瀏覽器指紋，避免被反爬蟲機制識別
- **安裝**: `pip install fpgen`
- **使用**: 自動生成 Windows + Chrome 等組合的指紋數據

#### 2.2 TLS 指紋池
- **工具**: `curl_cffi` 模組
- **目的**: 模擬真實的 TLS 握手指紋
- **功能**: 避免基於 TLS 指紋的封鎖機制

### 3. HTML 解析器
- **工具**: [`Pandoc`](https://github.com/jgm/pandoc)
- **功能**: HTML to Markdown 轉換，便於後續資料處理
- **安裝**: 需額外安裝 Pandoc 二進制文件

### 4. 反爬蟲機制
- **框架**: Scrapy 內建反偵測機制
- **策略**: 
  - 隨機延遲請求
  - 自動旋轉 User-Agent
  - 代理 IP 自動切換
  - 指紋數據隨機化

## Seek 網站 URL 結構分析

Seek 網站的 URL 具有高度規律性，無需登入即可存取：

### 基本搜尋模式
```
# 全國搜尋 - 第一頁
https://www.seek.com.au/{關鍵詞}-jobs

# 全國搜尋 - 分頁
https://www.seek.com.au/{關鍵詞}-jobs?page={頁碼}

# 地區搜尋 - 第一頁
https://www.seek.com.au/{關鍵詞}-jobs/in-All-{地區}

# 地區搜尋 - 分頁
https://www.seek.com.au/{關鍵詞}-jobs/in-All-{地區}?page={頁碼}
```

### 實際範例
```
# AI 工作全國搜尋
https://www.seek.com.au/AI-jobs
https://www.seek.com.au/AI-jobs?page=2

# AI 工作悉尼地區
https://www.seek.com.au/AI-jobs/in-All-Sydney-NSW
https://www.seek.com.au/AI-jobs/in-All-Sydney-NSW?page=2

# 土木工程師墨爾本地區
https://www.seek.com.au/civil-engineer-jobs/in-All-Melbourne-VIC
https://www.seek.com.au/civil-engineer-jobs/in-All-Melbourne-VIC?page=2
```

### URL 建構規則
1. **關鍵詞處理**: 空格替換為連字號，全小寫
2. **地區處理**: 空格替換為連字號，保持原始大小寫
3. **分頁參數**: `?page={number}`，從 1 開始

## ETL 資料流程

### Step 1: Raw Data 擷取 (原始資料收集)

#### 流程說明
1. **關鍵詞輸入**: 使用者提供搜尋關鍵詞列表
2. **地區篩選**: 可選擇特定地區或全國搜尋
3. **分頁處理**: 自動爬取所有分頁結果
4. **詳情頁擷取**: 進入每個工作詳情頁面獲取完整資訊

#### 資料收集內容
- HTML 原始碼
- CSS 樣式文件
- JavaScript 腳本
- 公司 Logo 圖片
- 截圖存檔
- 頁面元數據 (URL、時間戳等)

#### 檔案結構
```
data/raw/
├── {公司名稱}_{職位名稱}_{YYYYMMDD_HHMMSS}/
│   ├── index.html          # 詳情頁 HTML
│   ├── screenshot.png      # 頁面截圖
│   ├── metadata.json       # 元數據資訊
│   ├── company_logo.jpg    # 公司 Logo
│   └── assets/              # 相關資源文件
│       ├── styles.css
│       └── scripts.js
```

#### 技術實現
- **工具**: Playwright (處理動態載入內容)
- **代理**: 自動切換代理 IP
- **指紋**: 隨機化瀏覽器指紋
- **延遲**: 模擬真人操作節奏

### Step 2: Processed Data 解析 (結構化資料處理)

#### 解析目標
將 HTML 轉換為結構化的 JSON/CSV 格式，包含以下欄位：

| 欄位順序 | 欄位名稱 | 說明 | XPath/選擇器 |
|---------|---------|------|-------------|
| 1 | Job URL | 工作詳情頁連結 | 頁面 URL |
| 2 | Job Title | 職位名稱 | `[data-automation-id="job-detail-title"]` |
| 3 | Location | 工作地點 | `[data-automation-id="job-detail-location"]` |
| 4 | Classification | 工作分類 | `[data-automation-id="job-detail-classifications"]` |
| 5 | Work Type | 工作類型 | `[data-automation-id="job-detail-work-type"]` |
| 6 | Salary | 薪資範圍 | `[data-automation-id="job-detail-salary"]` |
| 7 | Job Details | 工作詳情描述 | `[data-automation-id="jobAdDetails"]` |

#### 輸出格式

##### CSV 格式
```csv
Job URL,Job Title,Location,Classification,Work Type,Salary,Job Details
https://www.seek.com.au/job/12345,AI Engineer,Sydney NSW,Information & Communication Technology,Full Time,"$150k - $180k",詳細工作描述...
```

##### JSON 格式
```json
{
  "jobs": [
    {
      "url": "https://www.seek.com.au/job/12345",
      "title": "AI Engineer",
      "location": "Sydney NSW",
      "classification": "Information & Communication Technology",
      "work_type": "Full Time",
      "salary": "$150k - $180k",
      "details": "詳細工作描述...",
      "scraped_at": "2025-09-26T10:30:00Z",
      "company": "Example Company"
    }
  ]
}
```

#### 檔案儲存位置
```
data/processed/
├── seek_jobs_{YYYYMMDD}_{HHMMSS}.csv    # CSV 輸出
├── seek_jobs_{YYYYMMDD}_{HHMMSS}.json   # JSON 輸出
└── processing_stats.json                 # 處理統計資訊
```

## 重構設計原則

### 1. 模組化架構
- **URL 建構器**: 獨立處理 URL 生成邏輯
- **爬蟲引擎**: 專注於資料擷取
- **ETL 處理器**: 負責資料轉換與儲存
- **工具函數**: 可重用的輔助功能

### 2. 錯誤處理
- **重試機制**: 失敗請求自動重試
- **異常記錄**: 詳細的錯誤日誌
- **優雅降級**: 部分失敗不影響整體流程

### 3. 效能優化
- **非同步處理**: 支援並發請求
- **快取機制**: 避免重複請求
- **增量更新**: 只處理新資料

### 4. 可維護性
- **清晰命名**: 語義化的變數和函數名
- **單一職責**: 每個函數只做一件事
- **文檔完整**: 詳細的註解和說明

## 實作建議

### 開發順序
1. **基礎工具**: 先實作 URL 建構器和基礎爬蟲
2. **資料擷取**: 實作 Raw Data 收集功能
3. **資料解析**: 開發 HTML to JSON/CSV 轉換器
4. **整合測試**: 確保各模組協同工作
5. **效能優化**: 加入代理池和指紋系統

### 程式碼結構
```
src/
├── utils/
│   ├── seek_url_builder.py      # URL 建構器
│   └── logger.py               # 日誌工具
├── scrapers/
│   ├── seek_crawler.py         # 主要爬蟲
│   └── playwright_scraper.py  # Playwright 封裝
├── parsers/
│   └── job_parser.py           # HTML 解析器
└── models/
    └── job_data.py             # 資料模型
```

這個重新設計的流程說明更加清晰、結構化，並且基於實際的網站行為和最佳實踐。接下來我們可以根據這個架構來實作具體的程式碼。

