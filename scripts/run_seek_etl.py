#!/usr/bin/env python3
"""
SEEK ETL 執行腳本

執行完整的 ETL 流程：
1. 搜尋職位
2. 擷取 raw 資料
3. 解析並轉換為結構化資料
4. 儲存結果
"""

import asyncio
import json
import logging
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.seek_etl import SeekETL
from scrapers.seek_scraper import SeekScraper
from src.models import SearchCriteria
from src.utils.logger import get_logger


def load_config() -> Dict[str, Any]:
    """載入配置"""
    config = {
        # 基本設定
        'data_dir': 'data',
        'headless': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        
        # 爬蟲設定
        'scraper_config': {
            'base_url': 'https://www.seek.com.au',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'timeout': 30,
            'request_delay': 1.0,
            'max_retries': 3,
            'max_pages': 5,
            'use_proxy': True,
            'proxy_rotation': True
        },
        
        # 反爬蟲設定
        'anti_bot_config': {
            'enable_delay': True,
            'min_delay': 1.0,
            'max_delay': 3.0,
            'randomize_user_agent': True,
            'enable_stealth': True
        },
        
        # 批次處理設定
        'batch_config': {
            'batch_size': 3,  # 每批次處理的職位數量
            'batch_delay': 5,  # 批次間延遲（秒）
            'max_concurrent': 2  # 最大並發數
        }
    }
    
    return config


async def search_jobs_with_criteria(scraper: SeekScraper, criteria: SearchCriteria) -> List[str]:
    """
    根據搜尋條件搜尋職位
    
    Args:
        scraper: SeekScraper 實例
        criteria: 搜尋條件
        
    Returns:
        List[str]: 職位 URL 列表
    """
    logger = logging.getLogger(__name__)
    logger.info(f"開始搜尋職位: {criteria.keywords} in {criteria.location}")
    
    try:
        # 執行搜尋
        job_urls = await scraper.search_jobs(criteria)
        
        logger.info(f"找到 {len(job_urls)} 個職位")
        
        # 獲取爬蟲統計資訊
        stats = scraper.get_statistics()
        logger.info(f"爬蟲統計: {stats}")
        
        return job_urls
        
    except Exception as e:
        logger.error(f"搜尋職位失敗: {e}")
        return []


async def run_etl_process(job_urls: List[str], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    執行 ETL 流程
    
    Args:
        job_urls: 職位 URL 列表
        config: ETL 配置
        
    Returns:
        List[Dict]: 處理結果
    """
    logger = logging.getLogger(__name__)
    logger.info(f"開始 ETL 流程，處理 {len(job_urls)} 個職位")
    
    results = []
    
    # 使用 ETL 處理器
    async with SeekETL(config) as etl:
        # 批次處理
        batch_size = config['batch_config']['batch_size']
        batch_delay = config['batch_config']['batch_delay']
        
        for i in range(0, len(job_urls), batch_size):
            batch = job_urls[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(job_urls) + batch_size - 1) // batch_size
            
            logger.info(f"處理批次 {batch_num}/{total_batches} ({len(batch)} 個職位)")
            
            # 處理當前批次
            batch_results = await etl.process_job_list(batch, batch_size)
            results.extend(batch_results)
            
            # 批次間延遲（除了最後一個批次）
            if i + batch_size < len(job_urls):
                delay = batch_delay + random.uniform(0, 2)  # 添加隨機延遲
                logger.info(f"批次間延遲 {delay:.1f} 秒")
                await asyncio.sleep(delay)
    
    logger.info(f"ETL 流程完成，成功處理 {len(results)} 個職位")
    
    return results


async def save_results(results: List[Dict[str, Any]], output_dir: Path) -> Dict[str, str]:
    """
    儲存處理結果
    
    Args:
        results: 處理結果
        output_dir: 輸出目錄
        
    Returns:
        Dict[str, str]: 輸出檔案路徑
    """
    logger = logging.getLogger(__name__)
    
    # 生成時間戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 儲存 JSON
    json_file = output_dir / f"seek_jobs_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    # 儲存 CSV
    csv_file = output_dir / f"seek_jobs_{timestamp}.csv"
    if results and 'parsed_data' in results[0]:
        import csv
        fieldnames = list(results[0]['parsed_data'].keys()) + ['raw_data_path', 'extraction_time']
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                if result and 'parsed_data' in result:
                    row = result['parsed_data'].copy()
                    row['raw_data_path'] = result.get('raw_data_path', '')
                    row['extraction_time'] = result.get('extraction_time', '')
                    writer.writerow(row)
    
    logger.info(f"結果已儲存: JSON={json_file}, CSV={csv_file}")
    
    return {
        'json': str(json_file),
        'csv': str(csv_file)
    }


async def main():
    """主函數"""
    # 設定日誌
    logger = get_logger(__name__)
    logger.info("SEEK ETL 執行腳本啟動")
    
    try:
        # 載入配置
        config = load_config()
        logger.info("配置載入完成")
        
        # 搜尋條件
        search_criteria = SearchCriteria(
            keywords='AI Engineer',  # 可以修改為其他關鍵字
            location='Sydney NSW',   # 可以修改為其他地點
            work_type='fulltime',    # fulltime, parttime, contract, etc.
            salary_range='100k-150k' # 薪資範圍
        )
        
        # 初始化爬蟲
        scraper = SeekScraper(config['scraper_config'])
        
        # 步驟 1: 搜尋職位
        job_urls = await search_jobs_with_criteria(scraper, search_criteria)
        
        if not job_urls:
            logger.warning("未找到任何職位，結束執行")
            return
        
        # 限制處理數量（測試用）
        max_jobs = 10  # 可以修改為更大的數字
        if len(job_urls) > max_jobs:
            job_urls = job_urls[:max_jobs]
            logger.info(f"限制處理數量為 {max_jobs} 個職位")
        
        # 步驟 2: 執行 ETL 流程
        results = await run_etl_process(job_urls, config)
        
        if not results:
            logger.warning("ETL 流程未產生任何結果")
            return
        
        # 步驟 3: 儲存結果
        output_dir = Path('data/processed')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_files = await save_results(results, output_dir)
        
        # 輸出摘要
        logger.info("=" * 50)
        logger.info("SEEK ETL 執行完成")
        logger.info(f"處理職位數: {len(results)}")
        logger.info(f"JSON 輸出: {output_files['json']}")
        logger.info(f"CSV 輸出: {output_files['csv']}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"執行失敗: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    # 檢查 Python 版本
    if sys.version_info < (3, 8):
        print("錯誤: 需要 Python 3.8 或更高版本")
        sys.exit(1)
    
    # 執行主函數
    asyncio.run(main())