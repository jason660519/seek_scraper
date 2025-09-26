#!/usr/bin/env python3
"""
簡化版 SEEK 測試腳本
跳過代理系統直接測試 PlaywrightScraper
"""

import asyncio
import json
from pathlib import Path
from src.scrapers.playwright_scraper import PlaywrightScraper
from src.utils.logger import get_logger

async def test_seek_simple():
    """簡化測試 SEEK 爬蟲"""
    logger = get_logger('seek_simple')
    
    # 創建 scraper（不使用代理）
    async with PlaywrightScraper(proxy_manager=None, logger=logger) as scraper:
        # 測試 URL
        test_url = "https://www.seek.com.au/ai-machine-learning-jobs/in-All-Sydney-NSW"
        
        logger.info(f"導航到: {test_url}")
        success = await scraper.navigate_to_url(test_url)
        
        if success:
            logger.info("成功導航到頁面")
            
            # 等待一點時間讓頁面完全加載
            await asyncio.sleep(3)
            
            # 提取工作連結
            job_links = await scraper.extract_job_links()
            logger.info(f"找到 {len(job_links)} 個工作連結")
            
            if job_links:
                # 保存到文件
                output_dir = Path("debug_output")
                output_dir.mkdir(exist_ok=True)
                
                with open(output_dir / "job_links.json", 'w', encoding='utf-8') as f:
                    json.dump(job_links, f, indent=2, ensure_ascii=False)
                
                logger.info(f"工作連結已保存到: {output_dir / 'job_links.json'}")
                
                # 測試提取第一個工作的詳細信息
                first_job_url = job_links[0]
                logger.info(f"測試提取第一個工作詳情: {first_job_url}")
                
                job_details = await scraper.scrape_job_details(first_job_url, output_dir)
                
                if job_details:
                    logger.info(f"成功提取工作詳情: {job_details.get('title', 'Unknown')}")
                    
                    with open(output_dir / "job_details.json", 'w', encoding='utf-8') as f:
                        json.dump(job_details, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"工作詳情已保存到: {output_dir / 'job_details.json'}")
                else:
                    logger.error("無法提取工作詳情")
            else:
                logger.warning("未找到工作連結")
                
                # 保存頁面內容進行調試
                await scraper.save_page_content(output_dir)
                logger.info(f"頁面內容已保存到: {output_dir}")
        else:
            logger.error("導航失敗")

if __name__ == '__main__':
    print("開始簡化版 SEEK 測試...")
    asyncio.run(test_seek_simple())
    print("測試完成！")