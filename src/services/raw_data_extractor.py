"""
ETL Raw 資料抓取服務

實現 SEEK 爬蟲的 Step 1：raw 檔案夾擷取功能。
每個工作創建獨立的 raw 檔案夾，包含 HTML、CSS、JS、圖片等所有相關資料。
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from typing import TYPE_CHECKING
from ..models import SearchCriteria
from ..services.proxy_manager import ProxyManager

if TYPE_CHECKING:
    from ..scrapers.playwright_scraper import PlaywrightScraper


class RawDataExtractor:
    """
    Raw 資料提取器
    
    負責從 SEEK 網站提取原始資料，包括：
    - HTML 頁面內容
    - CSS 樣式文件
    - JavaScript 腳本
    - 圖片和多媒體資源
    - 公司 logo
    - 其他相關資源
    """
    
    def __init__(self, output_dir: Path, proxy_manager: Optional[ProxyManager] = None, logger: Optional[logging.Logger] = None):
        """
        初始化 Raw 資料提取器
        
        Args:
            output_dir: 輸出目錄（通常是 data/raw/）
            proxy_manager: 代理管理器
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.output_dir = output_dir
        self.proxy_manager = proxy_manager
        self.scraper = None
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # 創建輸出目錄
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 資源下載配置
        self.download_resources = True
        self.resource_types = ["stylesheet", "script", "image", "font", "media"]
        self.downloaded_resources: set = set()
        
    async def __aenter__(self):
        """異步上下文管理器進入"""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器退出"""
        await self.cleanup()
    
    async def initialize(self) -> None:
        """初始化提取器"""
        self.logger.info("初始化 Raw 資料提取器...")
        
        try:
            # 創建 Playwright 實例
            self.playwright = await async_playwright().start()
            
            # 配置瀏覽器
            browser_config = await self._get_browser_config()
            
            # 啟動瀏覽器
            self.browser = await self.playwright.chromium.launch(**browser_config)
            
            # 創建上下文
            context_config = await self._get_context_config()
            self.context = await self.browser.new_context(**context_config)
            
            # 設置資源攔截器
            if self.download_resources:
                await self._setup_resource_interceptor()
            
            # 創建頁面
            self.page = await self.context.new_page()
            
            self.logger.info("Raw 資料提取器初始化完成")
            
        except Exception as e:
            self.logger.error(f"初始化提取器失敗: {e}")
            raise
    
    async def cleanup(self) -> None:
        """清理資源"""
        self.logger.info("清理 Raw 資料提取器...")
        
        try:
            if self.page:
                await self.page.close()
            
            if self.context:
                await self.context.close()
            
            if self.browser:
                await self.browser.close()
            
            if self.playwright:
                await self.playwright.stop()
                
            self.logger.info("Raw 資料提取器已清理完成")
            
        except Exception as e:
            self.logger.error(f"清理提取器失敗: {e}")
    
    async def _get_browser_config(self) -> Dict[str, Any]:
        """獲取瀏覽器配置"""
        config = {
            "headless": True,  # 後台運行
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process"
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
        return {
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "locale": "en-AU",
            "timezone_id": "Australia/Sydney",
            "java_script_enabled": True,
            "ignore_https_errors": True
        }
    
    async def _setup_resource_interceptor(self) -> None:
        """設置資源攔截器"""
        async def handle_route(route):
            try:
                request = route.request
                resource_type = request.resource_type
                url = request.url
                
                # 只下載配置的資源類型
                if resource_type in self.resource_types and url not in self.downloaded_resources:
                    self.downloaded_resources.add(url)
                    self.logger.debug(f"攔截資源: {url} (類型: {resource_type})")
                    
                    # 繼續請求
                    await route.continue_()
                else:
                    # 其他資源直接通過
                    await route.continue_()
                    
            except Exception as e:
                self.logger.error(f"處理資源攔截失敗: {e}")
                await route.continue_()
        
        # 設置路由
        await self.context.route("**/*", handle_route)
        self.logger.info("資源攔截器已設置")
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理後的文件名
        """
        import re
        
        # 移除非法字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # 限制長度
        if len(filename) > 200:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:200-len(ext)-1] + '.' + ext if ext else name[:200]
        
        return filename.strip()
    
    def _create_job_folder(self, company_name: str, job_title: str) -> Path:
        """
        創建工作資料夾
        
        Args:
            company_name: 公司名稱
            job_title: 職位名稱
            
        Returns:
            Path: 工作資料夾路徑
        """
        # 清理名稱
        clean_company = self._sanitize_filename(company_name)
        clean_title = self._sanitize_filename(job_title)
        
        # 創建時間戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 創建文件夾名稱
        folder_name = f"{clean_company}_{clean_title}_{timestamp}"
        
        # 創建文件夾路徑
        job_folder = self.output_dir / folder_name
        job_folder.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"創建工作資料夾: {job_folder}")
        return job_folder
    
    async def download_resource(self, url: str, output_path: Path) -> bool:
        """
        下載資源文件
        
        Args:
            url: 資源 URL
            output_path: 輸出路徑
            
        Returns:
            bool: 是否成功下載
        """
        try:
            import aiohttp
            
            # 創建會話
            timeout = aiohttp.ClientTimeout(total=60)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        # 創建父目錄
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # 保存文件
                        content = await response.read()
                        output_path.write_bytes(content)
                        
                        self.logger.debug(f"下載資源成功: {url} -> {output_path}")
                        return True
                    else:
                        self.logger.warning(f"下載資源失敗: {url} (狀態碼: {response.status})")
                        return False
                        
        except Exception as e:
            self.logger.error(f"下載資源失敗: {url} - {e}")
            return False
    
    async def extract_all_resources(self, job_folder: Path) -> Dict[str, Any]:
        """
        提取所有資源
        
        Args:
            job_folder: 工作資料夾
            
        Returns:
            Dict[str, Any]: 資源資訊
        """
        try:
            self.logger.info("提取所有資源...")
            
            resources_info = {
                "stylesheets": [],
                "scripts": [],
                "images": [],
                "fonts": [],
                "media": [],
                "other": []
            }
            
            # 獲取所有資源
            all_resources = await self.page.evaluate("""
                () => {
                    const resources = {
                        stylesheets: [],
                        scripts: [],
                        images: [],
                        fonts: [],
                        media: [],
                        other: []
                    };
                    
                    // 獲取樣式表
                    document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
                        if (link.href) resources.stylesheets.push(link.href);
                    });
                    
                    // 獲取腳本
                    document.querySelectorAll('script[src]').forEach(script => {
                        if (script.src) resources.scripts.push(script.src);
                    });
                    
                    // 獲取圖片
                    document.querySelectorAll('img[src]').forEach(img => {
                        if (img.src) resources.images.push(img.src);
                    });
                    
                    // 獲取字體
                    document.querySelectorAll('link[rel="preload"][as="font"]').forEach(link => {
                        if (link.href) resources.fonts.push(link.href);
                    });
                    
                    // 獲取媒體
                    document.querySelectorAll('video[src], audio[src]').forEach(media => {
                        if (media.src) resources.media.push(media.src);
                    });
                    
                    // 獲取其他資源
                    document.querySelectorAll('link[href]').forEach(link => {
                        if (link.href && !resources.stylesheets.includes(link.href) && !resources.fonts.includes(link.href)) {
                            resources.other.push(link.href);
                        }
                    });
                    
                    return resources;
                }
            """)
            
            # 下載資源
            resources_dir = job_folder / "resources"
            
            for resource_type, urls in all_resources.items():
                for url in urls:
                    try:
                        # 生成文件名
                        parsed_url = urlparse(url)
                        filename = self._sanitize_filename(parsed_url.path.split('/')[-1] or 'resource')
                        if not filename or '.' not in filename:
                            filename = f"resource_{int(time.time())}_{hash(url) % 10000}"
                        
                        # 創建輸出路徑
                        resource_path = resources_dir / resource_type / filename
                        
                        # 下載資源
                        if await self.download_resource(url, resource_path):
                            resources_info[resource_type].append({
                                "url": url,
                                "local_path": str(resource_path.relative_to(job_folder)),
                                "filename": filename
                            })
                        
                        # 隨機延遲，避免過快下載
                        await asyncio.sleep(random.uniform(0.1, 0.3))
                        
                    except Exception as e:
                        self.logger.warning(f"處理資源失敗: {url} - {e}")
                        continue
            
            self.logger.info(f"資源提取完成，共提取 {sum(len(items) for items in resources_info.values())} 個資源")
            return resources_info
            
        except Exception as e:
            self.logger.error(f"提取所有資源失敗: {e}")
            return {}
    
    async def extract_job_metadata(self, job_url: str) -> Dict[str, Any]:
        """
        提取工作元數據
        
        Args:
            job_url: 工作 URL
            
        Returns:
            Dict[str, Any]: 工作元數據
        """
        try:
            self.logger.info("提取工作元數據...")
            
            metadata = {
                "url": job_url,
                "title": await self.page.title(),
                "timestamp": datetime.now().isoformat(),
                "user_agent": await self.page.evaluate("navigator.userAgent"),
                "viewport": await self.page.viewport_size(),
                "cookies": await self.context.cookies(),
                "local_storage": await self.page.evaluate("() => Object.entries(localStorage)"),
                "session_storage": await self.page.evaluate("() => Object.entries(sessionStorage)"),
                "page_metrics": await self._get_page_metrics()
            }
            
            self.logger.info("工作元數據提取完成")
            return metadata
            
        except Exception as e:
            self.logger.error(f"提取工作元數據失敗: {e}")
            return {}
    
    async def _get_page_metrics(self) -> Dict[str, Any]:
        """
        獲取頁面性能指標
        
        Returns:
            Dict[str, Any]: 頁面指標
        """
        try:
            metrics = await self.page.evaluate("""
                () => {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    const paint = performance.getEntriesByType('paint');
                    
                    return {
                        load_time: navigation ? navigation.loadEventEnd - navigation.loadEventStart : null,
                        dom_content_loaded: navigation ? navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart : null,
                        first_paint: paint.find(entry => entry.name === 'first-paint')?.startTime || null,
                        first_contentful_paint: paint.find(entry => entry.name === 'first-contentful-paint')?.startTime || null,
                        memory: performance.memory ? {
                            used_js_heap_size: performance.memory.usedJSHeapSize,
                            total_js_heap_size: performance.memory.totalJSHeapSize,
                            js_heap_size_limit: performance.memory.jsHeapSizeLimit
                        } : null
                    };
                }
            """)
            
            return metrics
            
        except Exception as e:
            self.logger.warning(f"獲取頁面指標失敗: {e}")
            return {}
    
    async def extract_job_page(self, job_url: str, company_name: str = "Unknown", job_title: str = "Unknown") -> Optional[Path]:
        """
        提取工作頁面
        
        Args:
            job_url: 工作 URL
            company_name: 公司名稱
            job_title: 職位名稱
            
        Returns:
            Optional[Path]: 工作資料夾路徑，如果失敗返回 None
        """
        try:
            self.logger.info(f"提取工作頁面: {job_url}")
            
            # 導航到工作頁面
            self.logger.info(f"導航到工作頁面: {job_url}")
            await self.page.goto(job_url, wait_until="networkidle", timeout=30000)
            
            # 等待頁面加載
            await self.page.wait_for_timeout(2000)  # 額外等待 2 秒
            
            # 提取實際的公司名稱和職位名稱（如果可能的話）
            try:
                actual_company = await self.page.evaluate("""
                    () => {
                        const companyElement = document.querySelector('[data-automation="job-detail-company"], [data-automation="advertiser-name"]');
                        return companyElement ? companyElement.textContent.trim() : '';
                    }
                """)
                
                actual_title = await self.page.evaluate("""
                    () => {
                        const titleElement = document.querySelector('[data-automation="job-detail-title"], h1');
                        return titleElement ? titleElement.textContent.trim() : '';
                    }
                """)
                
                if actual_company:
                    company_name = actual_company
                if actual_title:
                    job_title = actual_title
                    
            except Exception as e:
                self.logger.warning(f"提取實際名稱失敗: {e}")
            
            # 創建工作資料夾
            job_folder = self._create_job_folder(company_name, job_title)
            
            # 保存主要 HTML
            main_html_path = job_folder / "index.html"
            html_content = await self.page.content()
            main_html_path.write_text(html_content, encoding='utf-8')
            self.logger.info(f"保存主 HTML: {main_html_path}")
            
            # 保存截圖
            screenshot_path = job_folder / "screenshot.png"
            await self.page.screenshot(path=str(screenshot_path), full_page=True)
            self.logger.info(f"保存截圖: {screenshot_path}")
            
            # 提取並保存所有資源
            resources_info = await self.extract_all_resources(job_folder)
            
            # 提取工作元數據
            metadata = await self.extract_job_metadata(job_url)
            
            # 保存元數據
            metadata_path = job_folder / "metadata.json"
            metadata.update({
                "resources": resources_info,
                "extraction_info": {
                    "company_name": company_name,
                    "job_title": job_title,
                    "job_url": job_url,
                    "extraction_timestamp": datetime.now().isoformat()
                }
            })
            
            metadata_path.write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            self.logger.info(f"保存元數據: {metadata_path}")
            
            # 創建資源映射文件
            resource_map_path = job_folder / "resource_map.json"
            resource_map_path.write_text(
                json.dumps(resources_info, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            
            self.logger.info(f"工作頁面提取完成: {job_folder}")
            return job_folder
            
        except Exception as e:
            self.logger.error(f"提取工作頁面失敗: {job_url} - {e}")
            return None
    
    async def extract_multiple_jobs(self, job_urls: List[str], delay_range: tuple = (2, 5)) -> List[Path]:
        """
        提取多個工作頁面
        
        Args:
            job_urls: 工作 URL 列表
            delay_range: 延遲範圍（最小，最大）秒
            
        Returns:
            List[Path]: 成功提取的工作資料夾路徑列表
        """
        self.logger.info(f"開始提取 {len(job_urls)} 個工作頁面...")
        
        successful_extractions = []
        failed_extractions = []
        
        for i, job_url in enumerate(job_urls, 1):
            try:
                self.logger.info(f"提取第 {i}/{len(job_urls)} 個工作: {job_url}")
                
                # 隨機延遲
                import random
                delay = random.uniform(delay_range[0], delay_range[1])
                self.logger.info(f"等待 {delay:.1f} 秒...")
                await asyncio.sleep(delay)
                
                # 提取工作頁面
                job_folder = await self.extract_job_page(job_url)
                
                if job_folder:
                    successful_extractions.append(job_folder)
                    self.logger.info(f"成功提取: {job_folder}")
                else:
                    failed_extractions.append(job_url)
                    self.logger.warning(f"提取失敗: {job_url}")
                
            except Exception as e:
                self.logger.error(f"提取工作失敗: {job_url} - {e}")
                failed_extractions.append(job_url)
                continue
        
        self.logger.info(f"提取完成: 成功 {len(successful_extractions)} 個，失敗 {len(failed_extractions)} 個")
        
        if failed_extractions:
            self.logger.warning(f"失敗的工作 URL: {failed_extractions}")
        
        return successful_extractions
    
    async def extract_from_search_results(self, search_criteria: SearchCriteria, max_jobs: int = 50) -> List[Path]:
        """
        從搜索結果中提取工作
        
        Args:
            search_criteria: 搜索條件
            max_jobs: 最大提取工作數量
            
        Returns:
            List[Path]: 成功提取的工作資料夾路徑列表
        """
        try:
            self.logger.info(f"從搜索結果中提取工作，關鍵詞: {search_criteria.keywords}")
            
            # 構建搜索 URL
            search_url = self._build_search_url(search_criteria)
            self.logger.info(f"搜索 URL: {search_url}")
            
            # 導航到搜索頁面
            await self.page.goto(search_url, wait_until="networkidle", timeout=30000)
            
            all_job_links = []
            current_page = 1
            
            while len(all_job_links) < max_jobs:
                self.logger.info(f"處理第 {current_page} 頁...")
                
                # 等待工作列表加載
                await self.page.wait_for_selector('[data-automation="jobTitle"]', timeout=10000)
                
                # 提取當前頁面的工作連結
                job_links = await self.page.evaluate("""
                    () => {
                        const links = [];
                        const jobElements = document.querySelectorAll('[data-automation="jobTitle"] a');
                        jobElements.forEach(element => {
                            if (element.href && !links.includes(element.href)) {
                                links.push(element.href);
                            }
                        });
                        return links;
                    }
                """)
                
                all_job_links.extend(job_links)
                self.logger.info(f"第 {current_page} 頁找到 {len(job_links)} 個工作連結")
                
                # 檢查是否已經達到最大數量
                if len(all_job_links) >= max_jobs:
                    all_job_links = all_job_links[:max_jobs]
                    break
                
                # 查找下一頁按鈕
                next_button = await self.page.query_selector('[data-automation="pageNext"], a[aria-label="Next"]')
                if not next_button:
                    self.logger.info("沒有更多頁面")
                    break
                
                # 檢查下一頁按鈕是否可用
                is_disabled = await next_button.get_attribute("disabled")
                if is_disabled:
                    self.logger.info("下一頁按鈕已禁用")
                    break
                
                # 點擊下一頁
                await next_button.click()
                await self.page.wait_for_load_state("networkidle", timeout=10000)
                
                current_page += 1
                
                # 隨機延遲
                import random
                delay = random.uniform(2, 4)
                await asyncio.sleep(delay)
            
            self.logger.info(f"總共找到 {len(all_job_links)} 個工作連結")
            
            # 提取工作詳情
            if all_job_links:
                return await self.extract_multiple_jobs(all_job_links[:max_jobs])
            else:
                self.logger.warning("未找到任何工作連結")
                return []
            
        except Exception as e:
            self.logger.error(f"從搜索結果提取工作失敗: {e}")
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
        
        if params:
            url += "?" + "&".join(params)
        
        return url