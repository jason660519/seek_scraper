#!/usr/bin/env python3
"""
測試不同關鍵詞和地點的職位搜索
測試多種AI/ML相關職位關鍵詞在不同城市的搜索效果
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加src目錄到Python路徑
sys.path.append(str(Path(__file__).parent / "src"))

from scripts.run_integrated_seek_etl import IntegratedSeekETLRunner
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 定義測試的關鍵詞和地點組合
TEST_SEARCHES = [
    # AI/ML核心職位
    {"keywords": "machine learning engineer", "location": "Sydney NSW 2000"},
    {"keywords": "data scientist", "location": "Melbourne VIC 3000"},
    {"keywords": "ai engineer", "location": "Brisbane QLD 4000"},
    {"keywords": "deep learning", "location": "Perth WA 6000"},
    {"keywords": "nlp engineer", "location": "Adelaide SA 5000"},
    
    # 專業領域
    {"keywords": "computer vision", "location": "Sydney NSW 2000"},
    {"keywords": "machine learning operations", "location": "Melbourne VIC 3000"},
    {"keywords": "ai research", "location": "Canberra ACT 2600"},
    {"keywords": "prompt engineer", "location": "Sydney NSW 2000"},
    {"keywords": "llm engineer", "location": "Melbourne VIC 3000"},
    
    # 高級職位
    {"keywords": "senior machine learning", "location": "Sydney NSW 2000"},
    {"keywords": "lead data scientist", "location": "Melbourne VIC 3000"},
    {"keywords": "principal ai engineer", "location": "Brisbane QLD 4000"},
    {"keywords": "head of machine learning", "location": "Perth WA 6000"},
    
    # 相關技術
    {"keywords": "tensorflow", "location": "Sydney NSW 2000"},
    {"keywords": "pytorch", "location": "Melbourne VIC 3000"},
    {"keywords": "scikit-learn", "location": "Brisbane QLD 4000"},
    {"keywords": "huggingface", "location": "Sydney NSW 2000"},
]

async def test_search_combination(keywords: str, location: str, max_pages: int = 1):
    """測試特定的搜索組合"""
    logger.info(f"測試搜索: '{keywords}' in '{location}'")
    
    try:
        # 創建臨時配置文件
        temp_config = {
            "search_criteria": {
                "keywords": [keywords],
                "location": location,
                "max_pages": max_pages
            },
            "settings": {
                "headless": True,
                "use_proxy": False,
                "output_format": "json"
            }
        }
        
        # 保存臨時配置
        temp_config_path = f'temp_config_{keywords.replace(" ", "_")}_{location.replace(" ", "_")}.json'
        with open(temp_config_path, 'w', encoding='utf-8') as f:
            json.dump(temp_config, f, indent=2, ensure_ascii=False)
        
        # 運行搜索
        runner = IntegratedSeekETLRunner(config_path=temp_config_path)
        results = await runner.run_full_pipeline()
        
        # 清理臨時文件
        import os
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)
        
        return {
            "keywords": keywords,
            "location": location,
            "jobs_found": len(results.get("jobs", [])),
            "success": results.get("status") == "success",
            "error": results.get("error"),
            "sample_jobs": [job.get("job_detail_title", "Unknown") for job in results.get("jobs", [])[:3]]
        }
        
    except Exception as e:
        logger.error(f"搜索失敗: {keywords} in {location} - {str(e)}")
        return {
            "keywords": keywords,
            "location": location,
            "jobs_found": 0,
            "success": False,
            "error": str(e),
            "sample_jobs": []
        }

async def main():
    """主測試函數"""
    logger.info("開始多樣化搜索測試...")
    
    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 測試前5個搜索組合（加快測試速度）
    test_subset = TEST_SEARCHES[:5]
    
    for search_config in test_subset:
        result = await test_search_combination(
            search_config["keywords"],
            search_config["location"]
        )
        results.append(result)
        
        # 簡短延遲以避免過於頻繁
        await asyncio.sleep(2)
    
    # 保存結果
    output_file = Path("debug_output") / f"diverse_search_results_{timestamp}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 生成簡要報告
    logger.info("\n" + "="*60)
    logger.info("搜索測試結果摘要")
    logger.info("="*60)
    
    successful_searches = [r for r in results if r["success"]]
    total_jobs_found = sum(r["jobs_found"] for r in results)
    
    logger.info(f"總測試搜索數: {len(results)}")
    logger.info(f"成功搜索數: {len(successful_searches)}")
    logger.info(f"總找到職位數: {total_jobs_found}")
    logger.info(f"平均成功率: {len(successful_searches)/len(results)*100:.1f}%")
    
    logger.info("\n詳細結果:")
    for result in results:
        status_emoji = "✅" if result["success"] else "❌"
        logger.info(f"{status_emoji} {result['keywords']} in {result['location']}: "
                   f"{result['jobs_found']} jobs found")
        if result["sample_jobs"]:
            logger.info(f"   樣本: {', '.join(result['sample_jobs'])}")
    
    logger.info(f"\n完整結果已保存至: {output_file}")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(main())