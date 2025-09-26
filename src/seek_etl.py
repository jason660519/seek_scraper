"""
SEEK 職位爬蟲 ETL 主程式

整合 proxy 管理與爬蟲功能，實現完整的 ETL 流程：
1. Raw 資料擷取（HTML、CSS、JS、圖片等）
2. HTML 轉 JSON/CSV 解析
3. 資料結構化與儲存
"""

import asyncio
import json
import csv
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import hashlib

from src.scrapers.seek_scraper import SeekScraper
from src.models import SearchCriteria, JobPost
from src.utils.logger import get_logger


class SeekETL:
    """
    SEEK ETL 處理器
    
    負責完整的資料擷取、轉換、載入流程：
    - Step 1: 擷取每個職位的 raw 資料（HTML、圖片等）
    - Step 2: 解析 HTML 並轉換為結構化資料（JSON/CSV）
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        初始化 ETL 處理器
        
        Args:
            config: ETL 配置物件
            logger: 日誌記錄器
        """
        self.config = config
        self.logger = logger or get_logger(__name__)
        
        # 設定資料目錄
        self.data_dir = Path(config.get('data_dir', 'data'))
        self.raw_dir = self.data_dir / 'raw'
        self.processed_dir = self.data_dir / 'processed'
        self.cache_dir = self.data_dir / 'cache'
        
        # 建立目錄
        for dir_path in [self.raw_dir, self.processed_dir, self.cache_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 統計資訊
        self.stats = {
            'total_jobs': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'start_time': None,
            'end_time': None
        }
        
        # 初始化爬蟲
        self.scraper = SeekScraper(config.get('scraper_config', {}))
        
        # Playwright 瀏覽器實例
        self.browser = None
        self.context = None
    
    async def __aenter__(self):
        """異步上下文管理器進入"""
        await self._init_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器退出"""
        await self._close_browser()
    
    async def _init_browser(self):
        """初始化 Playwright 瀏覽器"""
        self.logger.info("初始化 Playwright 瀏覽器...")
        self.playwright = await async_playwright().start()
        
        # 配置瀏覽器參數（反偵測）
        browser_config = {
            'headless': self.config.get('headless', True),
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                '--disable-web-security',
                '--disable-features=BlockInsecurePrivateNetworkRequests',
                '--disable-features=OutOfBlinkCors',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--single-process',
                '--disable-gpu'
            ]
        }
        
        self.browser = await self.playwright.chromium.launch(**browser_config)
        
        # 配置上下文參數
        context_config = {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': self.config.get('user_agent', 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
            'locale': 'en-US',
            'timezone_id': 'Australia/Sydney',
            'permissions': ['geolocation'],
            'geolocation': {'latitude': -33.8688, 'longitude': 151.2093},  # 雪梨
            'color_scheme': 'light',
            'device_scale_factor': 1,
            'is_mobile': False,
            'has_touch': False,
            'java_script_enabled': True,
            'bypass_csp': True,
            'ignore_https_errors': True
        }
        
        self.context = await self.browser.new_context(**context_config)
        
        # 添加腳本來隱藏自動化特徵
        await self.context.add_init_script("""
            // 隱藏自動化特徵
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // 修改插件資訊
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // 修改語言資訊
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // 移除 Chrome 自動化標記
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """)
        
        self.logger.info("Playwright 瀏覽器初始化完成")
    
    async def _close_browser(self):
        """關閉 Playwright 瀏覽器"""
        if self.context:
            await self.context.close()
            self.context = None
        
        if self.browser:
            await self.browser.close()
            self.browser = None
        
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        
        self.logger.info("Playwright 瀏覽器已關閉")
    
    def _generate_job_id(self, job_url: str) -> str:
        """
        生成職位 ID
        
        Args:
            job_url: 職位 URL
            
        Returns:
            str: 職位 ID
        """
        # 從 URL 提取職位 ID
        match = re.search(r'/job/(\d+)', job_url)
        if match:
            job_id = match.group(1)
        else:
            # 使用 URL 的哈希值作為 ID
            job_id = hashlib.md5(job_url.encode()).hexdigest()[:12]
        
        return job_id
    
    def _generate_folder_name(self, company_name: str, job_title: str, job_id: str) -> str:
        """
        生成資料夾名稱
        
        Args:
            company_name: 公司名稱
            job_title: 職位名稱
            job_id: 職位 ID
            
        Returns:
            str: 資料夾名稱
        """
        # 清理檔案名稱（移除特殊字元）
        safe_company = re.sub(r'[^\w\s-]', '', company_name).strip()
        safe_title = re.sub(r'[^\w\s-]', '', job_title).strip()
        
        # 限制長度
        safe_company = safe_company[:30]
        safe_title = safe_title[:30]
        
        # 生成時間戳
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 組合資料夾名稱
        folder_name = f"{safe_company}_{safe_title}_{job_id}_{timestamp}"
        
        return folder_name
    
    async def extract_raw_data(self, job_url: str) -> Optional[Dict[str, Any]]:
        """
        擷取職位的 raw 資料（Step 1）
        
        Args:
            job_url: 職位詳情頁 URL
            
        Returns:
            Optional[Dict]: 包含 raw 資料的資訊，失敗時返回 None
        """
        self.logger.info(f"開始擷取職位 raw 資料: {job_url}")
        
        try:
            # 生成職位 ID
            job_id = self._generate_job_id(job_url)
            
            # 創建頁面
            page = await self.context.new_page()
            
            # 設置額外的請求頭
            await page.set_extra_http_headers({
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # 監控網路請求
            network_logs = []
            
            async def log_request(request):
                network_logs.append({
                    'type': 'request',
                    'url': request.url,
                    'method': request.method,
                    'headers': dict(request.headers)
                })
            
            async def log_response(response):
                network_logs.append({
                    'type': 'response',
                    'url': response.url,
                    'status': response.status,
                    'headers': dict(response.headers)
                })
            
            page.on('request', log_request)
            page.on('response', log_response)
            
            # 導航到職位頁面
            await page.goto(job_url, wait_until='networkidle', timeout=30000)
            
            # 等待頁面載入完成
            await page.wait_for_load_state('domcontentloaded')
            
            # 獲取頁面內容
            html_content = await page.content()
            
            # 解析 HTML 獲取基本資訊
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 提取公司名稱和職位名稱
            company_name = self._extract_company_name(soup) or "Unknown_Company"
            job_title = self._extract_job_title(soup) or "Unknown_Position"
            
            # 生成資料夾名稱
            folder_name = self._generate_folder_name(company_name, job_title, job_id)
            job_dir = self.raw_dir / folder_name
            job_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存 HTML 內容
            html_file = job_dir / 'page.html'
            async with aiofiles.open(html_file, 'w', encoding='utf-8') as f:
                await f.write(html_content)
            
            # 提取並保存 CSS 檔案
            css_files = await self._extract_css_files(page, soup, job_dir)
            
            # 提取並保存 JavaScript 檔案
            js_files = await self._extract_js_files(page, soup, job_dir)
            
            # 提取並保存圖片檔案
            image_files = await self._extract_images(page, soup, job_dir)
            
            # 保存網路請求日誌
            network_log_file = job_dir / 'network_logs.json'
            async with aiofiles.open(network_log_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(network_logs, indent=2, ensure_ascii=False))
            
            # 保存中繼資料
            metadata = {
                'job_id': job_id,
                'job_url': job_url,
                'company_name': company_name,
                'job_title': job_title,
                'extraction_time': datetime.now().isoformat(),
                'files': {
                    'html': str(html_file.relative_to(self.raw_dir)),
                    'css': css_files,
                    'js': js_files,
                    'images': image_files,
                    'network_logs': str(network_log_file.relative_to(self.raw_dir))
                }
            }
            
            metadata_file = job_dir / 'metadata.json'
            async with aiofiles.open(metadata_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(metadata, indent=2, ensure_ascii=False))
            
            # 關閉頁面
            await page.close()
            
            self.logger.info(f"成功擷取職位 raw 資料: {folder_name}")
            self.stats['successful_extractions'] += 1
            
            return {
                'job_id': job_id,
                'folder_path': job_dir,
                'metadata': metadata,
                'html_content': html_content
            }
            
        except Exception as e:
            self.logger.error(f"擷取職位 raw 資料失敗: {job_url} - {e}")
            self.stats['failed_extractions'] += 1
            return None
    
    def _extract_company_name(self, soup: BeautifulSoup) -> Optional[str]:
        """提取公司名稱"""
        # 多種選擇器嘗試提取公司名稱
        selectors = [
            '[data-automation="job-detail-company"]',
            '.job-detail-company',
            '[data-testid="company-name"]',
            '.company-name',
            'h2[class*="company"]',
            '[class*="Company"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # 從 JSON-LD 中提取
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'hiringOrganization' in data:
                    return data['hiringOrganization'].get('name')
            except:
                continue
        
        return None
    
    def _extract_job_title(self, soup: BeautifulSoup) -> Optional[str]:
        """提取職位名稱"""
        selectors = [
            '[data-automation="job-detail-title"]',
            '.job-detail-title',
            '[data-testid="job-title"]',
            'h1[class*="title"]',
            '[class*="Title"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # 從 JSON-LD 中提取
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'title' in data:
                    return data['title']
            except:
                continue
        
        return None
    
    async def _extract_css_files(self, page, soup: BeautifulSoup, job_dir: Path) -> List[str]:
        """提取 CSS 檔案"""
        css_files = []
        css_dir = job_dir / 'css'
        css_dir.mkdir(exist_ok=True)
        
        # 尋找所有 CSS 連結
        css_links = soup.find_all('link', {'rel': 'stylesheet'})
        
        for i, link in enumerate(css_links):
            href = link.get('href')
            if not href:
                continue
            
            try:
                # 轉換為絕對 URL
                absolute_url = urljoin(str(page.url), href)
                
                # 下載 CSS 內容
                response = await page.context.request.get(absolute_url)
                if response.ok:
                    css_content = await response.text()
                    
                    # 生成檔案名稱
                    filename = f'style_{i+1}.css'
                    if 'href' in link.attrs:
                        # 嘗試從 URL 提取有意義的名稱
                        url_path = urlparse(href).path
                        if url_path and url_path != '/':
                            filename = url_path.split('/')[-1] or f'style_{i+1}.css'
                    
                    css_file = css_dir / filename
                    async with aiofiles.open(css_file, 'w', encoding='utf-8') as f:
                        await f.write(css_content)
                    
                    css_files.append(str(css_file.relative_to(job_dir)))
                    
            except Exception as e:
                self.logger.warning(f"提取 CSS 失敗 {href}: {e}")
        
        return css_files
    
    async def _extract_js_files(self, page, soup: BeautifulSoup, job_dir: Path) -> List[str]:
        """提取 JavaScript 檔案"""
        js_files = []
        js_dir = job_dir / 'js'
        js_dir.mkdir(exist_ok=True)
        
        # 尋找所有 JavaScript 腳本
        script_tags = soup.find_all('script', {'src': True})
        
        for i, script in enumerate(script_tags):
            src = script.get('src')
            if not src:
                continue
            
            try:
                # 轉換為絕對 URL
                absolute_url = urljoin(str(page.url), src)
                
                # 下載 JavaScript 內容
                response = await page.context.request.get(absolute_url)
                if response.ok:
                    js_content = await response.text()
                    
                    # 生成檔案名稱
                    filename = f'script_{i+1}.js'
                    if 'src' in script.attrs:
                        # 嘗試從 URL 提取有意義的名稱
                        url_path = urlparse(src).path
                        if url_path and url_path != '/':
                            filename = url_path.split('/')[-1] or f'script_{i+1}.js'
                    
                    js_file = js_dir / filename
                    async with aiofiles.open(js_file, 'w', encoding='utf-8') as f:
                        await f.write(js_content)
                    
                    js_files.append(str(js_file.relative_to(job_dir)))
                    
            except Exception as e:
                self.logger.warning(f"提取 JavaScript 失敗 {src}: {e}")
        
        return js_files
    
    async def _extract_images(self, page, soup: BeautifulSoup, job_dir: Path) -> List[str]:
        """提取圖片檔案"""
        image_files = []
        images_dir = job_dir / 'images'
        images_dir.mkdir(exist_ok=True)
        
        # 尋找所有圖片
        img_tags = soup.find_all('img')
        
        for i, img in enumerate(img_tags):
            src = img.get('src')
            if not src:
                continue
            
            try:
                # 轉換為絕對 URL
                absolute_url = urljoin(str(page.url), src)
                
                # 下載圖片內容
                response = await page.context.request.get(absolute_url)
                if response.ok:
                    image_content = await response.body()
                    
                    # 根據 content-type 決定副檔名
                    content_type = response.headers.get('content-type', '')
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        ext = '.jpg'
                    elif 'png' in content_type:
                        ext = '.png'
                    elif 'gif' in content_type:
                        ext = '.gif'
                    elif 'svg' in content_type:
                        ext = '.svg'
                    else:
                        # 從 URL 提取副檔名
                        url_path = urlparse(src).path
                        ext = Path(url_path).suffix or '.jpg'
                    
                    # 生成檔案名稱
                    filename = f'image_{i+1}{ext}'
                    if 'alt' in img.attrs and img['alt']:
                        # 使用 alt 文字作為檔案名稱
                        safe_alt = re.sub(r'[^\w\s-]', '', img['alt']).strip()
                        if safe_alt:
                            filename = f"{safe_alt[:30]}{ext}"
                    
                    image_file = images_dir / filename
                    async with aiofiles.open(image_file, 'wb') as f:
                        await f.write(image_content)
                    
                    image_files.append(str(image_file.relative_to(job_dir)))
                    
            except Exception as e:
                self.logger.warning(f"提取圖片失敗 {src}: {e}")
        
        return image_files
    
    def parse_job_details(self, html_content: str, job_url: str) -> Optional[Dict[str, Any]]:
        """
        解析職位詳情（Step 2）
        
        Args:
            html_content: HTML 內容
            job_url: 職位 URL
            
        Returns:
            Optional[Dict]: 結構化的職位資料
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 提取各欄位資料
            job_data = {
                'seek_url': job_url,
                'job_detail_title': self._extract_job_title(soup) or '',
                'job_detail_location': self._extract_location(soup) or '',
                'job_detail_classifications': self._extract_classifications(soup) or '',
                'job_detail_work_type': self._extract_work_type(soup) or '',
                'job_detail_salary': self._extract_salary(soup) or '',
                'jobAdDetails': self._extract_job_details(soup) or ''
            }
            
            return job_data
            
        except Exception as e:
            self.logger.error(f"解析職位詳情失敗: {job_url} - {e}")
            return None
    
    def _extract_location(self, soup: BeautifulSoup) -> Optional[str]:
        """提取地點資訊"""
        selectors = [
            '[data-automation="job-detail-location"]',
            '.job-detail-location',
            '[data-testid="job-location"]',
            '.job-location',
            '[class*="Location"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return None
    
    def _extract_classifications(self, soup: BeautifulSoup) -> Optional[str]:
        """提取分類資訊"""
        selectors = [
            '[data-automation="job-detail-classifications"]',
            '.job-detail-classifications',
            '[data-testid="job-classifications"]',
            '.job-classifications',
            '[class*="Classification"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return None
    
    def _extract_work_type(self, soup: BeautifulSoup) -> Optional[str]:
        """提取工作類型"""
        selectors = [
            '[data-automation="job-detail-work-type"]',
            '.job-detail-work-type',
            '[data-testid="job-work-type"]',
            '.job-work-type',
            '[class*="WorkType"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return None
    
    def _extract_salary(self, soup: BeautifulSoup) -> Optional[str]:
        """提取薪資資訊"""
        selectors = [
            '[data-automation="job-detail-salary"]',
            '.job-detail-salary',
            '[data-testid="job-salary"]',
            '.job-salary',
            '[class*="Salary"]',
            '[class*="Pay"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return None
    
    def _extract_job_details(self, soup: BeautifulSoup) -> Optional[str]:
        """提取職位詳細描述"""
        selectors = [
            '[data-automation="jobAdDetails"]',
            '.jobAdDetails',
            '[data-testid="job-description"]',
            '.job-description',
            '[class*="JobDescription"]',
            '[class*="JobDetail"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # 如果找不到特定容器，嘗試尋找主要內容區域
        main_content = soup.find('main') or soup.find('article') or soup.find('div', {'class': re.compile(r'content|main|body', re.I)})
        if main_content:
            return main_content.get_text(strip=True)
        
        return None
    
    async def process_job_list(self, job_urls: List[str], batch_size: int = 5) -> List[Dict[str, Any]]:
        """
        處理職位列表
        
        Args:
            job_urls: 職位 URL 列表
            batch_size: 批次處理大小
            
        Returns:
            List[Dict]: 處理結果列表
        """
        self.logger.info(f"開始處理 {len(job_urls)} 個職位")
        self.stats['total_jobs'] = len(job_urls)
        self.stats['start_time'] = datetime.now()
        
        results = []
        
        # 批次處理
        for i in range(0, len(job_urls), batch_size):
            batch = job_urls[i:i + batch_size]
            self.logger.info(f"處理批次 {i//batch_size + 1}/{(len(job_urls) + batch_size - 1)//batch_size}")
            
            # 並行處理批次
            batch_results = await asyncio.gather(*[
                self.process_single_job(url) for url in batch
            ], return_exceptions=True)
            
            # 處理結果
            for result in batch_results:
                if isinstance(result, Exception):
                    self.logger.error(f"處理職位時發生異常: {result}")
                elif result:
                    results.append(result)
            
            # 批次間延遲
            if i + batch_size < len(job_urls):
                await asyncio.sleep(random.uniform(2, 5))
        
        self.stats['end_time'] = datetime.now()
        self._save_processing_stats()
        
        self.logger.info(f"完成處理，成功: {self.stats['successful_extractions']}, 失敗: {self.stats['failed_extractions']}")
        
        return results
    
    async def process_single_job(self, job_url: str) -> Optional[Dict[str, Any]]:
        """
        處理單個職位
        
        Args:
            job_url: 職位 URL
            
        Returns:
            Optional[Dict]: 處理結果
        """
        try:
            # Step 1: 擷取 raw 資料
            raw_data = await self.extract_raw_data(job_url)
            if not raw_data:
                return None
            
            # Step 2: 解析 HTML
            job_details = self.parse_job_details(raw_data['html_content'], job_url)
            if not job_details:
                return None
            
            # 組合結果
            result = {
                'job_url': job_url,
                'raw_data_path': str(raw_data['folder_path']),
                'parsed_data': job_details,
                'extraction_time': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"處理職位失敗: {job_url} - {e}")
            return None
    
    def save_to_csv(self, job_data_list: List[Dict[str, Any]], filename: str = None) -> str:
        """
        儲存資料到 CSV 檔案
        
        Args:
            job_data_list: 職位資料列表
            filename: 檔案名稱（可選）
            
        Returns:
            str: CSV 檔案路徑
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"seek_jobs_{timestamp}.csv"
        
        csv_path = self.processed_dir / filename
        
        # 定義 CSV 欄位
        fieldnames = [
            'seek_url',
            'job_detail_title',
            'job_detail_location',
            'job_detail_classifications',
            'job_detail_work_type',
            'job_detail_salary',
            'jobAdDetails',
            'raw_data_path',
            'extraction_time'
        ]
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for job_data in job_data_list:
                if job_data and 'parsed_data' in job_data:
                    row = job_data['parsed_data'].copy()
                    row['raw_data_path'] = job_data.get('raw_data_path', '')
                    row['extraction_time'] = job_data.get('extraction_time', '')
                    writer.writerow(row)
        
        self.logger.info(f"CSV 檔案已儲存: {csv_path}")
        return str(csv_path)
    
    def save_to_json(self, job_data_list: List[Dict[str, Any]], filename: str = None) -> str:
        """
        儲存資料到 JSON 檔案
        
        Args:
            job_data_list: 職位資料列表
            filename: 檔案名稱（可選）
            
        Returns:
            str: JSON 檔案路徑
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"seek_jobs_{timestamp}.json"
        
        json_path = self.processed_dir / filename
        
        with open(json_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(job_data_list, jsonfile, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"JSON 檔案已儲存: {json_path}")
        return str(json_path)
    
    def _save_processing_stats(self):
        """儲存處理統計資訊"""
        stats_file = self.processed_dir / 'processing_stats.json'
        
        processing_time = None
        if self.stats['start_time'] and self.stats['end_time']:
            processing_time = str(self.stats['end_time'] - self.stats['start_time'])
        
        stats_data = {
            'total_jobs': self.stats['total_jobs'],
            'successful_extractions': self.stats['successful_extractions'],
            'failed_extractions': self.stats['failed_extractions'],
            'success_rate': self.stats['successful_extractions'] / max(self.stats['total_jobs'], 1),
            'processing_time': processing_time,
            'start_time': self.stats['start_time'].isoformat() if self.stats['start_time'] else None,
            'end_time': self.stats['end_time'].isoformat() if self.stats['end_time'] else None
        }
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"處理統計已儲存: {stats_file}")


async def main():
    """主函數"""
    # 配置
    config = {
        'headless': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'data_dir': 'data',
        'scraper_config': {
            'base_url': 'https://www.seek.com.au',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'timeout': 30,
            'request_delay': 1.0,
            'max_retries': 3,
            'max_pages': 5
        }
    }
    
    # 測試 URL 列表
    test_urls = [
        'https://www.seek.com.au/job/12345678',
        'https://www.seek.com.au/job/87654321'
    ]
    
    # 執行 ETL 流程
    async with SeekETL(config) as etl:
        results = await etl.process_job_list(test_urls)
        
        # 儲存結果
        if results:
            csv_path = etl.save_to_csv(results)
            json_path = etl.save_to_json(results)
            
            print(f"ETL 流程完成！")
            print(f"CSV 檔案: {csv_path}")
            print(f"JSON 檔案: {json_path}")
            print(f"處理職位數: {len(results)}")


if __name__ == '__main__':
    asyncio.run(main())