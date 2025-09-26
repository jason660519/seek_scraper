# Seek職位爬蟲項目 - 重構後架構

## 項目結構

```
seek-job-crawler/
├── src/                          # 源代碼目錄
│   ├── scrapers/                 # 爬蟲模組
│   │   ├── __init__.py
│   │   └── seek_crawler.py       # 主要的Seek爬蟲實現
│   ├── parsers/                  # 解析器模組
│   │   ├── __init__.py
│   │   └── job_parser.py         # HTML解析器
│   ├── utils/                    # 工具模組
│   │   ├── __init__.py
│   │   ├── seek_url_builder.py   # URL構建器
│   │   ├── logger.py             # 日誌工具
│   │   └── config.py             # 配置文件
│   ├── models/                   # 數據模型（可擴展）
│   │   └── __init__.py
│   ├── main_new.py               # 新的主程式
│   └── config.py                 # 配置管理
├── data/                         # 數據目錄
│   ├── raw/                      # 原始爬蟲數據
│   └── processed/                # 處理後的數據
├── logs/                         # 日誌文件
├── requirements.txt              # Python依賴
├── run_simple.py                 # 簡化運行腳本
└── README.md                     # 項目文檔
```

## 核心組件

### 1. SeekCrawler (`src/scrapers/seek_crawler.py`)
- 使用Playwright進行瀏覽器自動化
- 支持關鍵詞和地點搜索
- 自動保存原始數據（HTML、截圖、元數據）
- 每個職位獨立文件夾存儲

### 2. JobParser (`src/parsers/job_parser.py`)
- 使用BeautifulSoup解析HTML
- 提取結構化的職位信息
- 支持多種HTML結構的解析

### 3. SeekURLBuilder (`src/utils/seek_url_builder.py`)
- 構建符合Seek網站規則的URL
- 正確處理關鍵詞和地點格式
- 支持分頁參數

### 4. 配置管理 (`src/config.py`)
- 集中管理所有配置參數
- 支持環境變量覆蓋
- 提供配置驗證功能

## 使用方法

### 快速開始

1. 安裝依賴：
```bash
pip install -r requirements.txt
```

2. 安裝Playwright瀏覽器：
```bash
playwright install
```

3. 運行簡化版本：
```bash
python run_simple.py
```

### 自定義搜索

修改 `src/config.py` 中的配置：

```python
# 自定義關鍵詞
'default_keywords': ['data scientist', 'python developer'],

# 自定義地點  
'default_locations': ['Sydney NSW', 'Melbourne VIC'],

# 調整爬蟲參數
'max_pages': 3,  # 每個搜索組合的最大頁數
'delay_between_requests': 2,  # 請求間延遲
```

### 數據流程

1. **爬蟲階段**：從Seek網站提取職位信息
   - 保存HTML內容到 `data/raw/{公司名}_{職位名}_{時間戳}/`
   - 保存截圖和元數據
   - 每個職位獨立文件夾

2. **解析階段**：將原始HTML轉換為結構化數據
   - 提取關鍵字段（URL、標題、地點、薪資等）
   - 保存為JSON格式到 `data/processed/`

## 輸出格式

### 原始數據結構
```
data/raw/
├── CompanyName_JobTitle_20250926_143022/
│   ├── page.html          # 頁面HTML
│   ├── screenshot.png     # 頁面截圖
│   ├── metadata.json      # 元數據
│   └── company_logo.jpg   # 公司Logo
```

### 處理後數據格式
```json
[
  {
    "seek_url": "https://www.seek.com.au/job/12345678",
    "job_detail_title": "Senior Software Engineer",
    "job_detail_location": "Sydney NSW",
    "job_detail_classifications": "Information & Communication Technology",
    "job_detail_work_type": "Full Time",
    "job_detail_salary": "$120k - $140k",
    "jobAdDetails": "Job description here...",
    "scraped_at": "2025-09-26T14:30:22.123456",
    "company": "Tech Company Pty Ltd",
    "folder_name": "TechCompanyPtyLtd_SeniorSoftwareEngineer_20250926_143022"
  }
]
```

## 擴展功能

### 代理支持
在配置中啟用代理功能：
```python
'use_proxy': True,
'proxy_pool_size': 10,
```

### 反爬蟲機制
- 用戶代理輪換
- TLS指紋模擬
- 請求延遲隨機化
- 視口大小隨機化

### 錯誤處理
- 自動重試機制
- 超時處理
- 詳細的錯誤日誌
- 斷點續爬支持

## 注意事項

1. **遵守robots.txt**：確保爬蟲行為符合網站規定
2. **請求頻率**：設置適當的延遲避免對網站造成負擔
3. **數據使用**：僅用於個人學習和研究目的
4. **法律合規**：遵守相關法律法規

## 故障排除

### 常見問題

1. **瀏覽器啟動失敗**
   - 確保已安裝Playwright瀏覽器：`playwright install`
   - 檢查系統依賴

2. **頁面加載超時**
   - 增加timeout配置
   - 檢查網絡連接

3. **找不到職位元素**
   - 檢查Seek網站結構是否變化
   - 更新選擇器配置

4. **數據解析錯誤**
   - 檢查HTML結構
   - 查看日誌了解詳細錯誤