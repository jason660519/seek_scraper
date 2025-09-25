# 🛠️ 技術棧與依賴

本文檔概述了 SEEK 爬蟲專案所使用的核心技術、Python 依賴套件以及建議的進階技術選項。

## 核心依賴套件

以下是專案運行的基礎 Python 套件，建議將其固定在 `requirements.txt` 中。

```ini
# 核心爬蟲與網路請求
requests>=2.31.0          # 同步 HTTP 請求
httpx>=0.25.0             # 異步 HTTP 請求，支援 HTTP/2
beautifulsoup4>=4.12.0    # HTML/XML 解析
lxml>=4.9.0               # 高效能 XML/HTML 解析器
playwright>=1.39.0        # 現代化瀏覽器自動化，用於處理動態頁面
Scrapy                    # 成熟的 Python 爬蟲框架，提供完整的爬取生命週期管理。

# 資料處理與驗證
pandas>=2.0.0             # 資料結構與分析
pydantic>=2.4.0           # 資料驗證、序列化與設定管理
python-dateutil>=2.8.0    # 強大的日期時間解析

# 異步處理
asyncio>=3.4.3            # Python 標準異步 I/O 框架

# 資料庫與快取
sqlalchemy>=2.0.0         # SQL 工具包與 ORM
psycopg2-binary>=2.9.0    # PostgreSQL 資料庫驅動
redis>=5.0.0              # In-memory 快取與訊息代理

# 其他工具
python-dotenv>=1.0.0      # 環境變數管理
rich>=13.6.0              # 美觀的終端輸出與日誌
```

### 🗄️ 儲存與雲端服務

- **MinIO**: [GitHub](https://github.com/minio/minio) - 相容 S3 的開源物件儲存，適合大規模儲存原始 HTML 或圖片。
- **PostgreSQL**: 強大的開源關聯式資料庫，適合儲存結構化的工作資訊。

- **ClickHouse**: 高效能的分析型資料庫，適用於大規模資料的即時查詢與分析。

### 🕷️ 反偵測技術棧

- **Scrapy**: [GitHub](https://github.com/scrapy/scrapy) - 成熟的 Python 爬蟲框架，提供完整的爬取生命週期管理。
- **Apify**: [GitHub](https://github.com/apify/fingerprint-suite) -這個 toolkit 可以 生成／inject 瀏覽器指紋，例如生成 HTTP headers、瀏覽器 JS API 裡的指紋訊號，然後在 Playwright 或 Puppeteer 裡注入這些指紋，讓自動化瀏覽器看起來像真實使用者。 用來模仿真實瀏覽器的 fingerprint，而不被反爬或偵測系統識破。 
- **curl_cffi**: [GitHub](https://github.com/yifeikong/curl_cffi) - 模擬瀏覽器 TLS/JA3 指紋，有效規避 Cloudflare 等 WAF。
- **ScrapFly**: [Website](https://github.com/scrapfly/fingerprint-generator) - fingerprint-generator，用於生成瀏覽器指紋，能有效幫助避免被檢測為爬蟲

### 🔄 任務調度與隊列

- **Celery**: [GitHub](https://github.com/celery/celery) - 分散式任務隊列，適用於異步執行大規模爬取任務。
- **Prefect**: [GitHub](https://github.com/PrefectHQ/prefect) - 現代化的資料工作流程自動化平台。
- **Airflow**: [GitHub](https://github.com/apache/airflow) - 成熟的開源工作流程管理平台。

### 📄 文件與資料提取

- **Pandoc**: [GitHub](https://github.com/jgm/pandoc) - 通用文件轉換器，可將 HTML 轉換為 Markdown 等格式。
- **PaddleOCR**: [GitHub](https://github.com/PaddlePaddle/PaddleOCR) - 領先的 OCR 工具庫，用於從圖片中提取文字。
- **PyPDF2**: 用於讀取和處理 PDF 檔案。
