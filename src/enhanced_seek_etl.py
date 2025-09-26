"""
增強版 SEEK ETL 主程式（整合 Proxy 管理）

提供完整的 ETL 流程，整合 proxy 輪換、反爬蟲機制：
1. 智能 proxy 輪換
2. 反偵測機制
3. 自動重試與降級
4. 完整的錯誤處理
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
from playwright.async_api import async_playwright

# 添加專案根目錄到 Python 路徑
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.seek_etl import SeekETL
from src.proxy_integration import EnhancedSeekETL, ProxyRotator
from src.scrapers.seek_scraper import SeekScraper
from src.models import SearchCriteria, JobPost
from src.utils.logger import get_logger


class EnhancedSeekETLWithProxy(SeekETL):
    """
    增強版 SEEK ETL，整合 proxy 管理與反爬蟲機制
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        初始化增強版 ETL
        
        Args:
            config: 配置物件
            logger: 日誌記錄器
        """
        # 呼叫父類初始化
        super().__init__(config, logger)
        
        # Proxy 輪換器
        self.proxy_rotator = ProxyRotator(config.get('proxy_config', {}), logger)
        
        # 反爬蟲配置
        self.anti_bot_config = config.get('anti_bot_config', {
            'enable_delay': True,
            'min_delay': 1.0,
            'max_delay': 5.0,
            'randomize_delay': True,
            'enable_user_agent_rotation': True,
            'enable_viewport_randomization': True
        })
        
        # User Agent 池
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
        ]
        
        # 視窗大小池
        self.viewport_sizes = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1440, 'height': 900},
            {'width': 1536, 'height': 864},
            {'width': 1280, 'height': 720}
        ]
        
        self.logger.info("增強版 SEEK ETL（含 Proxy）初始化完成")
    
    async def __aenter__(self):
        """異步上下文管理器進入"""
        await super().__aenter__()
        await self.proxy_rotator.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器退出"""
        await super().__aexit__(exc_type, exc_val, exc_tb)
    
    def _get_random_user_agent(self) -> str:
        """獲取隨機 User Agent"""
        if self.anti_bot_config.get('enable_user_agent_rotation'):
            return random.choice(self.user_agents)
        return self.config.get('user_agent', self.user_agents[0])
    
    def _get_random_viewport(self) -> Dict[str, int]:
        """獲取隨機視窗大小"""
        if self.anti_bot_config.get('enable_viewport_randomization'):
            return random.choice(self.viewport_sizes)
        return {'width': 1920, 'height': 1080}
    
    def _get_random_delay(self) -> float:
        """獲取隨機延遲時間"""
        if not self.anti_bot_config.get('enable_delay'):
            return 0
        
        min_delay = self.anti_bot_config.get('min_delay', 1.0)
        max_delay = self.anti_bot_config.get('max_delay', 5.0)
        
        if self.anti_bot_config.get('randomize_delay'):
            return random.uniform(min_delay, max_delay)
        else:
            return min_delay
    
    async def _init_browser(self):
        """重寫瀏覽器初始化，整合反爬蟲機制"""
        self.logger.info("初始化增強版 Playwright 瀏覽器（含反爬蟲）...")
        
        # 獲取隨機配置
        user_agent = self._get_random_user_agent()
        viewport = self._get_random_viewport()
        
        # 先初始化 Playwright（不重複創建 browser）
        self.playwright = await async_playwright().start()
        
        # 配置瀏覽器參數（反偵測）
        browser_config = {
            'headless': self.config.get('headless', True),
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                '--disable-web-security',
                '--disable-features=BlockInsecurePrivateNetworkRequests',
                '--disable-features=OutOfBlinkCors',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--single-process',
                '--disable-gpu'
            ]
        }
        
        self.browser = await self.playwright.chromium.launch(**browser_config)
        
        # 配置上下文參數（包含隨機 user agent 和 viewport）
        context_config = {
            'viewport': viewport,
            'user_agent': user_agent,
            'locale': 'en-US',
            'timezone_id': 'Australia/Sydney',
            'permissions': ['geolocation'],
            'geolocation': {'latitude': -33.8688, 'longitude': 151.2093},  # 雪梨
            'color_scheme': 'light',
            'device_scale_factor': 1,
            'is_mobile': False,
            'has_touch': False,
            'java_script_enabled': True,
            'bypass_csp': True,
            'ignore_https_errors': True
        }
        
        self.context = await self.browser.new_context(**context_config)
        
        # 添加基礎反偵測腳本
        await self.context.add_init_script("""
            // 隱藏自動化特徵
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // 修改插件資訊
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // 修改語言資訊
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // 移除 Chrome 自動化標記
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """)
        
        # 添加更多反偵測腳本
        await self.context.add_init_script("""
                // 進階反偵測腳本
                
                // 隱藏 webdriver 屬性
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                    configurable: true
                });
                
                // 修改插件資訊
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {
                            0: {
                                type: "application/x-google-chrome-pdf",
                                suffixes: "pdf",
                                description: "Portable Document Format",
                                enabledPlugin: Plugin
                            },
                            description: "Portable Document Format",
                            filename: "internal-pdf-viewer",
                            length: 1,
                            name: "Chrome PDF Plugin"
                        }
                    ]
                });
                
                // 修改語言資訊
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                    configurable: true
                });
                
                // 修改平台資訊
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32',
                    configurable: true
                });
                
                // 移除自動化標記
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                
                // 修改 Chrome 運行時標記
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {
                        return {
                            commitLoadTime: performance.timing.domContentLoadedEventStart / 1000,
                            connectionInfo: 'h2',
                            firstPaintAfterLoadTime: 0,
                            firstPaintTime: performance.timing.domContentLoadedEventStart / 1000,
                            navigationType: 'Other',
                            npnNegotiatedProtocol: 'h2',
                            requestTime: performance.timing.requestStart / 1000,
                            startLoadTime: performance.timing.requestStart / 1000
                        };
                    }
                };
                
                // 模擬真實的時間戳
                const originalQuerySelector = document.querySelector;
                document.querySelector = function(selector) {
                    const start = performance.now();
                    const result = originalQuerySelector.call(this, selector);
                    const end = performance.now();
                    
                    // 添加微小的延遲來模擬真實操作
                    if (end - start < 0.1) {
                        const wait = Math.random() * 50 + 10;
                        const startWait = performance.now();
                        while (performance.now() - startWait < wait) {
                            // 忙等待
                        }
                    }
                    
                    return result;
                };
            """)
    
    async def extract_raw_data(self, job_url: str) -> Optional[Dict[str, Any]]:
        """
        重寫 raw 資料擷取，整合 proxy 和反爬蟲機制
        """
        # 添加隨機延遲
        delay = self._get_random_delay()
        if delay > 0:
            self.logger.info(f"反爬蟲延遲: {delay:.1f} 秒")
            await asyncio.sleep(delay)
        
        # 獲取當前 proxy
        current_proxy = self.proxy_rotator.get_current_proxy()
        self.logger.info(f"使用 proxy: {current_proxy}")
        
        try:
            # 呼叫父類的擷取方法
            result = await super().extract_raw_data(job_url)
            
            if result:
                # 記錄成功
                await self.proxy_rotator.record_success(current_proxy)
            else:
                # 記錄失敗
                await self.proxy_rotator.record_failure(current_proxy, 'extraction_failed')
            
            return result
            
        except Exception as e:
            self.logger.error(f"增強版 raw 資料擷取失敗: {job_url} - {e}")
            await self.proxy_rotator.record_failure(current_proxy, 'exception')
            return None
    
    async def process_job_list(self, job_urls: List[str], batch_size: int = 3) -> List[Dict[str, Any]]:
        """
        重寫職位列表處理，整合 proxy 輪換
        """
        self.logger.info(f"開始增強版處理 {len(job_urls)} 個職位（含 proxy 輪換）")
        
        # 初始化統計
        self.stats['total_jobs'] = len(job_urls)
        self.stats['start_time'] = datetime.now()
        
        results = []
        
        # 批次處理（減小批次大小以避免被封鎖）
        effective_batch_size = min(batch_size, 3)  # 限制批次大小
        
        for i in range(0, len(job_urls), effective_batch_size):
            batch = job_urls[i:i + effective_batch_size]
            batch_num = i // effective_batch_size + 1
            total_batches = (len(job_urls) + effective_batch_size - 1) // effective_batch_size
            
            self.logger.info(f"處理批次 {batch_num}/{total_batches} ({len(batch)} 個職位)")
            
            # 批次前輪換 proxy
            await self.proxy_rotator.get_next_proxy()
            
            # 處理當前批次
            batch_results = await asyncio.gather(*[
                self.process_single_job_with_retry(url) for url in batch
            ], return_exceptions=True)
            
            # 處理結果
            for result in batch_results:
                if isinstance(result, Exception):
                    self.logger.error(f"處理職位時發生異常: {result}")
                elif result:
                    results.append(result)
            
            # 批次間延遲（增加延遲時間）
            if i + effective_batch_size < len(job_urls):
                batch_delay = 5 + random.uniform(3, 7)  # 8-12 秒延遲
                self.logger.info(f"批次間延遲: {batch_delay:.1f} 秒")
                await asyncio.sleep(batch_delay)
        
        self.stats['end_time'] = datetime.now()
        self._save_processing_stats()
        self._save_proxy_stats()
        
        self.logger.info(f"增強版處理完成，成功: {self.stats['successful_extractions']}, 失敗: {self.stats['failed_extractions']}")
        
        return results
    
    async def process_single_job_with_retry(self, job_url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        處理單個職位（含重試機制）
        
        Args:
            job_url: 職位 URL
            max_retries: 最大重試次數
            
        Returns:
            Optional[Dict]: 處理結果
        """
        for attempt in range(max_retries + 1):
            try:
                result = await self.process_single_job(job_url)
                if result:
                    return result
                elif attempt < max_retries:
                    self.logger.warning(f"處理失敗，準備重試 ({attempt + 1}/{max_retries}): {job_url}")
                    await asyncio.sleep(2 ** attempt)  # 指數退避
                    
            except Exception as e:
                self.logger.error(f"處理異常 (嘗試 {attempt + 1}/{max_retries + 1}): {job_url} - {e}")
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)  # 指數退避
        
        return None
    
    def _save_proxy_stats(self):
        """儲存 proxy 使用統計"""
        proxy_stats_file = self.processed_dir / 'proxy_usage_stats.json'
        
        try:
            proxy_stats = self.proxy_rotator.get_statistics()
            
            with open(proxy_stats_file, 'w', encoding='utf-8') as f:
                json.dump(proxy_stats, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"Proxy 使用統計已儲存: {proxy_stats_file}")
            
        except Exception as e:
            self.logger.error(f"儲存 proxy 統計失敗: {e}")
    
    def parse_job_data(self, html_content: str, job_url: str) -> Optional[Dict[str, Any]]:
        """解析職位數據（別名方法，用於測試兼容性）"""
        return self.parse_job_details(html_content, job_url)


async def main():
    """主函數 - 測試增強版 ETL"""
    # 配置
    config = {
        # 基本設定
        'data_dir': 'data',
        'headless': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        
        # 爬蟲設定
        'scraper_config': {
            'base_url': 'https://www.seek.com.au',
            'timeout': 30,
            'request_delay': 2.0,
            'max_retries': 3,
            'max_pages': 3
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
            ]
        },
        
        # 反爬蟲配置
        'anti_bot_config': {
            'enable_delay': True,
            'min_delay': 2.0,
            'max_delay': 8.0,
            'randomize_delay': True,
            'enable_user_agent_rotation': True,
            'enable_viewport_randomization': True
        },
        
        # 批次處理設定
        'batch_config': {
            'batch_size': 2,  # 較小的批次大小
            'batch_delay': 10,  # 較長的批次間延遲
            'max_concurrent': 1  # 限制並發數
        }
    }
    
    # 測試 URL 列表（實際使用時應該從搜尋結果獲取）
    test_urls = [
        'https://www.seek.com.au/job/12345678',
        'https://www.seek.com.au/job/87654321',
        'https://www.seek.com.au/job/56789123'
    ]
    
    # 執行增強版 ETL 流程
    async with EnhancedSeekETLWithProxy(config) as etl:
        results = await etl.process_job_list(test_urls)
        
        # 儲存結果
        if results:
            csv_path = etl.save_to_csv(results)
            json_path = etl.save_to_json(results)
            
            print(f"增強版 ETL 流程完成！")
            print(f"CSV 檔案: {csv_path}")
            print(f"JSON 檔案: {json_path}")
            print(f"處理職位數: {len(results)}")
            
            # 輸出統計資訊
            proxy_stats = etl.proxy_rotator.get_statistics()
            print(f"Proxy 使用統計:")
            print(f"  總請求數: {proxy_stats['total_requests']}")
            print(f"  成功請求: {proxy_stats['successful_requests']}")
            print(f"  成功率: {proxy_stats['success_rate']:.2%}")
            print(f"  當前 Proxy: {proxy_stats['current_proxy']}")


if __name__ == '__main__':
    asyncio.run(main())