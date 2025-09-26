#!/usr/bin/env python3
"""
直接測試 SEEK 搜索功能
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加 src 到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.scrapers.playwright_scraper import PlaywrightScraper
from src.utils.logger import get_logger

async def test_direct_search():
    """直接測試搜索功能"""
    logger = get_logger(__name__)
    
    # 測試搜索組合
    test_searches = [
        {
            "keywords": "machine learning",
            "location": "Sydney NSW 2000",
            "expected_url": "https://www.seek.com.au/machine-learning-jobs/in-Sydney-NSW-2000"
        },
        {
            "keywords": "data scientist",
            "location": "Melbourne VIC 3000", 
            "expected_url": "https://www.seek.com.au/data-scientist-jobs/in-Melbourne-VIC-3000"
        }
    ]
    
    results = []
    
    # 創建 scraper
    scraper = PlaywrightScraper()
    
    # 啟動 scraper
    await scraper.start()
    
    try:
        for i, search in enumerate(test_searches):
            logger.info(f"\n測試搜索 {i+1}: {search['keywords']} in {search['location']}")
            logger.info(f"期望 URL: {search['expected_url']}")
            
            result = {
                "search": search,
                "timestamp": datetime.now().isoformat(),
                "navigation_success": False,
                "jobs_found": 0,
                "error": None
            }
            
            try:
                # 直接導航到搜索頁面
                navigation_success = await scraper.navigate_to_url(search['expected_url'])
                result["navigation_success"] = navigation_success
                
                if navigation_success:
                    logger.info("✅ 導航成功")
                    
                    # 等待頁面加載
                    await asyncio.sleep(3)
                    
                    # 提取工作連結
                    job_links = await scraper.extract_job_links()
                    result["jobs_found"] = len(job_links)
                    
                    logger.info(f"找到 {len(job_links)} 個工作連結")
                    
                    if job_links:
                        logger.info("前 3 個工作連結:")
                        for j, link in enumerate(job_links[:3]):
                            logger.info(f"  {j+1}. {link}")
                    
                else:
                    logger.error("❌ 導航失敗")
                    
            except Exception as e:
                logger.error(f"搜索過程中出錯: {e}")
                result["error"] = str(e)
            
            results.append(result)
            
            # 搜索間延遲
            if i < len(test_searches) - 1:
                await asyncio.sleep(5)
    
    finally:
        await scraper.close()
    
    # 保存結果
    output_file = Path(f"debug_output/direct_search_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    logger.info(f"\n{'='*60}")
    logger.info("直接搜索測試摘要")
    logger.info(f"{'='*60}")
    
    successful_navigations = sum(1 for r in results if r["navigation_success"])
    total_jobs = sum(r["jobs_found"] for r in results)
    
    logger.info(f"總測試數: {len(results)}")
    logger.info(f"成功導航: {successful_navigations}")
    logger.info(f"總工作數: {total_jobs}")
    logger.info(f"結果文件: {output_file}")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(test_direct_search())