# 🏗️ 系統架構設計

本文檔闡述了 SEEK 爬蟲專案的軟體架構、關鍵模組設計、錯誤處理策略以及日誌系統。

## 模組化架構

系統採用模組化設計，將爬蟲流程分解為幾個獨立且可重用的組件。

```python
# --- 專案進入點: main.py ---
async def main():
    """
    協調整個爬取、解析和儲存流程。
    """
    # 1. 載入設定
    config = load_config()
    
    # 2. 初始化服務 (資料庫, 日誌)
    db = DatabaseService(config.db_url)
    logger = CrawlerLogger()
    
    # 3. 實例化爬蟲
    crawler = SeekCrawler(config, logger)
    
    # 4. 執行搜尋
    search_params = get_search_params_from_user()
    raw_pages = await crawler.search_jobs(search_params)
    
    # 5. 解析資料
    parser = JobParser()
    jobs = [parser.parse_job(page) for page in raw_pages]
    
    # 6. 儲存結果
    await db.save_jobs(jobs)

# --- 資料模型: models.py (使用 Pydantic) ---
class JobItem(BaseModel):
    """
    定義符合 data_schema_spec.json 規範的職位資料模型。
    提供資料驗證、序列化和預設值。
    """
    job_id: str
    title: str
    company: Optional[CompanyInfo] = None
    # ... 其他欄位

# --- 核心爬蟲: scrapers.py ---
class SeekCrawler:
    """
    封裝與 SEEK 網站的網路互動。
    """
    def __init__(self, config: CrawlerConfig, logger: CrawlerLogger):
        self.http_client = httpx.AsyncClient(...) # 配置代理、標頭、超時
        self.logger = logger

    async def search_jobs(self, params: SearchParams) -> List[str]:
        """執行搜尋並返回原始 HTML 頁面列表。"""

    async def fetch_job_details(self, job_url: str) -> str:
        """獲取單一職位的詳細 HTML 頁面。"""

# --- 解析器: parsers.py ---
class JobParser:
    """
    從原始 HTML 中提取結構化資料。
    """
    def parse_job_list(self, html: str) -> List[JobItem]:
        """從搜尋結果頁解析出工作列表。"""

    def parse_job_details(self, html: str) -> JobItem:
        """從職位詳情頁解析出完整資訊。"""
```

## 🛡️ 錯誤處理與反爬蟲策略

健壯的錯誤處理和反爬蟲機制是專案成功的關鍵。

### 智慧重試機制

使用 `tenacity` 或自訂裝飾器來實現指數退避重試。

```python
from tenacity import retry, stop_after_attempt, wait_random_exponential

@retry(
    wait=wait_random_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5)
)
async def fetch_url_with_retry(client: httpx.AsyncClient, url: str):
    """
    帶有指數退避重試機制的請求函式。
    """
    response = await client.get(url)
    response.raise_for_status() # 針對 4xx/5xx 狀態碼拋出異常
    return response
```

### 統一錯誤處理器

建立一個中央錯誤處理類別，用於分類和記錄不同類型的錯誤。

```python
class ErrorHandler:
    """
    統一處理爬取過程中的預期和非預期錯誤。
    """
    def __init__(self, logger: CrawlerLogger):
        self.logger = logger

    async def handle(self, error: Exception, context: dict):
        if isinstance(error, httpx.HTTPStatusError):
            await self._handle_http_error(error, context)
        elif isinstance(error, httpx.RequestError):
            await self._handle_network_error(error, context)
        else:
            await self._handle_generic_error(error, context)

    async def _handle_http_error(self, error: httpx.HTTPStatusError, context: dict):
        """處理 HTTP 4xx/5xx 錯誤，如速率限制、找不到頁面。"""
        if error.response.status_code == 429: # Too Many Requests
            self.logger.warning("Rate limit detected. Implementing cooldown.", extra=context)
            # 可以在此處觸發全域降溫或代理輪換
        else:
            self.logger.error(f"HTTP error: {error.response.status_code}", extra=context)

    # ... 其他錯誤處理方法
```

### 反爬蟲策略

1. **請求速率控制**: 在請求之間引入隨機延遲（例如，1-3秒），模擬人類瀏覽行為。
2. **User-Agent 輪換**: 維護一個包含最新瀏覽器 User-Agent 的列表，並在每次請求時隨機選擇。
3. **代理伺服器**: 使用高品質的住宅或數據中心代理池，並在請求失敗或被封鎖時自動輪換 IP。
4. **TLS/JA3 指紋模擬**: 使用 `curl_cffi` 等工具來模擬主流瀏覽器的 TLS 指紋，以規避 Cloudflare 等進階 WAF 的偵測。
5. **無頭瀏覽器**: 對於需要 JavaScript 渲染的頁面，使用 Playwright 並搭配反偵測插件（如 `playwright-stealth`）。

## 📈 日誌管理系統

使用 `rich` 和 Python 內建的 `logging` 模組來建立結構化的日誌系統。

```python
import logging
from rich.logging import RichHandler

class CrawlerLogger:
    """
    提供結構化、色彩豐富的日誌記錄功能。
    """
    def __init__(self, name="seek_crawler", level="INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 防止重複添加 handler
        if not self.logger.handlers:
            shell_handler = RichHandler()
            file_handler = logging.FileHandler(f"data/logs/{name}.log")
            
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(shell_handler)
            self.logger.addHandler(file_handler)

    def info(self, message: str, extra: dict = None):
        self.logger.info(message, extra=extra)

    def warning(self, message: str, extra: dict = None):
        self.logger.warning(message, extra=extra)

    def error(self, message: str, exc_info=True, extra: dict = None):
        self.logger.error(message, exc_info=exc_info, extra=extra)
```
