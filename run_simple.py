#!/usr/bin/env python3
"""
Seek爬蟲簡化運行腳本

快速啟動Seek爬蟲的簡化版本
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime

# 將src目錄添加到Python路徑
import sys
sys.path.append(str(Path(__file__).parent / 'src'))

from src.scrapers.seek_crawler import SeekCrawler
from src.utils.logger import setup_global_logging, get_logger
from src.config import load_config as get_config, create_directories


async def run_simple_crawler():
    """簡化的爬蟲運行函數"""
    
    # 獲取配置
    config = get_config()
    
    # 創建必要的目錄
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # 設置日誌
    setup_global_logging(
        level=config['log_level'],
        log_file=f"{config['log_dir']}/seek_crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    
    logger = get_logger(__name__)
    logger.info("開始Seek爬蟲簡化版本...")
    
    try:
        # 創建爬蟲
        crawler = SeekCrawler(
            headless=config['headless'],
            output_dir=config['raw_data_dir']
        )
        
        # 啟動爬蟲
        await crawler.start()
        logger.info("爬蟲已啟動")
        
        # 執行爬蟲
        stats = await crawler.crawl_jobs(
            keywords=config['default_keywords'][:3],  # 限制關鍵詞數量
            locations=config['default_locations'][:2],  # 限制地點數量
            max_pages=2  # 限制頁數用於快速測試
        )
        
        logger.info(f"爬蟲統計: {stats}")
        
        # 簡單的數據解析
        raw_data_dir = Path(config['raw_data_dir'])
        processed_data_dir = Path(config['processed_data_dir'])
        processed_data_dir.mkdir(parents=True, exist_ok=True)
        
        jobs_data = []
        
        # 遍歷所有原始數據文件夾
        for job_folder in raw_data_dir.iterdir():
            if not job_folder.is_dir():
                continue
                
            metadata_file = job_folder / "metadata.json"
            if not metadata_file.exists():
                continue
            
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                job_info = {
                    'title': metadata.get('title', ''),
                    'company': metadata.get('company', ''),
                    'location': metadata.get('location', ''),
                    'url': metadata.get('url', ''),
                    'scraped_at': metadata.get('scraped_at', ''),
                    'folder': job_folder.name
                }
                
                jobs_data.append(job_info)
                
            except Exception as e:
                logger.error(f"解析文件夾 {job_folder} 失敗: {e}")
                continue
        
        # 保存結果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存JSON
        json_file = processed_data_dir / f"seek_jobs_simple_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"結果已保存到: {json_file}")
        logger.info(f"共處理 {len(jobs_data)} 個職位")
        
        return {
            'total_jobs': len(jobs_data),
            'json_file': str(json_file),
            'raw_data_dir': str(raw_data_dir),
            'processed_data_dir': str(processed_data_dir)
        }
        
    except Exception as e:
        logger.error(f"爬蟲執行失敗: {e}")
        raise
        
    finally:
        # 清理資源
        if 'crawler' in locals():
            await crawler.stop()
        logger.info("爬蟲已停止")


def main():
    """主函數"""
    print("Seek爬蟲簡化版本")
    print("=" * 50)
    
    try:
        result = asyncio.run(run_simple_crawler())
        
        print(f"\n✅ 爬蟲執行完成！")
        print(f"📊 統計信息:")
        print(f"   - 總職位數: {result['total_jobs']}")
        print(f"   - 原始數據目錄: {result['raw_data_dir']}")
        print(f"   - 處理後數據文件: {result['json_file']}")
        
    except KeyboardInterrupt:
        print("\n❌ 用戶中斷執行")
    except Exception as e:
        print(f"\n❌ 執行失敗: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)