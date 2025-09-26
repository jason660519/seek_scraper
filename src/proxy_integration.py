"""
Proxy 整合模組

整合 proxy_management 系統到 SEEK ETL 流程中，提供：
1. Proxy 輪換機制
2. Proxy 健康檢查
3. 自動重試與降級策略
4. 反爬蟲增強
"""

import asyncio
import logging
import random
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import aiohttp
from dataclasses import dataclass
from datetime import datetime, timedelta

# 添加專案根目錄到 Python 路徑
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import sys
from pathlib import Path

# 添加 proxy_management 到 Python 路徑
proxy_management_path = Path(__file__).parent.parent / "proxy_management" / "core"
sys.path.insert(0, str(proxy_management_path))

from comprehensive_proxy_manager import ComprehensiveProxyManager, ProxyStatus
from proxy_validator import ProxyValidator
from src.utils.logger import get_logger


@dataclass
class ProxyUsageStats:
    """Proxy 使用統計"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    blocked_requests: int = 0
    last_used: Optional[datetime] = None
    consecutive_failures: int = 0


class ProxyRotator:
    """
    Proxy 輪換器
    
    管理 proxy 的生命週期，提供智能輪換和錯誤處理
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        初始化 Proxy 輪換器
        
        Args:
            config: 配置物件
            logger: 日誌記錄器
        """
        self.config = config
        self.logger = logger or get_logger(__name__)
        
        # Proxy 管理器
        self.proxy_manager = ComprehensiveProxyManager()
        
        # 更新代理管理器配置
        self.proxy_manager.config.update({
            'max_fail_count': config.get('max_fail_count', 3),
            'temp_invalid_retry_hours': config.get('temp_invalid_retry_hours', 24),
            'validation_timeout': config.get('validation_timeout', 10)
        })
        
        # Proxy 驗證器
        self.validator = ProxyValidator(
            timeout=config.get('validation_timeout', 10)
        )
        
        # 設置測試 URL
        self.validator.test_urls = config.get('test_urls', [
            'https://www.seek.com.au',
            'https://httpbin.org/ip',
            'https://www.google.com'
        ])
        
        # 使用統計
        self.usage_stats: Dict[str, ProxyUsageStats] = {}
        
        # 輪換策略配置
        self.rotation_config = {
            'rotation_interval': config.get('rotation_interval', 5),  # 每 N 個請求輪換一次
            'failure_threshold': config.get('failure_threshold', 2),  # 失敗閾值
            'cooldown_period': config.get('cooldown_period', 300),  # 冷卻期（秒）
            'max_consecutive_failures': config.get('max_consecutive_failures', 3)
        }
        
        # 當前 proxy
        self.current_proxy: Optional[str] = None
        self.request_count = 0
        self.last_rotation = datetime.now()
        
        # 鎖定機制
        self._proxy_lock = asyncio.Lock()
        
        self.logger.info("Proxy 輪換器初始化完成")
    
    async def initialize(self):
        """初始化 proxy 池"""
        self.logger.info("初始化 proxy 池...")
        
        # 載入 proxy 來源
        proxies = self.proxy_manager.fetch_proxies_from_multiple_sources()
        
        # 驗證 proxy
        validated_proxies = self.proxy_manager.validate_proxy_batch(proxies)
        
        # 獲取可用 proxy 列表
        valid_proxies = [p for p in validated_proxies if p.status == ProxyStatus.VALID]
        
        self.logger.info(f"初始化完成，可用 proxy 數量: {len(valid_proxies)}")
        
        if not valid_proxies:
            self.logger.warning("沒有可用的 proxy，將使用直接連接")
    
    def get_current_proxy(self) -> Optional[str]:
        """獲取當前 proxy"""
        return self.current_proxy
    
    async def get_next_proxy(self) -> Optional[str]:
        """
        獲取下一個 proxy
        
        Returns:
            Optional[str]: proxy 地址或 None（使用直接連接）
        """
        async with self._proxy_lock:
            # 檢查是否需要輪換
            if self._should_rotate():
                await self._rotate_proxy()
            
            return self.current_proxy
    
    def _should_rotate(self) -> bool:
        """檢查是否需要輪換 proxy"""
        # 基於請求數量的輪換
        if self.request_count >= self.rotation_config['rotation_interval']:
            return True
        
        # 基於時間的輪換
        time_since_last = datetime.now() - self.last_rotation
        if time_since_last.total_seconds() > self.rotation_config['cooldown_period']:
            return True
        
        # 如果當前 proxy 失敗次數過多
        if self.current_proxy and self.current_proxy in self.usage_stats:
            stats = self.usage_stats[self.current_proxy]
            if stats.consecutive_failures >= self.rotation_config['max_consecutive_failures']:
                return True
        
        return False
    
    async def _rotate_proxy(self):
        """輪換到下一個 proxy"""
        self.logger.info("輪換 proxy...")
        
        # 獲取可用 proxy 列表
        valid_proxies = self.proxy_manager.get_proxies_by_status(ProxyStatus.VALID)
        
        if not valid_proxies:
            self.logger.warning("沒有可用的 proxy，使用直接連接")
            self.current_proxy = None
            return
        
        # 根據使用統計選擇最佳 proxy
        best_proxy = self._select_best_proxy(valid_proxies)
        
        if best_proxy:
            old_proxy = self.current_proxy
            self.current_proxy = best_proxy
            self.request_count = 0
            self.last_rotation = datetime.now()
            
            self.logger.info(f"Proxy 輪換完成: {old_proxy} -> {best_proxy}")
        else:
            self.logger.warning("無法選擇最佳 proxy，使用隨機選擇")
            self.current_proxy = random.choice(list(valid_proxies.keys()))
    
    def _select_best_proxy(self, valid_proxies: Dict[str, Any]) -> Optional[str]:
        """選擇最佳 proxy"""
        if not valid_proxies:
            return None
        
        # 計算每個 proxy 的分數
        proxy_scores = {}
        
        for proxy_url, proxy_info in valid_proxies.items():
            score = 0
            
            # 基礎分數（成功率）
            if proxy_url in self.usage_stats:
                stats = self.usage_stats[proxy_url]
                if stats.total_requests > 0:
                    success_rate = stats.successful_requests / stats.total_requests
                    score += success_rate * 100
                
                # 懲罰連續失敗
                score -= stats.consecutive_failures * 20
                
                # 懲罰最近使用過的 proxy
                if stats.last_used:
                    time_since_use = datetime.now() - stats.last_used
                    if time_since_use.total_seconds() < 60:  # 1 分鐘內使用過
                        score -= 30
            else:
                # 新 proxy 給予基礎分數
                score = 70
            
            # 響應時間獎勵
            if hasattr(proxy_info, 'response_time') and proxy_info.response_time:
                if proxy_info.response_time < 2:  # 快速響應
                    score += 20
                elif proxy_info.response_time < 5:  # 中等響應
                    score += 10
                else:  # 慢速響應
                    score -= 10
            
            proxy_scores[proxy_url] = score
        
        # 選擇分數最高的 proxy
        best_proxy = max(proxy_scores.items(), key=lambda x: x[1])[0]
        
        return best_proxy if proxy_scores[best_proxy] > 0 else None
    
    async def record_success(self, proxy_url: Optional[str]):
        """記錄成功請求"""
        if proxy_url:
            if proxy_url not in self.usage_stats:
                self.usage_stats[proxy_url] = ProxyUsageStats()
            
            stats = self.usage_stats[proxy_url]
            stats.total_requests += 1
            stats.successful_requests += 1
            stats.consecutive_failures = 0
            stats.last_used = datetime.now()
        
        self.request_count += 1
    
    async def record_failure(self, proxy_url: Optional[str], error_type: str = 'general'):
        """記錄失敗請求"""
        if proxy_url:
            if proxy_url not in self.usage_stats:
                self.usage_stats[proxy_url] = ProxyUsageStats()
            
            stats = self.usage_stats[proxy_url]
            stats.total_requests += 1
            stats.failed_requests += 1
            stats.consecutive_failures += 1
            stats.last_used = datetime.now()
            
            # 根據錯誤類型更新統計
            if error_type == 'blocked':
                stats.blocked_requests += 1
                # 標記 proxy 為暫時無效
                await self.proxy_manager.update_proxy_status(proxy_url, ProxyStatus.TEMP_INVALID)
            
            # 如果失敗次數過多，標記為無效
            if stats.consecutive_failures >= self.rotation_config['max_consecutive_failures']:
                await self.proxy_manager.update_proxy_status(proxy_url, ProxyStatus.INVALID)
        
        self.request_count += 1
    
    async def check_proxy_health(self, proxy_url: str) -> bool:
        """
        檢查 proxy 健康狀態
        
        Args:
            proxy_url: Proxy URL
            
        Returns:
            bool: Proxy 是否健康
        """
        try:
            # 使用 proxy 驗證器測試 proxy
            result = await self.validator.test_proxy_sync({
                'proxy': proxy_url,
                'proxy_type': 'http'
            })
            
            is_healthy = result.get('status', 'failed') == 'success'
            
            if is_healthy:
                await self.record_success(proxy_url)
            else:
                await self.record_failure(proxy_url, result.get('error', 'unknown'))
            
            return is_healthy
            
        except Exception as e:
            self.logger.error(f"檢查 proxy 健康狀態失敗: {e}")
            await self.record_failure(proxy_url, 'validation_error')
            return False
    
    async def close(self):
        """關閉 proxy 輪換器並清理資源"""
        self.logger.info("關閉 proxy 輪換器...")
        
        try:
            # 保存使用統計
            if self.usage_stats:
                self.logger.info(f"總共使用統計: {len(self.usage_stats)} 個 proxy")
                for proxy, stats in self.usage_stats.items():
                    self.logger.info(f"  {proxy}: {stats.total_requests} 請求, "
                                   f"{stats.successful_requests} 成功, "
                                   f"{stats.failed_requests} 失敗")
            
            # 清理資源
            self.current_proxy = None
            self.usage_stats.clear()
            
            self.logger.info("Proxy 輪換器已關閉")
            
        except Exception as e:
            self.logger.error(f"關閉 proxy 輪換器時發生錯誤: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        獲取 proxy 使用統計
        
        Returns:
            Dict[str, Any]: 統計資訊
        """
        total_requests = sum(stats.total_requests for stats in self.usage_stats.values())
        successful_requests = sum(stats.successful_requests for stats in self.usage_stats.values())
        failed_requests = sum(stats.failed_requests for stats in self.usage_stats.values())
        
        proxy_stats = {}
        for proxy, stats in self.usage_stats.items():
            proxy_stats[proxy] = {
                'total_requests': stats.total_requests,
                'successful_requests': stats.successful_requests,
                'failed_requests': stats.failed_requests,
                'success_rate': stats.successful_requests / max(stats.total_requests, 1),
                'consecutive_failures': stats.consecutive_failures,
                'last_used': stats.last_used.isoformat() if stats.last_used else None
            }
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'overall_success_rate': successful_requests / max(total_requests, 1),
            'active_proxy': self.current_proxy,
            'proxy_count': len(self.usage_stats),
            'proxy_details': proxy_stats
        }
    
    async def validate_proxy(self, proxy_url: str) -> bool:
        """驗證 proxy 可用性"""
        try:
            # 使用 proxy 驗證器
            is_valid = await self.validator.validate_proxy(proxy_url)
            
            if is_valid:
                await self.proxy_manager.update_proxy_status(proxy_url, ProxyStatus.VALID)
                self.logger.info(f"Proxy 驗證成功: {proxy_url}")
            else:
                await self.proxy_manager.update_proxy_status(proxy_url, ProxyStatus.TEMP_INVALID)
                self.logger.warning(f"Proxy 驗證失敗: {proxy_url}")
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f"Proxy 驗證異常: {proxy_url} - {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取使用統計"""
        total_requests = sum(stats.total_requests for stats in self.usage_stats.values())
        successful_requests = sum(stats.successful_requests for stats in self.usage_stats.values())
        failed_requests = sum(stats.failed_requests for stats in self.usage_stats.values())
        blocked_requests = sum(stats.blocked_requests for stats in self.usage_stats.values())
        
        # 獲取 proxy 狀態統計
        proxy_stats = self.proxy_manager.get_statistics()
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'blocked_requests': blocked_requests,
            'success_rate': successful_requests / max(total_requests, 1),
            'current_proxy': self.current_proxy,
            'request_count_since_rotation': self.request_count,
            'proxy_pool_stats': proxy_stats,
            'detailed_stats': {
                proxy_url: {
                    'total_requests': stats.total_requests,
                    'successful_requests': stats.successful_requests,
                    'failed_requests': stats.failed_requests,
                    'blocked_requests': stats.blocked_requests,
                    'success_rate': stats.successful_requests / max(stats.total_requests, 1),
                    'consecutive_failures': stats.consecutive_failures,
                    'last_used': stats.last_used.isoformat() if stats.last_used else None
                }
                for proxy_url, stats in self.usage_stats.items()
            }
        }


