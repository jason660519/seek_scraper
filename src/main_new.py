"""
新的Seek ETL主程式 - 使用重構後的架構
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

from src.scrapers.seek_crawler import SeekCrawler
from src.utils.seek_url_builder import SeekURLBuilder
from src.utils.logger import setup_global_logging, get_logger


async def main():
    """新的主函數，使用重構後的架構"""
    
    # 設置日誌
    setup_global_logging(
        level='INFO',
        log_file='logs/seek_crawler_new.log'
    )
    logger = get_logger(__name__)
    
    logger.info("開始新的Seek爬蟲流程...")
    
    try:
        # 配置
        keywords = ['data scientist', 'machine learning', 'AI engineer']
        locations = ['Sydney NSW', 'Melbourne VIC']
        
        # 創建爬蟲
        crawler = SeekCrawler(
            headless=True,
            output_dir='data/raw'
        )
        
        # 啟動爬蟲
        await crawler.start()
        
        # 執行爬蟲
        stats = await crawler.crawl_jobs(
            keywords=keywords,
            locations=locations,
            max_pages=2  # 限制頁數用於測試
        )
        
        logger.info(f"爬蟲完成，統計信息: {stats}")
        
        # 解析數據
        logger.info("開始解析原始數據...")
        
        raw_data_dir = Path('data/raw')
        processed_data_dir = Path('data/processed')
        processed_data_dir.mkdir(parents=True, exist_ok=True)
        
        all_jobs = []
        
        # 遍歷所有原始數據文件夾
        for job_folder in raw_data_dir.iterdir():
            if not job_folder.is_dir():
                continue
                
            try:
                # 讀取元數據
                metadata_file = job_folder / "metadata.json"
                if not metadata_file.exists():
                    continue
                
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # 提取所需字段
                job_data = {
                    'seek_url': metadata.get('url', ''),
                    'job_detail_title': metadata.get('title', ''),
                    'job_detail_location': metadata.get('location', ''),
                    'job_detail_classifications': metadata.get('classification', ''),
                    'job_detail_work_type': metadata.get('work_type', ''),
                    'job_detail_salary': metadata.get('salary', ''),
                    'jobAdDetails': metadata.get('description', ''),
                    'scraped_at': metadata.get('scraped_at', ''),
                    'company': metadata.get('company', ''),
                    'folder_name': job_folder.name
                }
                
                all_jobs.append(job_data)
                
            except Exception as e:
                logger.error(f"解析文件夾 {job_folder} 失敗: {e}")
                continue
        
        # 保存處理後的數據
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存JSON
        json_file = processed_data_dir / f"seek_jobs_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_jobs, f, ensure_ascii=False, indent=2)
        
        logger.info(f"處理後的數據已保存到: {json_file}")
        logger.info(f"共處理 {len(all_jobs)} 個職位")
        
        return {
            'total_jobs': len(all_jobs),
            'raw_data_dir': str(raw_data_dir),
            'processed_data_dir': str(processed_data_dir),
            'json_file': str(json_file),
            'timestamp': timestamp
        }
        
    except Exception as e:
        logger.error(f"執行過程中出現錯誤: {e}")
        raise
        
    finally:
        # 清理資源
        if 'crawler' in locals():
            await crawler.stop()
        logger.info("資源清理完成")


if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\n爬蟲執行完成！")
    print(f"共處理 {result['total_jobs']} 個職位")
    print(f"原始數據目錄: {result['raw_data_dir']}")
    print(f"處理後數據文件: {result['json_file']}")