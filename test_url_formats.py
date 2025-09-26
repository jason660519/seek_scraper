#!/usr/bin/env python3
"""
測試不同 URL 格式的搜索效果
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

async def test_url_formats():
    """測試不同 URL 格式的搜索效果"""
    logger = get_logger(__name__)
    
    # 測試搜索組合
    test_searches = [
        {
            "keywords": "machine learning",
            "location": "Sydney NSW 2000",
            "formats": [
                # 格式 1: 直接格式 (我測試成功的格式)
                "https://www.seek.com.au/machine-learning-jobs/in-Sydney-NSW-2000",
                # 格式 2: run_integrated_seek_etl.py 使用的格式
                "https://www.seek.com.au/machine-learning-jobs/in-Sydney-NSW-2000",
                # 格式 3: 簡化格式
                "https://www.seek.com.au/machine-learning-jobs"
            ]
        }
    ]
    
    results = []
    
    # 創建 scraper
    scraper = PlaywrightScraper()
    
    try:
        # 啟動 scraper
        await scraper.start()
        
        for search in test_searches:
            logger.info(f"\n測試關鍵詞: {search['keywords']} in {search['location']}")
            
            for i, url_format in enumerate(search['formats']):
                logger.info(f"\n格式 {i+1}: {url_format}")
                
                result = {
                    "keywords": search['keywords'],
                    "location": search['location'],
                    "url_format": url_format,
                    "format_type": f"format_{i+1}",
                    "timestamp": datetime.now().isoformat(),
                    "navigation_success": False,
                    "jobs_found": 0,
                    "error": None
                }
                
                try:
                    # 導航到搜索頁面
                    navigation_success = await scraper.navigate_to_url(url_format)
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
                
                # 格式間延遲
                await asyncio.sleep(5)
    
    finally:
        await scraper.close()
    
    # 保存結果
    output_file = Path(f"debug_output/url_format_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    logger.info(f"\n{'='*60}")
    logger.info("URL 格式測試摘要")
    logger.info(f"{'='*60}")
    
    for result in results:
        status = "✅" if result["navigation_success"] else "❌"
        logger.info(f"{status} {result['format_type']}: {result['jobs_found']} 個工作")
    
    logger.info(f"結果文件: {output_file}")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(test_url_formats())