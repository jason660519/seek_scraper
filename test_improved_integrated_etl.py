#!/usr/bin/env python3
"""
測試改進的整合 ETL，使用正確的 URL 格式
"""

import asyncio
import json
from pathlib import Path
from scripts.run_integrated_seek_etl import IntegratedSeekETLRunner
from src.utils.logger import get_logger

async def test_improved_integrated_etl():
    """測試改進的整合 ETL"""
    logger = get_logger('test_integrated')
    
    # 創建 ETL runner，使用測試配置（禁用代理）
    runner = IntegratedSeekETLRunner(config_path='config/test_config.json')
    
    # 搜索條件 - 使用正確的格式
    search_criteria = {
        "keywords": "ai-machine-learning-data-scientist",
        "location": "in-Sydney-NSW-2000",
        "max_pages": 1,
        "jobs_per_page": 20
    }
    
    try:
        # 運行 ETL
        logger.info("開始運行改進的整合 ETL...")
        results = await runner.run_full_pipeline(search_criteria)
        
        logger.info(f"ETL 完成，狀態: {results.get('status', 'unknown')}")
        
        # 保存結果
        output_file = Path("test_results_improved.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"結果已保存到: {output_file}")
        
        # 打印摘要
        runner.print_summary(results)
        
        return results
        
    except Exception as e:
        logger.error(f"ETL 運行失敗: {e}")
        return []

if __name__ == '__main__':
    print("開始測試改進的整合 ETL...")
    results = asyncio.run(test_improved_integrated_etl())
    print(f"測試完成，結果狀態: {results.get('status', 'unknown')}")