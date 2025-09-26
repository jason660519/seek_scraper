#!/usr/bin/env python3
"""
使用 IntegratedSeekETLRunner 測試多樣化搜索
基於之前成功的經驗
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 將當前目錄添加到 Python 路徑
sys.path.append(str(Path(__file__).parent))

from scripts.run_integrated_seek_etl import IntegratedSeekETLRunner
from src.utils.logger import get_logger

async def test_diverse_searches():
    """測試多樣化搜索"""
    logger = get_logger('diverse_search_runner')
    
    # 創建 ETL runner，使用測試配置（禁用代理）
    runner = IntegratedSeekETLRunner(config_path='config/test_config.json')
    
    # 多樣化搜索組合
    search_combinations = [
        {"keywords": "ai-machine-learning-data-scientist", "location": "in-Sydney-NSW-2000"},
        {"keywords": "data-scientist-machine-learning", "location": "in-Melbourne-VIC-3000"},
        {"keywords": "software-engineer-developer", "location": "in-Brisbane-QLD-4000"},
        {"keywords": "data-analyst-business-analyst", "location": "in-Perth-WA-6000"},
        {"keywords": "python-developer-backend", "location": "in-Adelaide-SA-5000"}
    ]
    
    results = []
    total_jobs = 0
    successful_searches = 0
    
    for i, combo in enumerate(search_combinations, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"測試搜索 {i}/{len(search_combinations)}")
        logger.info(f"關鍵詞: {combo['keywords']}")
        logger.info(f"地點: {combo['location']}")
        logger.info(f"{'='*60}")
        
        try:
            # 搜索條件
            search_criteria = {
                "keywords": combo['keywords'],
                "location": combo['location'],
                "max_pages": 1,
                "jobs_per_page": 20
            }
            
            # 運行 ETL
            logger.info("開始搜索...")
            result = await runner.run_full_pipeline(search_criteria)
            
            jobs_found = len(result.get('jobs', []))
            success = result.get('status') == 'completed' and jobs_found > 0
            
            if success:
                successful_searches += 1
                total_jobs += jobs_found
                logger.info(f"✅ 找到 {jobs_found} 個職位")
            else:
                logger.warning(f"❌ 未找到職位 (狀態: {result.get('status', 'unknown')})")
                if result.get('error'):
                    logger.warning(f"錯誤信息: {result['error']}")
            
            results.append({
                "keywords": combo['keywords'],
                "location": combo['location'],
                "jobs_found": jobs_found,
                "success": success,
                "status": result.get('status'),
                "error": result.get('error')
            })
            
            # 延遲以避免過快請求
            if i < len(search_combinations):
                logger.info("等待 5 秒後繼續下一個搜索...")
                await asyncio.sleep(5)
                
        except Exception as e:
            logger.error(f"搜索失敗: {e}")
            results.append({
                "keywords": combo['keywords'],
                "location": combo['location'],
                "jobs_found": 0,
                "success": False,
                "error": str(e)
            })
    
    # 總結報告
    logger.info(f"\n{'='*60}")
    logger.info("搜索測試結果摘要")
    logger.info(f"{'='*60}")
    logger.info(f"總測試搜索數: {len(search_combinations)}")
    logger.info(f"成功搜索數: {successful_searches}")
    logger.info(f"總找到職位數: {total_jobs}")
    logger.info(f"平均成功率: {(successful_searches/len(search_combinations)*100):.1f}%")
    logger.info(f"\n詳細結果:")
    
    for result in results:
        status_icon = "✅" if result['success'] else "❌"
        logger.info(f"{status_icon} {result['keywords']} in {result['location']}: {result['jobs_found']} jobs found")
        if not result['success'] and result.get('error'):
            logger.info(f"   錯誤: {result['error']}")
    
    # 保存結果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"debug_output/diverse_search_runner_results_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "summary": {
                "total_searches": len(search_combinations),
                "successful_searches": successful_searches,
                "total_jobs": total_jobs,
                "success_rate": (successful_searches/len(search_combinations)*100)
            },
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n完整結果已保存至: {output_file}")
    
    return results

if __name__ == '__main__':
    print("開始測試多樣化搜索（使用 IntegratedSeekETLRunner）...")
    results = asyncio.run(test_diverse_searches())
    print(f"測試完成，找到 {sum(r['jobs_found'] for r in results)} 個職位")