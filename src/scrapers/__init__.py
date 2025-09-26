"""
SEEK 網站爬蟲模組

提供對 SEEK 求職網站的爬取功能，包括搜尋、分頁處理等。
"""

import asyncio
import random
import time
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse, parse_qs
import aiohttp
from bs4 import BeautifulSoup
import logging

from src.models import SearchCriteria, JobPost
from src.utils.logger import get_logger


class SeekScraper:
    """
    SEEK 網站爬蟲類別
    
    負責從 SEEK 網站爬取職位資訊，包含搜尋、分頁、延遲控制等功能。
    """
    
    def __init__(self, config, logger: Optional[logging.Logger] = None):
        """
        初始化爬蟲
        
        Args:
            config: 爬蟲配置物件
            logger: 日誌記錄器
        """
        self.config = config
        self.logger = logger or get_logger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # 統計資訊
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        # 請求頭
        self.headers = {
            'User-Agent': config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
    
    async def __aenter__(self):
        """異步上下文管理器進入"""
        await self._create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器退出"""
        await self._close_session()
    
    async def _create_session(self):
        """創建 HTTP 會話"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            connector = aiohttp.TCPConnector(
                limit=10,  # 連接池限制
                limit_per_host=5,  # 每主機連接限制
                ttl_dns_cache=300,  # DNS 快取時間
                use_dns_cache=True,
            )
            
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=timeout,
                connector=connector,
                trust_env=True  # 信任環境變數中的代理設定
            )
            self.logger.info("HTTP 會話創建完成")
    
    async def _close_session(self):
        """關閉 HTTP 會話"""
        if self.session:
            await self.session.close()
            self.session = None
            self.logger.info("HTTP 會話已關閉")
    
    async def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        發送 HTTP 請求
        
        Args:
            url: 請求 URL
            params: 查詢參數
            
        Returns:
            str: 響應內容
            
        Raises:
            aiohttp.ClientError: 請求失敗
        """
        self.total_requests += 1
        
        # 添加隨機延遲避免被封鎖
        delay = self.config.request_delay + random.uniform(0.1, 0.5)
        await asyncio.sleep(delay)
        
        for attempt in range(self.config.max_retries):
            try:
                self.logger.debug(f"發送請求: {url} (嘗試 {attempt + 1}/{self.config.max_retries})")
                
                async with self.session.get(url, params=params) as response:
                    response.raise_for_status()
                    content = await response.text()
                    
                    self.successful_requests += 1
                    self.logger.debug(f"請求成功: {url} (狀態碼: {response.status})")
                    return content
                    
            except aiohttp.ClientError as e:
                self.logger.warning(f"請求失敗 (嘗試 {attempt + 1}): {url} - {e}")
                
                if attempt < self.config.max_retries - 1:
                    # 指數退避重試
                    retry_delay = (2 ** attempt) + random.uniform(0.1, 1.0)
                    self.logger.info(f"等待 {retry_delay:.1f} 秒後重試...")
                    await asyncio.sleep(retry_delay)
                else:
                    self.failed_requests += 1
                    self.logger.error(f"請求最終失敗: {url}")
                    raise
        
        # 不應該到達這裡，但為了類型檢查
        raise RuntimeError("請求重試邏輯錯誤")
    
    def _build_search_url(self, criteria: SearchCriteria, page: int = 1) -> tuple[str, Dict[str, Any]]:
        """
        構建搜尋 URL
        
        Args:
            criteria: 搜尋條件
            page: 頁碼
            
        Returns:
            tuple: (URL, 參數)
        """
        base_url = f"{self.config.base_url}/jobs"
        
        # 轉換搜尋條件為 SEEK 參數
        params = criteria.to_seek_params()
        
        # 添加分頁參數
        if page > 1:
            params['page'] = page
        
        return base_url, params
    
    def _extract_job_links(self, html_content: str) -> List[str]:
        """
        從 HTML 中提取職位連結
        
        Args:
            html_content: HTML 內容
            
        Returns:
            List[str]: 職位連結列表
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        job_links = []
        
        # SEEK 使用多種方式標記職位連結
        # 方法 1: 尋找包含 '/job/' 的連結
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/job/' in href and href.startswith('/'):
                full_url = urljoin(self.config.base_url, href)
                job_links.append(full_url)
        
        # 方法 2: 尋找特定的職位卡片
        job_cards = soup.find_all('article', {'data-automation': 'jobListing'})
        for card in job_cards:
            link = card.find('a', {'data-automation': 'jobTitle'})
            if link and link.get('href'):
                href = link['href']
                if href.startswith('/'):
                    full_url = urljoin(self.config.base_url, href)
                    job_links.append(full_url)
        
        # 去重並限制數量
        unique_links = list(set(job_links))
        self.logger.info(f"從頁面中提取了 {len(unique_links)} 個職位連結")
        
        return unique_links[:20]  # 限制每頁最多 20 個連結
    
    def _extract_total_pages(self, html_content: str) -> int:
        """
        從 HTML 中提取總頁數
        
        Args:
            html_content: HTML 內容
            
        Returns:
            int: 總頁數
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 方法 1: 尋找分頁資訊
        pagination = soup.find('nav', {'aria-label': 'pagination'})
        if pagination:
            page_links = pagination.find_all('a')
            page_numbers = []
            
            for link in page_links:
                text = link.get_text(strip=True)
                if text.isdigit():
                    page_numbers.append(int(text))
            
            if page_numbers:
                return max(page_numbers)
        
        # 方法 2: 尋找結果計數
        result_count = soup.find('span', string=lambda text: text and 'jobs' in text.lower())
        if result_count:
            # 假設每頁 20 個結果
            return 1  # 保守估計
        
        return 1  # 預設值
    
    async def search_jobs(self, criteria: SearchCriteria, max_pages: Optional[int] = None) -> List[str]:
        """
        搜尋職位
        
        Args:
            criteria: 搜尋條件
            max_pages: 最大頁數限制
            
        Returns:
            List[str]: 職位頁面 HTML 內容列表
        """
        if max_pages is None:
            max_pages = self.config.max_pages
        
        self.logger.info(f"開始搜尋職位：{criteria.keyword}")
        if criteria.location:
            self.logger.info(f"地點：{criteria.location}")
        
        all_pages = []
        
        try:
            await self._create_session()
            
            # 第一頁：獲取總頁數
            url, params = self._build_search_url(criteria, page=1)
            first_page_content = await self._make_request(url, params)
            all_pages.append(first_page_content)
            
            total_pages = self._extract_total_pages(first_page_content)
            self.logger.info(f"找到 {total_pages} 頁結果")
            
            # 限制頁數
            pages_to_fetch = min(total_pages, max_pages)
            self.logger.info(f"將爬取 {pages_to_fetch} 頁")
            
            # 爬取剩餘頁面
            tasks = []
            for page in range(2, pages_to_fetch + 1):
                url, params = self._build_search_url(criteria, page=page)
                task = self._make_request(url, params)
                tasks.append(task)
            
            if tasks:
                self.logger.info(f"並行爬取 {len(tasks)} 個頁面...")
                remaining_pages = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 處理結果
                for i, result in enumerate(remaining_pages):
                    if isinstance(result, Exception):
                        self.logger.error(f"第 {i + 2} 頁爬取失敗: {result}")
                    else:
                        all_pages.append(result)
            
            self.logger.info(f"搜尋完成，共獲得 {len(all_pages)} 個頁面")
            
            # 統計資訊
            self.logger.info(f"總請求數：{self.total_requests}")
            self.logger.info(f"成功請求：{self.successful_requests}")
            self.logger.info(f"失敗請求：{self.failed_requests}")
            
            return all_pages
            
        except Exception as e:
            self.logger.error(f"搜尋過程中發生錯誤: {e}")
            raise
        finally:
            await self._close_session()
    
    async def fetch_job_detail(self, job_url: str) -> str:
        """
        獲取職位詳情頁面
        
        Args:
            job_url: 職位詳情頁面 URL
            
        Returns:
            str: 職位詳情 HTML 內容
        """
        self.logger.info(f"獲取職位詳情: {job_url}")
        
        try:
            await self._create_session()
            content = await self._make_request(job_url)
            self.logger.info(f"成功獲取職位詳情: {job_url}")
            return content
            
        except Exception as e:
            self.logger.error(f"獲取職位詳情失敗: {job_url} - {e}")
            raise
        finally:
            await self._close_session()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        獲取爬蟲統計資訊
        
        Returns:
            Dict: 統計資訊
        """
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': self.successful_requests / max(self.total_requests, 1),
            'average_delay': self.config.request_delay
        }


# 導出 PlaywrightScraper
from .playwright_scraper import PlaywrightScraper, AntiCrawlingConfig

__all__ = ['SeekScraper', 'PlaywrightScraper', 'AntiCrawlingConfig']