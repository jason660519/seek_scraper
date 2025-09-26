#!/usr/bin/env python3
"""
SEEK 網站調試腳本
用於測試和調試 PlaywrightScraper
"""

import asyncio
import json
from pathlib import Path
from src.scrapers.playwright_scraper import PlaywrightScraper
from src.services.proxy_manager import ProxyManager
from src.utils.logger import get_logger

async def test_seek_navigation():
    """測試 SEEK 導航和元素提取"""
    logger = get_logger('seek_debug')
    
    # 創建代理管理器
    proxy_manager = ProxyManager()
    
    # 創建 scraper
    async with PlaywrightScraper(proxy_manager=proxy_manager, logger=logger) as scraper:
        # 測試 URL
        test_url = "https://www.seek.com.au/ai-machine-learning-jobs/in-All-Sydney-NSW"
        
        logger.info(f"導航到: {test_url}")
        success = await scraper.navigate_to_url(test_url)
        
        if success:
            logger.info("成功導航到頁面")
            
            # 等待一點時間讓頁面完全加載
            await asyncio.sleep(3)
            
            # 保存頁面截圖和 HTML
            output_dir = Path("debug_output")
            output_dir.mkdir(exist_ok=True)
            
            await scraper.save_page_content(output_dir)
            logger.info(f"頁面內容已保存到: {output_dir}")
            
            # 嘗試不同的選擇器
            selectors = [
                '[data-automation="jobTitle"] a',
                'a[data-automation="jobTitle"]',
                '[data-automation="job-title"] a',
                'article a[href*="/job/"]',
                'a[href*="/job/"]',
                '.job-title a',
                'h1 a',
                'a h1',
                'article h1',
                'h1'
            ]
            
            # 獲取頁面內容進行分析
            page_content = await scraper.page.content()
            
            # 檢查每個選擇器
            for selector in selectors:
                try:
                    elements = await scraper.page.query_selector_all(selector)
                    if elements:
                        logger.info(f"找到 {len(elements)} 個元素使用選擇器: {selector}")
                        
                        # 獲取第一個元素的文本和 href
                        first_element = elements[0]
                        text = await first_element.text_content()
                        href = await first_element.get_attribute('href')
                        
                        logger.info(f"  文本: {text}")
                        logger.info(f"  鏈接: {href}")
                        
                        # 獲取所有鏈接
                        links = []
                        for element in elements[:5]:  # 只取前5個
                            text = await element.text_content()
                            href = await element.get_attribute('href')
                            if href:
                                links.append({
                                    'text': text.strip() if text else '',
                                    'href': href
                                })
                        
                        logger.info(f"  前幾個鏈接: {json.dumps(links, indent=2, ensure_ascii=False)}")
                        break
                        
                except Exception as e:
                    logger.error(f"選擇器 {selector} 錯誤: {e}")
            
            # 搜索包含 "job" 的鏈接
            all_links = await scraper.page.query_selector_all('a')
            job_links = []
            
            for link in all_links:
                try:
                    href = await link.get_attribute('href')
                    text = await link.text_content()
                    
                    if href and ('/job/' in href or 'job' in (text or '').lower()):
                        job_links.append({
                            'text': text.strip() if text else '',
                            'href': href
                        })
                except:
                    continue
            
            logger.info(f"找到 {len(job_links)} 個可能的工作鏈接")
            if job_links:
                logger.info(f"前幾個工作鏈接: {json.dumps(job_links[:5], indent=2, ensure_ascii=False)}")
            
            # 保存所有鏈接到文件
            with open(output_dir / "all_links.json", 'w', encoding='utf-8') as f:
                json.dump(job_links, f, indent=2, ensure_ascii=False)
            
            logger.info(f"所有鏈接已保存到: {output_dir / 'all_links.json'}")
            
        else:
            logger.error("導航失敗")

if __name__ == '__main__':
    print("開始 SEEK 網站調試...")
    asyncio.run(test_seek_navigation())
    print("調試完成！")