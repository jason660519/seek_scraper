# 專案結構與命名規範

本文檔定義了 SEEK 爬蟲專案的標準目錄結構和檔案命名慣例，以確保專案的一致性與可維護性。

## 🗂️ 目錄結構規劃

專案採用模組化的目錄結構，將不同功能的程式碼和資料分離。

```text
seek-job-crawler/
├── .github/               # GitHub Actions CI/CD 工作流程
├── .vscode/               # VS Code 編輯器設定
├── src/                   # 專案原始碼
│   ├── scrapers/          # 爬蟲核心邏輯
│   ├── parsers/           # HTML/JSON 解析模組
│   ├── models/            # Pydantic 資料模型
│   ├── utils/             # 通用工具函式
│   ├── config/            # 設定檔管理
│   ├── services/          # 外部服務 (資料庫, 快取)
│   └── main.py            # 專案進入點
├── data/                  # 爬取資料
│   ├── raw/               # 原始未處理資料 (HTML, JSON)
│   ├── processed/         # 清理後的結構化資料 (CSV, JSON)
│   └── logs/              # 應用程式日誌
├── tests/                 # 單元測試與整合測試
├── docs/                  # 專案文件
├── docker/                # Docker 相關配置 (Dockerfile, docker-compose.yml)
├── scripts/               # 輔助腳本 (部署, 資料遷移)
├── .env.example           # 環境變數範本
├── .gitignore             # Git 忽略檔案清單
├── requirements.txt       # Python 依賴套件
└── README.md              # 專案說明文件
```

## 📄 檔案命名規範

標準化的檔案命名有助於快速定位和管理資料。

### 原始資料檔案

- **HTML**: `seek_raw_{keyword}_{location}_page{page_number}_{timestamp}.html`
  - *範例*: `seek_raw_Data-Analyst_Sydney_page01_20231120T143000Z.html`
- **JSON API**: `seek_api_raw_{keyword}_{location}_{timestamp}.json`
  - *範例*: `seek_api_raw_Data-Analyst_Sydney_20231120T143000Z.json`

### 處理後資料檔案

- **CSV**: `seek_jobs_processed_{keyword}_{location}_{timestamp}.csv`
  - *範例*: `seek_jobs_processed_Data-Analyst_Sydney_20231120T143000Z.csv`
- **JSON**: `seek_jobs_processed_{keyword}_{location}_{timestamp}.json`
  - *範例*: `seek_jobs_processed_Data-Analyst_Sydney_20231120T143000Z.json`

### 日誌檔案

- **應用日誌**: `seek_crawler_{date}.log`
  - *範例*: `seek_crawler_2023-11-20.log`
- **錯誤日誌**: `seek_error_{date}.log`
  - *範例*: `seek_error_2023-11-20.log`

**命名約定**:
- `{keyword}` 和 `{location}` 應進行 slugify 處理 (例如，"Data Analyst" 變為 "data-analyst")。
- `{timestamp}` 使用 ISO 8601 格式 (`YYYYMMDDTHHMMSSZ`)。
- `{date}` 使用 `YYYY-MM-DD` 格式。
