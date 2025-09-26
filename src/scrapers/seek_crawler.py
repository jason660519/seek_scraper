"""
Seek職位爬蟲
簡潔高效的Seek職位搜索和詳情提取
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page

from ..utils.seek_url_builder import SeekURLBuilder
from ..utils.logger import get_logger
from ..parsers.job_parser import JobParser

logger = get_logger(__name__)


class SeekJob:
    """Seek職位數據模型"""
    
    def __init__(self, job_id: str, title: str, company: str, location: str, url: str):
        self.job_id = job_id
        self.title = title
        self.company = company
        self.location = location
        self.url = url
        self.details = {}
        self.scraped_at = datetime.now().isoformat()


class SeekCrawler:
    """Seek職位爬蟲"""
    
    def __init__(self, headless: bool = True, output_dir: str = "data/raw"):
        self.headless = headless
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.browser = None
        self.context = None
        self.page = None
        self.parser = JobParser()
        
    async def start(self):
        """啟動爬蟲"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = await self.context.new_page()
        logger.info("Seek爬蟲已啟動")
        
    async def stop(self):
        """停止爬蟲"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("Seek爬蟲已停止")
        
    async def search_jobs(self, keyword: str, location: Optional[str] = None, 
                         max_pages: int = 5) -> List[SeekJob]:
        """
        搜索職位
        
        Args:
            keyword: 搜索關鍵詞
            location: 地點（可選）
            max_pages: 最大頁數
            
        Returns:
            職位列表
        """
        jobs = []
        
        for page in range(1, max_pages + 1):
            url = SeekURLBuilder.build_search_url(keyword, location, page)
            logger.info(f"搜索第{page}頁: {url}")
            
            try:
                await self.page.goto(url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(2)  # 等待頁面加載
                
                # 提取職位鏈接
                job_links = await self._extract_job_links()
                if not job_links:
                    logger.info(f"第{page}頁未找到職位，停止搜索")
                    break
                    
                jobs.extend(job_links)
                logger.info(f"第{page}頁找到{len(job_links)}個職位")
                
            except Exception as e:
                logger.error(f"搜索第{page}頁失敗: {e}")
                break
                
        return jobs
    
    async def _extract_job_links(self) -> List[SeekJob]:
        """從搜索結果頁提取職位鏈接"""
        jobs = []
        
        # 等待職位列表加載
        await self.page.wait_for_selector('article[data-testid="job-card"]', timeout=10000)
        
        # 獲取所有職位卡片
        job_cards = await self.page.query_selector_all('article[data-testid="job-card"]')
        
        for card in job_cards:
            try:
                # 提取基本信息
                title_elem = await card.query_selector('h3 a')
                if not title_elem:
                    continue
                    
                title = await title_elem.text_content()
                job_url = await title_elem.get_attribute('href')
                
                if not job_url:
                    continue
                    
                # 提取公司名稱
                company_elem = await card.query_selector('[data-testid="job-card-company-name"]')
                company = await company_elem.text_content() if company_elem else "Unknown"
                
                # 提取地點
                location_elem = await card.query_selector('[data-testid="job-card-location"]')
                location = await location_elem.text_content() if location_elem else "Unknown"
                
                # 提取職位ID
                job_id = job_url.split('/')[-1] if '/' in job_url else job_url
                
                job = SeekJob(job_id, title.strip(), company.strip(), 
                            location.strip(), f"https://www.seek.com.au{job_url}")
                jobs.append(job)
                
            except Exception as e:
                logger.warning(f"提取職位信息失敗: {e}")
                continue
                
        return jobs
    
    async def get_job_details(self, job: SeekJob) -> bool:
        """
        獲取職位詳情
        
        Args:
            job: SeekJob對象
            
        Returns:
            是否成功獲取詳情
        """
        try:
            logger.info(f"獲取職位詳情: {job.title}")
            await self.page.goto(job.url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(1)
            
            # 提取詳細信息
            details = {}
            
            # 獲取頁面內容
            html_content = await self.page.content()
            
            # 使用解析器提取信息
            job_posts = self.parser.parse_job_listing(html_content)
            
            if job_posts:
                parsed_job = job_posts[0]  # 取第一個職位
                details['description'] = parsed_job.description
                details['salary'] = str(parsed_job.salary) if parsed_job.salary else "Not specified"
                details['work_type'] = parsed_job.job_type.value if parsed_job.job_type else "Unknown"
                details['classification'] = ""  # 需要從頁面中提取
            else:
                # 後備方案：手動提取
                # 職位描述
                desc_elem = await self.page.query_selector('[data-testid="job-ad-details"]')
                if desc_elem:
                    details['description'] = await desc_elem.text_content()
                
                # 薪資信息
                salary_elem = await self.page.query_selector('[data-testid="job-detail-salary"]')
                if salary_elem:
                    details['salary'] = await salary_elem.text_content()
                
                # 工作類型
                work_type_elem = await self.page.query_selector('[data-testid="job-detail-work-type"]')
                if work_type_elem:
                    details['work_type'] = await work_type_elem.text_content()
                
                # 職位分類
                classification_elem = await self.page.query_selector('[data-testid="job-detail-classification"]')
                if classification_elem:
                    details['classification'] = await classification_elem.text_content()
            
            job.details = details
            return True
            
        except Exception as e:
            logger.error(f"獲取職位詳情失敗 {job.title}: {e}")
            return False
    
    async def save_raw_data(self, job: SeekJob, output_dir: Path):
        """
        保存原始數據
        
        Args:
            job: SeekJob對象
            output_dir: 輸出目錄
        """
        # 創建文件夾名稱：公司名_職位名_時間戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_company = self._sanitize_filename(job.company)
        safe_title = self._sanitize_filename(job.title)
        folder_name = f"{safe_company}_{safe_title}_{timestamp}"
        
        job_dir = output_dir / folder_name
        job_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 1. 保存 HTML
            html_content = await self.page.content()
            html_file = job_dir / "index.html"
            html_file.write_text(html_content, encoding='utf-8')
            
            # 2. 保存截圖
            screenshot_file = job_dir / "screenshot.png"
            await self.page.screenshot(path=str(screenshot_file), full_page=True)
            
            # 3. 保存元數據
            metadata = {
                "job_id": job.job_id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "url": job.url,
                "scraped_at": job.scraped_at,
                "details": job.details
            }
            metadata_file = job_dir / "metadata.json"
            metadata_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
            
            # 4. 保存公司 Logo（如果存在）
            logo_elem = await self.page.query_selector('img[alt*="logo"], img[src*="company"]')
            if logo_elem:
                try:
                    logo_src = await logo_elem.get_attribute('src')
                    if logo_src:
                        logo_response = await self.page.context.request.get(logo_src)
                        if logo_response.ok:
                            logo_file = job_dir / "company_logo.jpg"
                            logo_file.write_bytes(await logo_response.body())
                except Exception as e:
                    logger.warning(f"保存公司 Logo 失敗: {e}")
            
            logger.info(f"原始資料已保存: {job_dir}")
            return True
            
        except Exception as e:
            logger.error(f"保存原始資料失敗: {e}")
            return False
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理檔案名稱，移除無效字元
        
        Args:
            filename: 原始檔案名稱
            
        Returns:
            清理後的檔案名稱
        """
        import re
        # 移除無效字元
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 限制長度
        return filename[:50]  # 最多 50 個字元
    
    async def crawl_jobs(self, keywords: List[str], locations: Optional[List[str]] = None,
                        max_pages: int = 5, output_dir: str = "data/raw") -> Dict:
        """
        完整的爬蟲流程
        
        Args:
            keywords: 關鍵詞列表
            locations: 地點列表（可選）
            max_pages: 每個搜尋的最大頁數
            output_dir: 輸出目錄
            
        Returns:
            爬蟲統計資訊
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        stats = {
            "total_jobs_found": 0,
            "total_jobs_processed": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "keywords": keywords,
            "locations": locations or ["All Australia"],
            "start_time": datetime.now().isoformat(),
            "end_time": None
        }
        
        try:
            await self.start()
            
            all_jobs = []
            
            # 組合關鍵詞和地點進行搜尋
            search_combinations = []
            if locations:
                for keyword in keywords:
                    for location in locations:
                        search_combinations.append((keyword, location))
            else:
                for keyword in keywords:
                    search_combinations.append((keyword, None))
            
            logger.info(f"開始爬蟲任務，共 {len(search_combinations)} 個搜尋組合")
            
            for keyword, location in search_combinations:
                logger.info(f"搜尋: {keyword} in {location or 'All Australia'}")
                
                jobs = await self.search_jobs(keyword, location, max_pages)
                all_jobs.extend(jobs)
                
                logger.info(f"找到 {len(jobs)} 個職位")
            
            stats["total_jobs_found"] = len(all_jobs)
            
            # 處理每個職位的詳情
            for i, job in enumerate(all_jobs, 1):
                logger.info(f"處理第 {i}/{len(all_jobs)} 個職位: {job.title}")
                
                try:
                    # 獲取詳情
                    success = await self.get_job_details(job)
                    if success:
                        # 保存原始資料
                        saved = await self.save_raw_data(job, output_path)
                        if saved:
                            stats["successful_extractions"] += 1
                        else:
                            stats["failed_extractions"] += 1
                            
                    stats["total_jobs_processed"] += 1
                    
                    # 隨機延遲，避免過快
                    await asyncio.sleep(1 + (i % 3))  # 1-3 秒延遲
                    
                except Exception as e:
                    logger.error(f"處理職位失敗 {job.title}: {e}")
                    stats["failed_extractions"] += 1
                    
        except Exception as e:
            logger.error(f"爬蟲任務失敗: {e}")
            stats["error"] = str(e)
            
        finally:
            await self.stop()
            stats["end_time"] = datetime.now().isoformat()
            
            # 保存統計資訊
            stats_file = output_path / f"crawl_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            stats_file.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')
            
            logger.info(f"爬蟲任務完成。成功: {stats['successful_extractions']}, 失敗: {stats['failed_extractions']}")
            
        return stats
        folder_name = f"{job.company}_{job.title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        folder_name = "".join(c for c in folder_name if c.isalnum() or c in "-_ ")
        job_dir = output_dir / folder_name
        job_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存頁面HTML
        html_content = await self.page.content()
        (job_dir / "page.html").write_text(html_content, encoding='utf-8')
        
        # 保存截圖
        await self.page.screenshot(path=str(job_dir / "screenshot.png"), full_page=True)
        
        # 保存職位數據
        job_data = {
            'job_id': job.job_id,
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'url': job.url,
            'details': job.details,
            'scraped_at': job.scraped_at
        }
        (job_dir / "job_data.json").write_text(json.dumps(job_data, ensure_ascii=False, indent=2))
        
        logger.info(f"已保存原始數據到: {job_dir}")


# 使用示例
async def main():
    """測試爬蟲"""
    crawler = SeekCrawler(headless=False)
    
    try:
        await crawler.start()
        
        # 搜索職位
        jobs = await crawler.search_jobs("software engineer", "melbourne", max_pages=2)
        logger.info(f"總共找到{len(jobs)}個職位")
        
        # 獲取前3個職位的詳情
        for i, job in enumerate(jobs[:3]):
            success = await crawler.get_job_details(job)
            if success:
                # 保存原始數據
                await crawler.save_raw_data(job, Path("data/raw"))
                
    finally:
        await crawler.stop()


if __name__ == "__main__":
    asyncio.run(main())