#!/usr/bin/env python3
"""
SEEK Job Crawler 主程序

這個模組是整個 SEEK 工作爬蟲的入口點，負責協調各個組件來完成工作搜索、
詳情抓取、數據解析和存儲的完整流程。

ETL 流程：
1. Raw 資料抓取：從 SEEK 網站提取每個工作的原始 HTML 和相關資源
2. HTML 解析：將 raw 資料夾中的 HTML 解析為結構化的 JSON/CSV 數據
"""

import asyncio
import sys
from pathlib import Path

# 將 src 目錄添加到 Python 路徑
sys.path.append(str(Path(__file__).parent))

from config.settings import load_config
from models.search_criteria import SearchCriteria
from scrapers.seek_scraper import SeekScraper
from services.database import DatabaseService
from services.proxy_manager import ProxyManager
from services.raw_data_extractor import RawDataExtractor
from services.html_to_json_parser import HtmlToJsonParser
from utils.logger import get_logger


async def main():
    """
    主函數 - 協調整個爬蟲 ETL 流程
    """
    logger = get_logger(__name__)
    logger.info("開始 SEEK 爬蟲 ETL 任務...")
    
    try:
        # 加載配置
        config = load_config()
        logger.info("配置加載完成")
        
        # 創建代理管理器
        proxy_manager = ProxyManager()
        await proxy_manager.initialize()
        logger.info("代理管理器初始化完成")
        
        # 創建 Raw 資料提取器
        raw_data_extractor = RawDataExtractor(
            output_dir=Path("data/raw"),
            proxy_manager=proxy_manager
        )
        await raw_data_extractor.initialize()
        logger.info("Raw 資料提取器初始化完成")
        
        # 創建 HTML 解析器
        html_parser = HtmlToJsonParser()
        logger.info("HTML 解析器初始化完成")
        
        # 創建搜索條件
        search_criteria = SearchCriteria(
            keywords="Software Engineer",
            location="Sydney",
            job_type="Full Time"
        )
        
        logger.info(f"搜索條件: {search_criteria}")
        
        # Step 1: Raw 資料抓取
        logger.info("Step 1: 開始 Raw 資料抓取...")
        
        # 從搜索結果中提取工作
        job_folders = await raw_data_extractor.extract_from_search_results(
            search_criteria=search_criteria,
            max_jobs=10  # 限制數量用於測試
        )
        
        logger.info(f"Raw 資料抓取完成，共提取 {len(job_folders)} 個工作")
        
        # Step 2: HTML 解析轉 JSON/CSV
        logger.info("Step 2: 開始 HTML 解析...")
        
        # 解析 raw 資料夾
        raw_data_folder = Path("data/raw")
        processed_data_folder = Path("data/processed")
        
        # 轉換為 JSON
        json_success = html_parser.convert_folder_to_json(
            input_folder=raw_data_folder,
            output_folder=processed_data_folder / "json"
        )
        
        # 轉換為 CSV
        csv_success = html_parser.convert_folder_to_csv(
            input_folder=raw_data_folder,
            output_folder=processed_data_folder / "csv"
        )
        
        if json_success and csv_success:
            logger.info("HTML 解析完成，成功生成 JSON 和 CSV 文件")
        else:
            logger.warning("HTML 解析部分完成")
        
        logger.info("SEEK 爬蟲 ETL 任務完成")
        
    except Exception as e:
        logger.error(f"爬蟲 ETL 任務失敗: {e}")
        raise
    
    finally:
        # 清理資源
        if 'raw_data_extractor' in locals():
            await raw_data_extractor.cleanup()
        if 'proxy_manager' in locals():
            await proxy_manager.cleanup()
        logger.info("資源清理完成")


if __name__ == "__main__":
    # 使用 asyncio 運行主函數
    asyncio.run(main())