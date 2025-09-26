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
from src.scrapers import PlaywrightScraper
from src.services.proxy_manager import ProxyManager
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
            
            # 搜尋條件 - 根據 SEEK URL 結構優化
            'search_criteria': {
                'keywords': ['AI', 'Machine Learning', 'Data Scientist'],
                'location': 'in-All-Sydney-NSW',  # SEEK 標準位置格式
                'max_pages': 2,
                'url_pattern': 'https://www.seek.com.au/{keyword}-jobs/{location}?page={page}',  # SEEK URL 模式
                'follow_redirects': True,  # 允許重定向
                'respect_robots_txt': True,  # 遵守 robots.txt
                'request_timeout': 30  # 請求超時時間
            },
            
            # 爬蟲設定 - 增強反爬蟲配置
            'scraper_config': {
                'base_url': 'https://www.seek.com.au',
                'timeout': 30,
                'request_delay': 3.0,  # 增加延遲以避免被檢測
                'max_retries': 3,
                'max_pages': 2,
                'proxy_enabled': True,  # 啟用代理
                'proxy_rotation': True,  # 啟用代理輪換
                'user_agent_rotation': True,  # 啟用 User-Agent 輪換
                'viewport_randomization': True,  # 啟用視窗大小隨機化
                'enable_stealth': True,  # 啟用隱身模式
                'respect_robots_txt': True,  # 遵守 robots.txt
                'follow_redirects': True,  # 允許重定向
                'max_redirects': 5,  # 最大重定向次數
                'verify_ssl': True,  # SSL 驗證
                'allow_cookies': True,  # 允許 cookies
                'custom_headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
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
                },
                'use_proxy': True,  # 明確啟用代理
                'proxy_rotation': True,  # 啟用代理輪換
                'proxy_retry_count': 3  # 代理重試次數
            },
            
            # 反爬蟲配置 - 根據 SEEK 特性優化
            'anti_bot_config': {
                'enable_delay': True,
                'min_delay': 3.0,  # 最小延遲 3 秒（SEEK 建議）
                'max_delay': 8.0,  # 最大延遲 8 秒
                'randomize_delay': True,
                'enable_user_agent_rotation': True,
                'enable_viewport_randomization': True,
                'enable_mouse_movement': True,  # 啟用鼠標移動模擬
                'enable_scroll_simulation': True,  # 啟用滾動模擬
                'enable_click_simulation': True,  # 啟用點擊模擬
                'page_load_timeout': 30,  # 頁面加載超時
                'script_timeout': 10,  # 腳本執行超時
                'wait_for_network_idle': True,  # 等待網絡空閒
                'bypass_cdp_detection': True,  # 繞過 Chrome DevTools 檢測
                'disable_webdriver_detection': True,  # 禁用 WebDriver 檢測
                'preserve_user_preferences': True,  # 保持用戶偏好設置
                'randomize_canvas_fingerprint': True,  # 隨機化 Canvas 指紋
                'randomize_webgl_fingerprint': True,  # 隨機化 WebGL 指紋
                'randomize_audio_fingerprint': True,  # 隨機化音頻指紋
                'enable_session_persistence': True  # 啟用會話持久化
            },
            
            # 批次處理設定 - 針對 SEEK 優化
            'batch_config': {
                'batch_size': 1,  # 單個處理以避免被檢測
                'batch_delay': 10,  # 批次間延遲 10 秒
                'max_concurrent': 1,  # 限制並發數為 1
                'page_delay': 5,  # 頁面間延遲 5 秒
                'job_delay': 8,  # 工作間延遲 8 秒
                'enable_jitter': True,  # 啟用隨機抖動
                'jitter_range': [0.5, 2.0],  # 抖動範圍
                'retry_on_failure': True,  # 失敗時重試
                'max_retries': 3,  # 最大重試次數
                'backoff_factor': 2.0  # 退避因子
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
    
    def _get_working_proxies(self) -> List[str]:
        """
        從代理管理系統獲取工作代理列表
        
        Returns:
            List[str]: 工作代理列表
        """
        import requests
        import json
        
        try:
            # 從代理管理API獲取工作代理
            response = requests.get('http://localhost:5000/api/proxies', timeout=10)
            if response.status_code == 200:
                proxy_data = response.json()
                working_proxies = []
                
                # 提取工作代理
                for proxy in proxy_data.get('proxies', []):
                    if proxy.get('status') == 'active' and proxy.get('success_rate', 0) > 0.5:
                        proxy_url = f"{proxy['protocol']}://{proxy['ip']}:{proxy['port']}"
                        working_proxies.append(proxy_url)
                
                self.logger.info(f"從代理管理系統獲取 {len(working_proxies)} 個工作代理")
                return working_proxies[:10]  # 限制使用前10個代理
            else:
                self.logger.warning(f"無法從代理管理API獲取代理，狀態碼: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"獲取工作代理失敗: {e}")
        
        # 返回默認代理列表（本地代理管理器）
        return [
            'http://localhost:8080',
            'http://localhost:8081',
            'http://localhost:8082'
        ]
    
    async def search_jobs(self, criteria: Dict[str, Any]) -> List[str]:
        """
        搜尋職位並獲取 URL 列表
        
        Args:
            criteria: 搜尋條件
            
        Returns:
            List[str]: 職位 URL 列表
        """
        self.logger.info(f"開始搜尋職位: {criteria}")
        
        # 創建搜尋條件物件 - 根據 SEEK URL 結構優化
        keywords = criteria.get('keywords', ['AI'])
        location = criteria.get('location', 'in-All-Sydney-NSW')  # 默認位置格式
        
        # 處理關鍵詞格式（SEEK 使用連字符連接）
        if isinstance(keywords, list):
            # 先處理每個關鍵詞中的空格，然後用連字符連接
            processed_keywords = [str(k).lower().replace(' ', '-') for k in keywords]
            keyword_str = '-'.join(processed_keywords)
        else:
            keyword_str = str(keywords).lower().replace(' ', '-')
        
        # 處理位置格式（將空格替換為連字符，符合 SEEK URL 格式）
        if location:
            location = str(location).replace(' ', '-')
            if not location.startswith('in-'):
                location = f'in-{location}'
        
        search_criteria = SearchCriteria(
            keyword=keyword_str,
            location=location
        )
        
        self.logger.info(f"搜尋條件: 關鍵詞='{keyword_str}', 位置='{location}'")
        
        # 使用 PlaywrightScraper 搜尋（支援更好的反爬蟲功能）
        from src.services.proxy_manager import ProxyManager
        from src.scrapers.playwright_scraper import PlaywrightScraper
        
        # 初始化代理管理器
        proxy_manager = ProxyManager()
        
        # 創建 PlaywrightScraper
        scraper = PlaywrightScraper(proxy_manager=proxy_manager, logger=self.logger)
        
        job_urls = []
        try:
            async with scraper:
                # 構建 SEEK 搜尋 URL
                base_url = "https://www.seek.com.au"
                search_url = f"{base_url}/{search_criteria.keyword}-jobs"
                if search_criteria.location:
                    search_url += f"/{search_criteria.location}"
                
                self.logger.info(f"開始搜尋: {search_url}")
                
                # 導航到搜尋頁面
                success = await scraper.navigate_to_url(search_url)
                if not success:
                    self.logger.error(f"無法導航到搜尋頁面: {search_url}")
                    return []
                
                # 提取工作連結
                job_urls = await scraper.extract_job_links()
                self.logger.info(f"找到 {len(job_urls)} 個工作連結")
                
                # 如果需要多頁，提取總頁數並遍歷
                max_pages = criteria.get('max_pages', 2)
                if max_pages > 1:
                    total_pages = await scraper.extract_total_pages()
                    pages_to_scrape = min(total_pages, max_pages)
                    
                    self.logger.info(f"總頁數: {total_pages}, 將爬取: {pages_to_scrape} 頁")
                    
                    # 遍歷其他頁面
                    for page in range(2, pages_to_scrape + 1):
                        try:
                            # 構建分頁 URL
                            page_url = f"{search_url}?page={page}"
                            self.logger.info(f"爬取第 {page} 頁: {page_url}")
                            
                            # 導航到分頁
                            success = await scraper.navigate_to_url(page_url)
                            if success:
                                # 提取該頁面的工作連結
                                page_job_urls = await scraper.extract_job_links()
                                job_urls.extend(page_job_urls)
                                self.logger.info(f"第 {page} 頁找到 {len(page_job_urls)} 個工作連結")
                            else:
                                self.logger.warning(f"無法導航到第 {page} 頁")
                                break
                                
                            # 頁面間延遲
                            await asyncio.sleep(5)
                            
                        except Exception as e:
                            self.logger.error(f"爬取第 {page} 頁失敗: {e}")
                            break
                
                self.logger.info(f"搜尋完成，總共找到 {len(job_urls)} 個職位")
                
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
            try:
                # 嘗試獲取 ETL 統計資訊
                stats = etl.get_statistics() if hasattr(etl, 'get_statistics') else {}
            except AttributeError:
                # 如果 EnhancedSeekETLWithProxy 沒有 get_statistics 方法，
                # 嘗試從 proxy_rotator 獲取統計資訊
                try:
                    if hasattr(etl, 'proxy_rotator') and hasattr(etl.proxy_rotator, 'get_statistics'):
                        proxy_stats = etl.proxy_rotator.get_statistics()
                        stats = {'proxy_statistics': proxy_stats}
                    else:
                        stats = {}
                except Exception as e:
                    self.logger.warning(f"無法獲取統計資訊: {e}")
                    stats = {}
            
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