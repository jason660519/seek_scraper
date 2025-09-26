"""
整合版 SEEK ETL 執行腳本

整合 proxy 管理、反爬蟲機制、完整 ETL 流程的執行腳本
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.enhanced_seek_etl import EnhancedSeekETLWithProxy
from src.scrapers.seek_scraper import SeekScraper, SearchCriteria
from src.utils.logger import get_logger


class IntegratedSeekETLRunner:
    """
    整合版 SEEK ETL 執行器
    """
    
    def __init__(self, config_path: str = None):
        """
        初始化執行器
        
        Args:
            config_path: 配置文件路徑
        """
        self.config_path = config_path or 'config/etl_config.json'
        self.config = self._load_config()
        self.logger = get_logger('integrated_seek_etl')
        
        # 確保目錄存在
        self._ensure_directories()
        
        self.logger.info("整合版 SEEK ETL 執行器初始化完成")
    
    def _load_config(self) -> Dict[str, Any]:
        """載入配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"配置文件 {self.config_path} 不存在，使用預設配置")
            return self._get_default_config()
        except Exception as e:
            self.logger.error(f"載入配置文件失敗: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取預設配置"""
        return {
            # 基本設定
            'data_dir': 'data',
            'headless': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            
            # 搜尋條件
            'search_criteria': {
                'keywords': ['AI', 'Machine Learning', 'Data Scientist'],
                'location': 'All-Sydney-NSW',
                'max_pages': 2
            },
            
            # 爬蟲設定
            'scraper_config': {
                'base_url': 'https://www.seek.com.au',
                'timeout': 30,
                'request_delay': 2.0,
                'max_retries': 3,
                'max_pages': 2
            },
            
            # Proxy 配置
            'proxy_config': {
                'rotation_interval': 3,
                'failure_threshold': 2,
                'cooldown_period': 300,
                'max_consecutive_failures': 3,
                'max_fail_count': 3,
                'temp_invalid_retry_hours': 24,
                'validation_timeout': 10,
                'test_urls': [
                    'https://www.seek.com.au',
                    'https://httpbin.org/ip',
                    'https://www.google.com'
                ],
                'proxy_sources': {
                    'proxifly': {
                        'enabled': True,
                        'api_key': None,
                        'countries': ['AU', 'US', 'GB', 'CA'],
                        'protocols': ['http', 'https'],
                        'anonymity_levels': ['elite', 'anonymous']
                    }
                }
            },
            
            # 反爬蟲配置
            'anti_bot_config': {
                'enable_delay': True,
                'min_delay': 3.0,
                'max_delay': 10.0,
                'randomize_delay': True,
                'enable_user_agent_rotation': True,
                'enable_viewport_randomization': True
            },
            
            # 批次處理設定
            'batch_config': {
                'batch_size': 2,  # 較小的批次大小
                'batch_delay': 15,  # 較長的批次間延遲
                'max_concurrent': 1  # 限制並發數
            },
            
            # 輸出設定
            'output_config': {
                'save_raw_data': True,
                'save_processed_data': True,
                'save_statistics': True,
                'output_formats': ['json', 'csv']
            }
        }
    
    def _ensure_directories(self):
        """確保必要的目錄存在"""
        directories = [
            'data',
            'data/raw',
            'data/processed',
            'data/logs',
            'data/stats',
            'config'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    async def search_jobs(self, criteria: Dict[str, Any]) -> List[str]:
        """
        搜尋職位並獲取 URL 列表
        
        Args:
            criteria: 搜尋條件
            
        Returns:
            List[str]: 職位 URL 列表
        """
        self.logger.info(f"開始搜尋職位: {criteria}")
        
        # 創建搜尋條件物件
        search_criteria = SearchCriteria(
            keywords=criteria.get('keywords', ['AI']),
            location=criteria.get('location', ''),
            max_pages=criteria.get('max_pages', 2)
        )
        
        # 使用 SeekScraper 搜尋
        scraper = SeekScraper(self.config.get('scraper_config', {}))
        
        job_urls = []
        try:
            # 搜尋職位
            job_urls = await scraper.search_jobs(search_criteria)
            self.logger.info(f"搜尋完成，找到 {len(job_urls)} 個職位")
            
        except Exception as e:
            self.logger.error(f"搜尋職位失敗: {e}")
            
        finally:
            # 關閉 scraper
            await scraper.close()
        
        return job_urls
    
    async def run_etl_process(self, job_urls: List[str]) -> Dict[str, Any]:
        """
        執行完整的 ETL 流程
        
        Args:
            job_urls: 職位 URL 列表
            
        Returns:
            Dict[str, Any]: 執行結果統計
        """
        self.logger.info(f"開始 ETL 流程，處理 {len(job_urls)} 個職位")
        
        start_time = datetime.now()
        
        # 執行 ETL 流程
        async with EnhancedSeekETLWithProxy(self.config, self.logger) as etl:
            results = await etl.process_job_list(job_urls)
            
            # 儲存結果
            output_files = {}
            if results:
                if 'json' in self.config['output_config']['output_formats']:
                    json_path = etl.save_to_json(results)
                    output_files['json'] = str(json_path)
                    self.logger.info(f"JSON 檔案已儲存: {json_path}")
                
                if 'csv' in self.config['output_config']['output_formats']:
                    csv_path = etl.save_to_csv(results)
                    output_files['csv'] = str(csv_path)
                    self.logger.info(f"CSV 檔案已儲存: {csv_path}")
            
            # 獲取統計資訊
            stats = etl.get_statistics()
            stats.update({
                'total_time': (datetime.now() - start_time).total_seconds(),
                'output_files': output_files,
                'timestamp': start_time.isoformat()
            })
            
            return stats
    
    async def run_full_pipeline(self, search_criteria: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        執行完整的搜尋 + ETL 流程
        
        Args:
            search_criteria: 搜尋條件（可選）
            
        Returns:
            Dict[str, Any]: 完整流程統計
        """
        self.logger.info("開始完整流程（搜尋 + ETL）")
        
        # 使用配置中的搜尋條件或參數
        if search_criteria is None:
            search_criteria = self.config['search_criteria']
        
        # 步驟 1: 搜尋職位
        job_urls = await self.search_jobs(search_criteria)
        
        if not job_urls:
            self.logger.error("未找到任何職位，流程結束")
            return {
                'status': 'failed',
                'message': 'No jobs found',
                'timestamp': datetime.now().isoformat()
            }
        
        self.logger.info(f"找到 {len(job_urls)} 個職位，開始 ETL 流程")
        
        # 步驟 2: 執行 ETL
        etl_stats = await self.run_etl_process(job_urls)
        
        # 組合結果
        full_stats = {
            'status': 'success',
            'search_stats': {
                'total_jobs_found': len(job_urls),
                'search_criteria': search_criteria
            },
            'etl_stats': etl_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        # 儲存完整統計
        stats_file = Path('data/stats') / f'full_pipeline_stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(full_stats, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"完整流程完成，統計資訊已儲存: {stats_file}")
        
        return full_stats
    
    def print_summary(self, stats: Dict[str, Any]):
        """列印執行摘要"""
        print("\n" + "="*60)
        print("SEEK ETL 流程執行摘要")
        print("="*60)
        
        if stats.get('status') == 'success':
            search_stats = stats.get('search_stats', {})
            etl_stats = stats.get('etl_stats', {})
            
            print(f"搜尋結果:")
            print(f"  找到職位數: {search_stats.get('total_jobs_found', 0)}")
            print(f"  搜尋條件: {search_stats.get('search_criteria', {})}")
            
            print(f"\nETL 結果:")
            print(f"  總處理時間: {etl_stats.get('total_time', 0):.1f} 秒")
            print(f"  成功擷取: {etl_stats.get('successful_extractions', 0)}")
            print(f"  失敗擷取: {etl_stats.get('failed_extractions', 0)}")
            print(f"  成功率: {etl_stats.get('success_rate', 0):.1%}")
            
            output_files = etl_stats.get('output_files', {})
            if output_files:
                print(f"\n輸出檔案:")
                for format_type, file_path in output_files.items():
                    print(f"  {format_type.upper()}: {file_path}")
            
            print(f"\nProxy 統計:")
            proxy_stats = etl_stats.get('proxy_statistics', {})
            if proxy_stats:
                print(f"  總請求數: {proxy_stats.get('total_requests', 0)}")
                print(f"  成功請求: {proxy_stats.get('successful_requests', 0)}")
                print(f"  成功率: {proxy_stats.get('success_rate', 0):.2%}")
                print(f"  當前 Proxy: {proxy_stats.get('current_proxy', 'N/A')}")
            
        else:
            print(f"狀態: {stats.get('status', 'unknown')}")
            print(f"訊息: {stats.get('message', 'No message')}")
        
        print(f"\n執行時間: {stats.get('timestamp', 'N/A')}")
        print("="*60)


async def main():
    """主函數"""
    # 初始化執行器
    runner = IntegratedSeekETLRunner()
    
    try:
        # 執行完整流程
        print("開始執行整合版 SEEK ETL 流程...")
        stats = await runner.run_full_pipeline()
        
        # 列印摘要
        runner.print_summary(stats)
        
        return stats
        
    except KeyboardInterrupt:
        print("\n使用者中斷執行")
        return {'status': 'interrupted', 'timestamp': datetime.now().isoformat()}
    except Exception as e:
        print(f"\n執行失敗: {e}")
        runner.logger.error(f"執行失敗: {e}", exc_info=True)
        return {'status': 'error', 'message': str(e), 'timestamp': datetime.now().isoformat()}


if __name__ == '__main__':
    # 檢查虛擬環境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("已進入虛擬環境 ✓")
    else:
        print("警告：未進入虛擬環境，建議使用 `uv shell` 啟動虛擬環境")
    
    # 執行主程式
    result = asyncio.run(main())
    
    # 退出碼
    sys.exit(0 if result.get('status') == 'success' else 1)