class EnhancedSeekETL:
    """
    增強版 SEEK ETL，整合 proxy 輪換
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        初始化增強版 ETL
        
        Args:
            config: 配置物件
            logger: 日誌記錄器
        """
        self.config = config
        self.logger = logger or get_logger(__name__)
        
        # Proxy 輪換器
        self.proxy_rotator = ProxyRotator(config.get('proxy_config', {}), logger)
        
        # 請求會話
        self.session: Optional[aiohttp.ClientSession] = None
        
        # 統計資訊
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'proxy_rotations': 0,
            'start_time': None,
            'end_time': None
        }
        
        # 重試配置
        self.retry_config = {
            'max_retries': config.get('max_retries', 3),
            'retry_delay': config.get('retry_delay', 2.0),
            'backoff_factor': config.get('backoff_factor', 2.0)
        }
        
        self.logger.info("增強版 SEEK ETL 初始化完成")
    
    async def __aenter__(self):
        """異步上下文管理器進入"""
        await self._init_session()
        await self.proxy_rotator.initialize()
        self.stats['start_time'] = datetime.now()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器退出"""
        await self._close_session()
        self.stats['end_time'] = datetime.now()
    
    async def _init_session(self):
        """初始化 HTTP 會話"""
        # 配置連接器
        connector = aiohttp.TCPConnector(
            limit=100,  # 總連接數限制
            limit_per_host=10,  # 每主機連接數限制
            ttl_dns_cache=300,  # DNS 快取時間
            use_dns_cache=True,
            keepalive_timeout=30
        )
        
        # 配置超時
        timeout = aiohttp.ClientTimeout(
            total=30,  # 總超時
            connect=10,  # 連接超時
            sock_read=20  # 讀取超時
        )
        
        # 創建會話
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': self.config.get('user_agent', 
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
        )
        
        self.logger.info("HTTP 會話初始化完成")
    
    async def _close_session(self):
        """關閉 HTTP 會話"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.logger.info("HTTP 會話已關閉")
    
    async def make_request(self, url: str, method: str = 'GET', **kwargs) -> aiohttp.ClientResponse:
        """
        發送 HTTP 請求（整合 proxy）
        
        Args:
            url: 請求 URL
            method: 請求方法
            **kwargs: 其他參數
            
        Returns:
            aiohttp.ClientResponse: 響應物件
        """
        max_retries = self.retry_config['max_retries']
        retry_delay = self.retry_config['retry_delay']
        
        for attempt in range(max_retries + 1):
            proxy_url = await self.proxy_rotator.get_next_proxy()
            
            try:
                # 配置 proxy
                if proxy_url:
                    kwargs['proxy'] = proxy_url
                    self.logger.debug(f"使用 proxy: {proxy_url}")
                
                # 發送請求
                self.stats['total_requests'] += 1
                
                async with self.session.request(method, url, **kwargs) as response:
                    # 檢查是否被封鎖
                    if self._is_blocked(response):
                        await self.proxy_rotator.record_failure(proxy_url, 'blocked')
                        if attempt < max_retries:
                            await asyncio.sleep(retry_delay * (self.retry_config['backoff_factor'] ** attempt))
                            continue
                        else:
                            raise aiohttp.ClientError(f"請求被封鎖: {url}")
                    
                    # 成功請求
                    await self.proxy_rotator.record_success(proxy_url)
                    self.stats['successful_requests'] += 1
                    
                    return response
                    
            except Exception as e:
                self.logger.warning(f"請求失敗 (嘗試 {attempt + 1}/{max_retries + 1}): {e}")
                await self.proxy_rotator.record_failure(proxy_url, 'general')
                
                if attempt < max_retries:
                    # 指數退避
                    delay = retry_delay * (self.retry_config['backoff_factor'] ** attempt)
                    await asyncio.sleep(delay)
                else:
                    self.stats['failed_requests'] += 1
                    raise
        
        raise aiohttp.ClientError(f"所有重試都失敗: {url}")
    
    def _is_blocked(self, response: aiohttp.ClientResponse) -> bool:
        """檢查是否被封鎖"""
        # 檢查狀態碼
        if response.status in [403, 429, 503]:
            return True
        
        # 檢查響應內容
        if response.content_type == 'text/html':
            # 這裡可以添加更多的封鎖檢測邏輯
            pass
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計資訊"""
        proxy_stats = self.proxy_rotator.get_statistics()
        
        return {
            'etl_stats': self.stats,
            'proxy_stats': proxy_stats,
            'success_rate': self.stats['successful_requests'] / max(self.stats['total_requests'], 1)
        }


# 測試函數
async def test_proxy_integration():
    """測試 proxy 整合"""
    config = {
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
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'max_retries': 3,
        'retry_delay': 2.0,
        'backoff_factor': 2.0
    }
    
    logger = get_logger(__name__)
    
    async with EnhancedSeekETL(config, logger) as etl:
        logger.info("開始測試 proxy 整合...")
        
        # 測試請求
        test_urls = [
            'https://httpbin.org/ip',
            'https://www.seek.com.au',
            'https://www.google.com'
        ]
        
        for url in test_urls:
            try:
                response = await etl.make_request(url)
                logger.info(f"請求成功: {url} - 狀態碼: {response.status}")
                
                if response.content_type == 'application/json':
                    data = await response.json()
                    logger.info(f"響應資料: {data}")
                
            except Exception as e:
                logger.error(f"請求失敗: {url} - {e}")
        
        # 輸出統計
        stats = etl.get_statistics()
        logger.info(f"統計資訊: {json.dumps(stats, indent=2, default=str)}")


if __name__ == '__main__':
    import json
    asyncio.run(test_proxy_integration())