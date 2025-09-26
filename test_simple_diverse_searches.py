#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版多樣化搜索測試腳本
測試不同關鍵詞和地點的職位搜索功能
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 將當前目錄添加到 Python 路徑
sys.path.append(str(Path(__file__).parent))

# 使用絕對導入
from src.scrapers.playwright_scraper import PlaywrightScraper
from src.utils.logger import get_logger

async def test_single_search(keywords: str, location: str, max_pages: int = 1):
    """測試單個搜索"""
    logger = get_logger('simple_diverse_search')
    
    logger.info(f"測試搜索: {keywords} in {location}")
    
    try:
        # 創建 scraper 實例
        scraper = PlaywrightScraper(
            logger=logger
        )
        
        # 構建搜索 URL
        search_url = f"https://www.seek.com.au/{keywords.replace(' ', '-')}-jobs/in-{location.replace(' ', '-')}?page=1"
        
        logger.info(f"導航到: {search_url}")
        
        # 導航到搜索頁面
        success = await scraper.navigate_to_url(search_url)
        if not success:
            logger.error(f"無法導航到搜索頁面: {search_url}")
            return {
                'keywords': keywords,
                'location': location,
                'jobs_found': 0,
                'success': False,
                'error': 'Navigation failed',
                'search_url': search_url
            }
        
        # 等待頁面加載
        await asyncio.sleep(3)
        
        # 提取工作連結
        job_links = await scraper.extract_job_links()
        
        # 獲取詳細信息（只處理前3個）
        detailed_jobs = []
        for i, link in enumerate(job_links[:3]):
            try:
                logger.info(f"處理第 {i+1} 個職位: {link}")
                job_details = await scraper.get_job_details(link)
                if job_details:
                    detailed_jobs.append(job_details)
                    await asyncio.sleep(2)  # 避免過快
            except Exception as e:
                logger.error(f"處理職位失敗: {e}")
                continue
        
        # 關閉 scraper
        await scraper.close()
        
        jobs_found = len(job_links)
        success = jobs_found > 0
        
        logger.info(f"✅ {keywords} in {location}: {jobs_found} jobs found, {len(detailed_jobs)} detailed")
        
        return {
            'keywords': keywords,
            'location': location,
            'jobs_found': jobs_found,
            'success': success,
            'error': None,
            'search_url': search_url,
            'sample_jobs': detailed_jobs
        }
        
    except Exception as e:
        logger.error(f"❌ {keywords} in {location}: {str(e)}")
        return {
            'keywords': keywords,
            'location': location,
            'jobs_found': 0,
            'success': False,
            'error': str(e),
            'search_url': search_url if 'search_url' in locals() else None,
            'sample_jobs': []
        }

async def main():
    """主函數"""
    logger = get_logger('simple_diverse_search')
    
    # 測試組合
    test_combinations = [
        ("machine learning engineer", "Sydney NSW 2000"),
        ("data scientist", "Melbourne VIC 3000"),
        ("ai engineer", "Brisbane QLD 4000"),
        ("software engineer", "Perth WA 6000"),
        ("data analyst", "Adelaide SA 5000")
    ]
    
    logger.info("開始多樣化搜索測試")
    logger.info(f"測試組合數: {len(test_combinations)}")
    
    results = []
    
    for keywords, location in test_combinations:
        try:
            result = await test_single_search(keywords, location)
            results.append(result)
            
            # 搜索間延遲
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"測試失敗: {e}")
            results.append({
                'keywords': keywords,
                'location': location,
                'jobs_found': 0,
                'success': False,
                'error': str(e),
                'sample_jobs': []
            })
    
    # 統計結果
    successful_searches = sum(1 for r in results if r['success'])
    total_jobs = sum(r['jobs_found'] for r in results)
    
    logger.info("\n" + "="*60)
    logger.info("搜索測試結果摘要")
    logger.info("="*60)
    logger.info(f"總測試搜索數: {len(test_combinations)}")
    logger.info(f"成功搜索數: {successful_searches}")
    logger.info(f"總找到職位數: {total_jobs}")
    logger.info(f"平均成功率: {successful_searches/len(test_combinations)*100:.1f}%")
    logger.info("")
    logger.info("詳細結果:")
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        logger.info(f"{status} {result['keywords']} in {result['location']}: {result['jobs_found']} jobs found")
        if result['error']:
            logger.info(f"   錯誤: {result['error']}")
    
    # 保存結果
    output_file = f"debug_output/simple_diverse_search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n完整結果已保存至: {output_file}")
    
    return results

if __name__ == '__main__':
    # 檢查虛擬環境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("已進入虛擬環境 ✓")
    else:
        print("警告：未進入虛擬環境，建議使用 `uv shell` 啟動虛擬環境")
    
    # 執行主程式
    results = asyncio.run(main())
    
    # 退出碼
    successful_count = sum(1 for r in results if r['success'])
    sys.exit(0 if successful_count > 0 else 1)