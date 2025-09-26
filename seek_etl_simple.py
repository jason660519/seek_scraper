#!/usr/bin/env python3
"""
Seek職位爬蟲 - 重構版本

這是一個簡化的Seek職位爬蟲，支持：
- 關鍵詞和地點搜索
- 原始數據保存（HTML、截圖、元數據）
- HTML解析和結構化數據提取
- 日誌記錄和錯誤處理
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from src.scrapers.seek_crawler import SeekCrawler
from src.utils.logger import setup_global_logging, get_logger
from src.config import load_config


class SeekETLRunner:
    """Seek爬蟲ETL運行器"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.config = load_config()
        self.crawler = None
        
    async def initialize(self):
        """初始化運行器"""
        # 創建必要目錄
        os.makedirs('data/raw', exist_ok=True)
        os.makedirs('data/processed', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # 初始化爬蟲
        self.crawler = SeekCrawler()
        await self.crawler.start()
        
        self.logger.info("Seek ETL運行器初始化完成")
    
    async def crawl_phase(self, keywords: List[str], locations: List[str], max_pages: int = 3):
        """
        執行爬蟲階段
        
        Args:
            keywords: 搜索關鍵詞列表
            locations: 搜索地點列表
            max_pages: 每個搜索組合的最大頁數
        """
        self.logger.info(f"開始爬蟲階段 - 關鍵詞: {len(keywords)}, 地點: {len(locations)}, 最大頁數: {max_pages}")
        
        all_jobs = []
        
        for keyword in keywords:
            for location in locations:
                self.logger.info(f"搜索: {keyword} in {location}")
                
                try:
                    # 爬取職位
                    jobs = await self.crawler.crawl_jobs(
                        keywords=[keyword],
                        locations=[location],
                        max_pages=max_pages
                    )
                    
                    all_jobs.extend(jobs)
                    self.logger.info(f"找到 {len(jobs)} 個職位")
                    
                except Exception as e:
                    self.logger.error(f"搜索失敗 {keyword} in {location}: {e}")
                    continue
        
        self.logger.info(f"爬蟲階段完成，總共找到 {len(all_jobs)} 個職位")
        return all_jobs
    
    def parse_raw_data(self) -> List[Dict[str, Any]]:
        """
        解析原始數據文件夾中的數據
        
        Returns:
            List[Dict]: 解析後的職位數據列表
        """
        self.logger.info("開始解析原始數據")
        
        raw_data_dir = Path("data/raw")
        processed_jobs = []
        
        if not raw_data_dir.exists():
            self.logger.warning("原始數據目錄不存在")
            return processed_jobs
        
        # 遍歷所有職位文件夾
        for job_folder in raw_data_dir.iterdir():
            if not job_folder.is_dir():
                continue
            
            metadata_file = job_folder / "metadata.json"
            if not metadata_file.exists():
                self.logger.warning(f"缺少元數據文件: {metadata_file}")
                continue
            
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # 提取關鍵信息
                job_data = {
                    "seek_url": metadata.get("url", ""),
                    "job_detail_title": metadata.get("title", ""),
                    "job_detail_location": metadata.get("location", ""),
                    "company": metadata.get("company", ""),
                    "scraped_at": metadata.get("scraped_at", ""),
                    "folder_name": job_folder.name
                }
                
                processed_jobs.append(job_data)
                self.logger.debug(f"解析職位: {job_data['job_detail_title']}")
                
            except Exception as e:
                self.logger.error(f"解析文件夾失敗 {job_folder}: {e}")
                continue
        
        self.logger.info(f"解析完成，總共處理 {len(processed_jobs)} 個職位")
        return processed_jobs
    
    def save_processed_data(self, jobs: List[Dict[str, Any]], output_file: str = None):
        """
        保存處理後的數據
        
        Args:
            jobs: 職位數據列表
            output_file: 輸出文件路徑
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"data/processed/seek_jobs_{timestamp}.json"
        
        # 確保目錄存在
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # 保存數據
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"處理後的數據已保存到: {output_file}")
    
    async def run_etl(self, keywords: List[str] = None, locations: List[str] = None, max_pages: int = 3):
        """
        執行完整的ETL流程
        
        Args:
            keywords: 搜索關鍵詞列表
            locations: 搜索地點列表
            max_pages: 每個搜索組合的最大頁數
        """
        if keywords is None:
            keywords = ['software engineer', 'data scientist']
        if locations is None:
            locations = ['Sydney NSW', 'Melbourne VIC']
        
        self.logger.info("開始執行Seek ETL流程")
        
        try:
            # 階段1: 爬蟲
            await self.crawl_phase(keywords, locations, max_pages)
            
            # 階段2: 解析原始數據
            processed_jobs = self.parse_raw_data()
            
            # 階段3: 保存處理後的數據
            self.save_processed_data(processed_jobs)
            
            self.logger.info("Seek ETL流程完成")
            
        except Exception as e:
            self.logger.error(f"ETL流程失敗: {e}")
            raise
        
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """清理資源"""
        if self.crawler:
            await self.crawler.stop()
            self.logger.info("爬蟲資源已清理")


async def main():
    """主函數"""
    # 設置日誌
    setup_global_logging()
    
    # 創建運行器
    runner = SeekETLRunner()
    
    try:
        # 初始化
        await runner.initialize()
        
        # 運行ETL流程
        await runner.run_etl(
            keywords=['software engineer', 'data scientist'],
            locations=['Sydney NSW', 'Melbourne VIC'],
            max_pages=2
        )
        
    except Exception as e:
        print(f"程序執行失敗: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)