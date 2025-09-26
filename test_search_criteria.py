#!/usr/bin/env python3
"""
測試 SearchCriteria 的 URL 構建邏輯
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加 src 到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.models import SearchCriteria
from src.scrapers.playwright_scraper import PlaywrightScraper
from src.utils.logger import get_logger

def build_url_test(keyword: str, location: str) -> str:
    """測試 URL 構建邏輯"""
    base_url = "https://www.seek.com.au"
    
    # 處理關鍵詞格式
    keyword_str = str(keyword).lower().replace(' ', '-')
    
    # 處理位置格式（模擬 run_integrated_seek_etl.py 的邏輯）
    if location and not location.startswith('in-'):
        location = f'in-{location}'
    
    # 構建 URL（模擬 run_integrated_seek_etl.py 的邏輯）
    search_url = f"{base_url}/{keyword_str}-jobs"
    if location:
        search_url += f"/{location}"
    
    return search_url

def build_url_correct(keyword: str, location: str) -> str:
    """正確的 URL 構建邏輯（基於我的成功測試）"""
    base_url = "https://www.seek.com.au"
    
    # 處理關鍵詞格式
    keyword_str = str(keyword).lower().replace(' ', '-')
    
    # 處理位置格式（正確的 SEEK 格式）
    location_str = str(location).replace(' ', '-')
    
    # 構建 URL
    search_url = f"{base_url}/{keyword_str}-jobs/in-{location_str}"
    
    return search_url

async def test_search_criteria_building():
    """測試不同的搜索條件構建方式"""
    logger = get_logger(__name__)
    
    # 測試案例
    test_cases = [
        {
            "keyword": "machine learning",
            "location": "Sydney NSW 2000",
            "expected_working": True
        },
        {
            "keyword": "data scientist", 
            "location": "Melbourne VIC 3000",
            "expected_working": True
        }
    ]
    
    results = []
    
    # 創建 scraper
    scraper = PlaywrightScraper()
    
    try:
        # 啟動 scraper
        await scraper.start()
        
        for i, test_case in enumerate(test_cases):
            logger.info(f"\n測試案例 {i+1}: {test_case['keyword']} in {test_case['location']}")
            
            # 測試當前實現的 URL 構建
            current_url = build_url_test(test_case['keyword'], test_case['location'])
            logger.info(f"當前實現: {current_url}")
            
            # 測試正確的 URL 構建
            correct_url = build_url_correct(test_case['keyword'], test_case['location'])
            logger.info(f"正確格式: {correct_url}")
            
            # 測試當前實現的 URL
            result_current = {
                "test_case": i+1,
                "keyword": test_case['keyword'],
                "location": test_case['location'],
                "url_type": "current_implementation",
                "url": current_url,
                "navigation_success": False,
                "jobs_found": 0,
                "error": None
            }
            
            try:
                navigation_success = await scraper.navigate_to_url(current_url)
                result_current["navigation_success"] = navigation_success
                
                if navigation_success:
                    await asyncio.sleep(3)
                    job_links = await scraper.extract_job_links()
                    result_current["jobs_found"] = len(job_links)
                    logger.info(f"當前實現: 找到 {len(job_links)} 個工作")
                else:
                    logger.error("當前實現: 導航失敗")
                    
            except Exception as e:
                result_current["error"] = str(e)
                logger.error(f"當前實現出錯: {e}")
            
            results.append(result_current)
            
            # 測試正確格式的 URL
            result_correct = {
                "test_case": i+1,
                "keyword": test_case['keyword'],
                "location": test_case['location'],
                "url_type": "correct_format",
                "url": correct_url,
                "navigation_success": False,
                "jobs_found": 0,
                "error": None
            }
            
            try:
                navigation_success = await scraper.navigate_to_url(correct_url)
                result_correct["navigation_success"] = navigation_success
                
                if navigation_success:
                    await asyncio.sleep(3)
                    job_links = await scraper.extract_job_links()
                    result_correct["jobs_found"] = len(job_links)
                    logger.info(f"正確格式: 找到 {len(job_links)} 個工作")
                else:
                    logger.error("正確格式: 導航失敗")
                    
            except Exception as e:
                result_correct["error"] = str(e)
                logger.error(f"正確格式出錯: {e}")
            
            results.append(result_correct)
            
            # 測試間延遲
            await asyncio.sleep(5)
    
    finally:
        await scraper.close()
    
    # 保存結果
    output_file = Path(f"debug_output/search_criteria_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    logger.info(f"\n{'='*60}")
    logger.info("搜索條件測試摘要")
    logger.info(f"{'='*60}")
    
    for result in results:
        status = "✅" if result["navigation_success"] else "❌"
        logger.info(f"{status} {result['url_type']}: {result['jobs_found']} 個工作")
    
    logger.info(f"結果文件: {output_file}")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(test_search_criteria_building())