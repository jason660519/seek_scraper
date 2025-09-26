"""
Playwright 爬蟲實現

使用 Playwright 進行網頁爬取，具備反爬蟲機制。
"""

import asyncio
import json
import logging
import random
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth import stealth_async

from ..models import JobPost, SearchCriteria
from ..services.proxy_manager import ProxyManager, ProxyConfig


class AntiCrawlingConfig:
    """反爬蟲配置"""
    
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
        ]
        
        # 請求延遲配置
        self.min_delay = 2.0  # 最小延遲（秒）
        self.max_delay = 5.0  # 最大延遲（秒）
        self.page_load_timeout = 30000  # 頁面加載超時（毫秒）
        
        # 瀏覽器配置
        self.viewport = {"width": 1920, "height": 1080}
        self.locale = "en-AU"
        self.timezone_id = "Australia/Sydney"
        
        # 重試配置
        self.max_retries = 3
        self.retry_delay = 1.0
        
        # 反檢測配置
        self.enable_stealth = True
        self.block_webrtc = True
        self.block_plugins = True
        self.disable_web_security = False


class PlaywrightScraper:
    """
    Playwright 爬蟲
    
    使用 Playwright 進行網頁爬取，具備反爬蟲機制。
    """
    
    def __init__(self, proxy_manager: Optional[ProxyManager] = None, logger: Optional[logging.Logger] = None):
        """
        初始化 Playwright 爬蟲
        
        Args:
            proxy_manager: 代理管理器
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.proxy_manager = proxy_manager
        self.config = AntiCrawlingConfig()
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.visited_urls: Set[str] = set()
        
    async def __aenter__(self):
        """異步上下文管理器進入"""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器退出"""
        await self.close()
        
    async def start(self) -> None:
        """啟動瀏覽器"""
        self.logger.info("啟動 Playwright 瀏覽器...")
        
        try:
            self.playwright = await async_playwright().start()
            
            # 配置瀏覽器
            browser_config = await self._get_browser_config()
            
            # 啟動瀏覽器
            self.browser = await self.playwright.chromium.launch(**browser_config)
            
            # 創建上下文
            context_config = await self._get_context_config()
            self.context = await self.browser.new_context(**context_config)
            
            # 應用反檢測措施
            if self.config.enable_stealth:
                await self._apply_stealth_measures()
            
            # 創建頁面
            self.page = await self.context.new_page()
            
            self.logger.info("Playwright 瀏覽器啟動成功")
            
        except Exception as e:
            self.logger.error(f"啟動瀏覽器失敗: {e}")
            raise
    
    async def close(self) -> None:
        """關閉瀏覽器"""
        self.logger.info("關閉 Playwright 瀏覽器...")
        
        try:
            if self.page:
                await self.page.close()
            
            if self.context:
                await self.context.close()
            
            if self.browser:
                await self.browser.close()
            
            if self.playwright:
                await self.playwright.stop()
                
            self.logger.info("Playwright 瀏覽器已關閉")
            
        except Exception as e:
            self.logger.error(f"關閉瀏覽器失敗: {e}")
    
    async def _get_browser_config(self) -> Dict[str, Any]:
        """獲取瀏覽器配置"""
        config = {
            "headless": False,  # 調試時設為 False
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--allow-running-insecure-content",
                "--disable-features=InterestCohortFeaturePolicy",
                "--disable-features=InterestCohortAPI",
                "--disable-features=FederatedLearningOfCohorts",
                "--disable-features=FlocIdComputedEventLogging",
                "--disable-features=FlocIdEventLogging",
                "--disable-features=TrustTokens",
                "--disable-features=TrustTokensAlwaysAllowIssuance",
                "--disable-features=PrivateAggregationApi",
                "--disable-features=PrivateAggregationApiFledgeExtensions",
                "--disable-features=AttributionReportingCrossAppWeb",
                "--disable-features=ConversionMeasurement",
                "--disable-features=EventReporting"
            ]
        }
        
        # 配置代理
        if self.proxy_manager:
            proxy = self.proxy_manager.get_proxy()
            if proxy:
                config["proxy"] = self.proxy_manager.get_proxy_for_playwright(proxy)
        
        return config
    
    async def _get_context_config(self) -> Dict[str, Any]:
        """獲取上下文配置"""
        user_agent = random.choice(self.config.user_agents)
        
        return {
            "viewport": self.config.viewport,
            "user_agent": user_agent,
            "locale": self.config.locale,
            "timezone_id": self.config.timezone_id,
            "java_script_enabled": True,
            "ignore_https_errors": True,
            "bypass_csp": True,
            "permissions": ["geolocation"],
            "geolocation": {"latitude": -33.8688, "longitude": 151.2093},  # 悉尼
            "color_scheme": "light"
        }
    
    async def _apply_stealth_measures(self) -> None:
        """應用反檢測措施"""
        try:
            # 應用 stealth 腳本
            await stealth_async(self.page)
            
            # 自定義腳本
            await self.page.add_init_script("""
                // 覆蓋 navigator 屬性
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // 覆蓋 chrome 屬性
                Object.defineProperty(window, 'chrome', {
                    get: () => ({
                        runtime: {},
                        loadTimes: () => ({}),
                        csi: () => ({})
                    })
                });
                
                // 覆蓋 permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // 模擬插件
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // 模擬語言
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-AU', 'en-US', 'en']
                });
            """)
            
            self.logger.info("已應用反檢測措施")
            
        except Exception as e:
            self.logger.error(f"應用反檢測措施失敗: {e}")
    
    async def random_delay(self) -> None:
        """隨機延遲"""
        delay = random.uniform(self.config.min_delay, self.config.max_delay)
        self.logger.debug(f"等待 {delay:.2f} 秒...")
        await asyncio.sleep(delay)
    
    async def navigate_to_url(self, url: str, wait_until: str = "networkidle") -> bool:
        """
        導航到指定 URL
        
        Args:
            url: 目標 URL
            wait_until: 等待條件
            
        Returns:
            bool: 是否成功導航
        """
        try:
            self.logger.info(f"導航到: {url}")
            
            # 檢查是否已經訪問過
            if url in self.visited_urls:
                self.logger.warning(f"URL 已訪問過: {url}")
                return False
            
            # 隨機延遲
            await self.random_delay()
            
            # 導航到頁面
            await self.page.goto(
                url,
                wait_until=wait_until,
                timeout=self.config.page_load_timeout
            )
            
            # 添加到已訪問集合
            self.visited_urls.add(url)
            
            self.logger.info(f"成功導航到: {url}")
            return True
            
        except Exception as e:
            self.logger.error(f"導航失敗: {url} - {e}")
            return False
    
    async def save_page_content(self, output_path: Path) -> bool:
        """
        保存頁面內容
        
        Args:
            output_path: 輸出路徑
            
        Returns:
            bool: 是否成功保存
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存 HTML
            html_content = await self.page.content()
            html_path = output_path / "page.html"
            html_path.write_text(html_content, encoding='utf-8')
            
            # 保存截圖
            screenshot_path = output_path / "screenshot.png"
            await self.page.screenshot(path=str(screenshot_path), full_page=True)
            
            # 保存頁面資訊
            page_info = {
                "url": self.page.url,
                "title": await self.page.title(),
                "viewport": await self.page.viewport_size(),
                "user_agent": await self.page.evaluate("navigator.userAgent"),
                "timestamp": time.time()
            }
            
            info_path = output_path / "page_info.json"
            info_path.write_text(json.dumps(page_info, indent=2, ensure_ascii=False), encoding='utf-8')
            
            self.logger.info(f"頁面內容已保存到: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存頁面內容失敗: {e}")
            return False
    
    async def extract_job_links(self) -> List[str]:
        """
        提取工作連結
        
        Returns:
            List[str]: 工作連結列表
        """
        try:
            # 等待工作列表加載
            await self.page.wait_for_selector('[data-automation="jobTitle"]', timeout=10000)
            
            # 提取工作連結
            job_links = await self.page.evaluate("""
                () => {
                    const links = [];
                    const jobElements = document.querySelectorAll('[data-automation="jobTitle"] a');
                    jobElements.forEach(element => {
                        if (element.href) {
                            links.push(element.href);
                        }
                    });
                    return links;
                }
            """)
            
            self.logger.info(f"提取到 {len(job_links)} 個工作連結")
            return job_links
            
        except Exception as e:
            self.logger.error(f"提取工作連結失敗: {e}")
            return []
    
    async def extract_total_pages(self) -> int:
        """
        提取總頁數
        
        Returns:
            int: 總頁數
        """
        try:
            # 查找分頁元素
            pagination_elements = await self.page.query_selector_all('nav[aria-label="pagination"] a, [data-automation="pageNumber"]');
            
            if pagination_elements:
                # 提取頁碼
                page_numbers = []
                for element in pagination_elements:
                    text = await element.text_content()
                    if text and text.strip().isdigit():
                        page_numbers.append(int(text.strip()))
                
                if page_numbers:
                    total_pages = max(page_numbers)
                    self.logger.info(f"總頁數: {total_pages}")
                    return total_pages
            
            # 如果沒有找到分頁，檢查是否有 "下一頁" 按鈕
            next_button = await self.page.query_selector('[data-automation="pageNext"], a[aria-label="Next"]');
            if next_button:
                # 假設有很多頁，返回一個較大的數字
                self.logger.info("找到下一頁按鈕，假設有多頁")
                return 10  # 預設值
            
            self.logger.info("只有一頁")
            return 1
            
        except Exception as e:
            self.logger.error(f"提取總頁數失敗: {e}")
            return 1
    
    async def click_next_page(self) -> bool:
        """
        點擊下一頁
        
        Returns:
            bool: 是否成功點擊
        """
        try:
            # 查找下一頁按鈕
            next_button_selectors = [
                '[data-automation="pageNext"]',
                'a[aria-label="Next"]',
                'button:has-text("Next")',
                'a:has-text("Next")'
            ]
            
            next_button = None
            for selector in next_button_selectors:
                next_button = await self.page.query_selector(selector)
                if next_button:
                    break
            
            if not next_button:
                self.logger.info("未找到下一頁按鈕")
                return False
            
            # 檢查按鈕是否可用
            is_disabled = await next_button.get_attribute("disabled")
            if is_disabled:
                self.logger.info("下一頁按鈕已禁用")
                return False
            
            # 隨機延遲
            await self.random_delay()
            
            # 點擊下一頁
            await next_button.click()
            
            # 等待頁面加載
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            
            self.logger.info("成功點擊下一頁")
            return True
            
        except Exception as e:
            self.logger.error(f"點擊下一頁失敗: {e}")
            return False
    
    async def search_jobs(self, search_criteria: SearchCriteria) -> List[str]:
        """
        搜索工作
        
        Args:
            search_criteria: 搜索條件
            
        Returns:
            List[str]: 工作連結列表
        """
        try:
            # 構建搜索 URL
            search_url = self._build_search_url(search_criteria)
            self.logger.info(f"搜索 URL: {search_url}")
            
            # 導航到搜索頁面
            if not await self.navigate_to_url(search_url):
                return []
            
            all_job_links = []
            
            # 提取當前頁面的工作連結
            current_links = await self.extract_job_links()
            all_job_links.extend(current_links)
            
            # 獲取總頁數
            total_pages = await self.extract_total_pages()
            self.logger.info(f"總共 {total_pages} 頁")
            
            # 遍歷所有頁面
            for page_num in range(2, min(total_pages + 1, 6)):  # 限制最多爬取 5 頁
                self.logger.info(f"處理第 {page_num} 頁...")
                
                if not await self.click_next_page():
                    break
                
                # 提取當前頁面的工作連結
                current_links = await self.extract_job_links()
                all_job_links.extend(current_links)
                
                # 隨機延遲
                await self.random_delay()
            
            self.logger.info(f"總共找到 {len(all_job_links)} 個工作")
            return all_job_links
            
        except Exception as e:
            self.logger.error(f"搜索工作失敗: {e}")
            return []
    
    def _build_search_url(self, search_criteria: SearchCriteria) -> str:
        """
        構建搜索 URL
        
        Args:
            search_criteria: 搜索條件
            
        Returns:
            str: 搜索 URL
        """
        base_url = "https://www.seek.com.au"
        
        # 關鍵詞
        keyword = search_criteria.keywords.replace(" ", "-")
        
        # 位置
        location = ""
        if search_criteria.location:
            location = f"/in-All-{search_criteria.location}"
        
        # 構建 URL
        url = f"{base_url}/{keyword}-jobs{location}"
        
        # 添加查詢參數
        params = []
        
        if search_criteria.job_type:
            params.append(f"worktype={search_criteria.job_type}")
        
        if search_criteria.salary_range:
            if search_criteria.salary_range.min_salary:
                params.append(f"salaryrange={search_criteria.salary_range.min_salary}-{search_criteria.salary_range.max_salary or ''}")
        
        if params:
            url += "?" + "&".join(params)
        
        return url
    
    async def extract_job_details(self) -> Optional[Dict[str, Any]]:
        """
        提取工作詳情
        
        Returns:
            Optional[Dict[str, Any]]: 工作詳情
        """
        try:
            # 等待頁面加載
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            
            # 提取工作詳情
            job_details = await self.page.evaluate("""
                () => {
                    const details = {};
                    
                    // 工作標題
                    const titleElement = document.querySelector('[data-automation="job-detail-title"], h1');
                    details.title = titleElement ? titleElement.textContent.trim() : '';
                    
                    // 公司名稱
                    const companyElement = document.querySelector('[data-automation="job-detail-company"], [data-automation="advertiser-name"]');
                    details.company = companyElement ? companyElement.textContent.trim() : '';
                    
                    // 位置
                    const locationElement = document.querySelector('[data-automation="job-detail-location"], [data-automation="job-location"]');
                    details.location = locationElement ? locationElement.textContent.trim() : '';
                    
                    // 工作類型
                    const workTypeElement = document.querySelector('[data-automation="job-detail-work-type"], [data-automation="job-work-type"]');
                    details.work_type = workTypeElement ? workTypeElement.textContent.trim() : '';
                    
                    // 薪資
                    const salaryElement = document.querySelector('[data-automation="job-detail-salary"], [data-automation="job-salary"]');
                    details.salary = salaryElement ? salaryElement.textContent.trim() : '';
                    
                    // 分類
                    const classificationElements = document.querySelectorAll('[data-automation="job-detail-classification"] a, [data-automation="job-classification"] a');
                    details.classifications = Array.from(classificationElements).map(el => el.textContent.trim()).join(', ');
                    
                    // 工作詳情
                    const jobDetailsElement = document.querySelector('[data-automation="jobAdDetails"], [data-automation="job-description"]');
                    details.job_details = jobDetailsElement ? jobDetailsElement.innerHTML : '';
                    
                    // 發布日期
                    const dateElement = document.querySelector('[data-automation="job-detail-date"], [data-automation="job-date"]');
                    details.posted_date = dateElement ? dateElement.textContent.trim() : '';
                    
                    // 當前 URL
                    details.url = window.location.href;
                    
                    return details;
                }
            """)
            
            # 清理數據
            job_details = self._clean_job_details(job_details)
            
            self.logger.info(f"成功提取工作詳情: {job_details.get('title', 'Unknown')}")
            return job_details
            
        except Exception as e:
            self.logger.error(f"提取工作詳情失敗: {e}")
            return None
    
    def _clean_job_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理工作詳情數據
        
        Args:
            details: 原始詳情數據
            
        Returns:
            Dict[str, Any]: 清理後的詳情數據
        """
        cleaned = {}
        
        for key, value in details.items():
            if isinstance(value, str):
                # 移除多餘的空白字符
                cleaned_value = ' '.join(value.split())
                # 移除 HTML 標籤
                cleaned_value = cleaned_value.replace('<br>', '\n').replace('<br/>', '\n')
                cleaned[key] = cleaned_value
            else:
                cleaned[key] = value
        
        return cleaned
    
    async def scrape_job_details(self, job_url: str, output_dir: Path) -> Optional[Dict[str, Any]]:
        """
        爬取工作詳情
        
        Args:
            job_url: 工作 URL
            output_dir: 輸出目錄
            
        Returns:
            Optional[Dict[str, Any]]: 工作詳情
        """
        try:
            self.logger.info(f"爬取工作詳情: {job_url}")
            
            # 導航到工作詳情頁面
            if not await self.navigate_to_url(job_url):
                return None
            
            # 提取工作詳情
            job_details = await self.extract_job_details()
            
            if job_details:
                # 創建輸出目錄
                company_name = job_details.get('company', 'Unknown').replace(' ', '_')
                job_title = job_details.get('title', 'Unknown').replace(' ', '_')
                timestamp = str(int(time.time()))
                
                folder_name = f"{company_name}_{job_title}_{timestamp}"
                job_output_dir = output_dir / folder_name
                
                # 保存頁面內容
                await self.save_page_content(job_output_dir)
                
                # 保存工作詳情
                details_path = job_output_dir / "job_details.json"
                details_path.write_text(
                    json.dumps(job_details, indent=2, ensure_ascii=False),
                    encoding='utf-8'
                )
                
                self.logger.info(f"工作詳情已保存到: {job_output_dir}")
                return job_details
            
            return None
            
        except Exception as e:
            self.logger.error(f"爬取工作詳情失敗: {e}")
            return None