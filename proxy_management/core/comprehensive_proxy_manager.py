"""
綜合代理管理系統
提供完整的代理獲取、驗證、分類和管理功能
"""

import asyncio
import json
import csv
import time
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProxyStatus(Enum):
    """代理狀態枚舉"""
    VALID = "valid"           # 有效代理
    TEMP_INVALID = "temp_invalid"  # 暫時無效（可重試）
    INVALID = "invalid"       # 永久失效
    UNTESTED = "untested"     # 未測試


@dataclass
class ProxyInfo:
    """代理信息數據類"""
    ip: str
    port: int
    protocol: str  # http, https, socks4, socks5
    country: str = ""
    anonymity: str = ""
    response_time: float = 0.0
    status: ProxyStatus = ProxyStatus.UNTESTED
    last_tested: Optional[datetime] = None
    fail_count: int = 0
    last_success: Optional[datetime] = None
    source: str = ""
    
    def to_dict(self) -> Dict:
        """轉換為字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProxyInfo':
        """從字典創建實例"""
        # 處理狀態字段
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = ProxyStatus(data['status'])
        
        # 處理日期字段
        for field in ['last_tested', 'last_success']:
            if field in data and data[field]:
                if isinstance(data[field], str):
                    data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)


class ComprehensiveProxyManager:
    """綜合代理管理器"""
    
    def __init__(self, data_dir: str = "proxy_management/data/comprehensive"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 定義各類代理的存儲文件
        self.files = {
            'valid': self.data_dir / "valid_proxies.json",
            'temp_invalid': self.data_dir / "temp_invalid_proxies.json", 
            'invalid': self.data_dir / "invalid_proxies.json",
            'untested': self.data_dir / "untested_proxies.json",
            'stats': self.data_dir / "proxy_stats.json"
        }
        
        # 配置參數
        self.config = {
            'max_fail_count': 3,           # 最大失敗次數
            'temp_invalid_retry_hours': 6, # 暫時無效代理重試間隔（小時）
            'validation_timeout': 10,      # 驗證超時時間（秒）
            'test_urls': [                  # 測試URL列表
                'http://httpbin.org/ip',
                'https://httpbin.org/ip',
                'http://icanhazip.com',
                'https://api.ipify.org?format=json'
            ],
            'proxy_sources': [              # 代理源配置
                {
                    'name': 'proxifly',
                    'base_url': 'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols',
                    'protocols': ['http', 'socks4', 'socks5']
                },
                {
                    'name': 'proxylist',
                    'url': 'https://www.proxy-list.download/api/v1/get?type={protocol}',
                    'protocols': ['http', 'https', 'socks4', 'socks5']
                }
            ]
        }
        
        # 初始化存儲
        self._initialize_storage()
        
        # 線程池
        self.executor = ThreadPoolExecutor(max_workers=50)
    
    def _initialize_storage(self):
        """初始化存儲文件"""
        for file_path in self.files.values():
            if not file_path.exists():
                if 'stats' in str(file_path):
                    self._save_stats({})
                else:
                    self._save_proxies([])
    
    def _load_proxies(self, status: ProxyStatus) -> List[ProxyInfo]:
        """加載指定狀態的代理"""
        file_path = self.files[status.value]
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [ProxyInfo.from_dict(proxy) for proxy in data]
        except Exception as e:
            logger.error(f"加載代理文件失敗 {file_path}: {e}")
            return []
    
    def _save_proxies(self, proxies: List[ProxyInfo], status: ProxyStatus = None):
        """保存代理列表"""
        if status is None:
            # 根據代理狀態分組保存
            status_groups = {}
            for proxy in proxies:
                if proxy.status.value not in status_groups:
                    status_groups[proxy.status.value] = []
                status_groups[proxy.status.value].append(proxy.to_dict())
            
            for status_value, proxy_list in status_groups.items():
                file_path = self.files[status_value]
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(proxy_list, f, ensure_ascii=False, indent=2, default=str)
        else:
            # 保存到指定狀態文件
            file_path = self.files[status.value]
            data = [proxy.to_dict() for proxy in proxies]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def _load_stats(self) -> Dict:
        """加載統計信息"""
        file_path = self.files['stats']
        if not file_path.exists():
            return self._create_default_stats()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加載統計信息失敗: {e}")
            return self._create_default_stats()
    
    def _save_stats(self, stats: Dict):
        """保存統計信息"""
        file_path = self.files['stats']
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
    
    def _create_default_stats(self) -> Dict:
        """創建默認統計信息"""
        return {
            'total_fetched': 0,
            'total_valid': 0,
            'total_invalid': 0,
            'total_temp_invalid': 0,
            'last_fetch_time': None,
            'last_validation_time': None,
            'validation_history': [],
            'source_stats': {}
        }
    
    def fetch_proxies_from_proxifly(self, protocol: str = 'http', country: str = None) -> List[ProxyInfo]:
        """從Proxifly獲取代理"""
        try:
            url = f"https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/{protocol}/data.txt"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            proxies = []
            for line in response.text.strip().split('\n'):
                if ':' in line:
                    ip, port = line.strip().split(':')
                    proxy = ProxyInfo(
                        ip=ip,
                        port=int(port),
                        protocol=protocol,
                        source='proxifly',
                        status=ProxyStatus.UNTESTED
                    )
                    proxies.append(proxy)
            
            logger.info(f"從Proxifly獲取到 {len(proxies)} 個 {protocol} 代理")
            return proxies
            
        except Exception as e:
            logger.error(f"從Proxifly獲取代理失敗: {e}")
            return []
    
    def fetch_proxies_from_multiple_sources(self) -> List[ProxyInfo]:
        """從多個源獲取代理"""
        all_proxies = []
        
        # 從Proxifly獲取
        for protocol in ['http', 'socks4', 'socks5']:
            proxies = self.fetch_proxies_from_proxifly(protocol)
            all_proxies.extend(proxies)
        
        # 去重
        seen = set()
        unique_proxies = []
        for proxy in all_proxies:
            key = f"{proxy.ip}:{proxy.port}:{proxy.protocol}"
            if key not in seen:
                seen.add(key)
                unique_proxies.append(proxy)
        
        logger.info(f"總共獲取到 {len(unique_proxies)} 個唯一代理")
        return unique_proxies
    
    def _test_proxy_sync(self, proxy: ProxyInfo, test_url: str) -> Tuple[bool, float]:
        """同步測試單個代理"""
        try:
            proxy_url = f"{proxy.protocol}://{proxy.ip}:{proxy.port}"
            
            # 配置代理
            if proxy.protocol in ['socks4', 'socks5']:
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            else:
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            
            start_time = time.time()
            response = requests.get(
                test_url,
                proxies=proxies,
                timeout=self.config['validation_timeout'],
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return True, response_time
            else:
                return False, 0.0
                
        except Exception as e:
            return False, 0.0
    
    def validate_proxy_batch(self, proxies: List[ProxyInfo], batch_size: int = 50) -> List[ProxyInfo]:
        """批量驗證代理"""
        logger.info(f"開始批量驗證 {len(proxies)} 個代理")
        
        # 隨機選擇測試URL
        test_url = random.choice(self.config['test_urls'])
        
        # 分批處理
        for i in range(0, len(proxies), batch_size):
            batch = proxies[i:i + batch_size]
            logger.info(f"驗證第 {i//batch_size + 1} 批，共 {len(batch)} 個代理")
            
            # 使用線程池驗證
            futures = []
            for proxy in batch:
                future = self.executor.submit(self._test_proxy_sync, proxy, test_url)
                futures.append((proxy, future))
            
            # 收集結果
            for proxy, future in futures:
                is_valid, response_time = future.result()
                
                # 更新代理信息
                proxy.last_tested = datetime.now()
                proxy.response_time = response_time
                
                if is_valid:
                    # 代理有效
                    proxy.status = ProxyStatus.VALID
                    proxy.fail_count = 0
                    proxy.last_success = datetime.now()
                    logger.debug(f"代理 {proxy.ip}:{proxy.port} 有效，響應時間: {response_time:.2f}s")
                else:
                    # 代理無效
                    proxy.fail_count += 1
                    
                    if proxy.fail_count >= self.config['max_fail_count']:
                        proxy.status = ProxyStatus.INVALID
                        logger.debug(f"代理 {proxy.ip}:{proxy.port} 永久失效（失敗次數: {proxy.fail_count}）")
                    else:
                        proxy.status = ProxyStatus.TEMP_INVALID
                        logger.debug(f"代理 {proxy.ip}:{proxy.port} 暫時無效（失敗次數: {proxy.fail_count}）")
        
        return proxies
    
    def retry_temp_invalid_proxies(self) -> List[ProxyInfo]:
        """重試暫時無效的代理"""
        temp_invalid_proxies = self._load_proxies(ProxyStatus.TEMP_INVALID)
        
        # 篩選需要重試的代理（超過重試間隔）
        retry_proxies = []
        current_time = datetime.now()
        retry_interval = timedelta(hours=self.config['temp_invalid_retry_hours'])
        
        for proxy in temp_invalid_proxies:
            if proxy.last_tested and (current_time - proxy.last_tested) >= retry_interval:
                proxy.status = ProxyStatus.UNTESTED
                retry_proxies.append(proxy)
        
        if retry_proxies:
            logger.info(f"找到 {len(retry_proxies)} 個需要重試的暫時無效代理")
            validated_proxies = self.validate_proxy_batch(retry_proxies)
            
            # 更新統計
            stats = self._load_stats()
            stats['last_validation_time'] = datetime.now().isoformat()
            self._save_stats(stats)
            
            return validated_proxies
        
        return []
    
    def get_proxy_statistics(self) -> Dict:
        """獲取代理統計信息"""
        valid_proxies = self._load_proxies(ProxyStatus.VALID)
        temp_invalid_proxies = self._load_proxies(ProxyStatus.TEMP_INVALID)
        invalid_proxies = self._load_proxies(ProxyStatus.INVALID)
        untested_proxies = self._load_proxies(ProxyStatus.UNTESTED)
        
        # 計算協議分布
        protocol_stats = {}
        for proxy in valid_proxies:
            protocol = proxy.protocol
            protocol_stats[protocol] = protocol_stats.get(protocol, 0) + 1
        
        # 計算國家分布
        country_stats = {}
        for proxy in valid_proxies:
            country = proxy.country or 'unknown'
            country_stats[country] = country_stats.get(country, 0) + 1
        
        # 計算平均響應時間
        avg_response_time = 0
        if valid_proxies:
            avg_response_time = sum(p.response_time for p in valid_proxies) / len(valid_proxies)
        
        return {
            'valid_count': len(valid_proxies),
            'temp_invalid_count': len(temp_invalid_proxies),
            'invalid_count': len(invalid_proxies),
            'untested_count': len(untested_proxies),
            'total_proxies': len(valid_proxies) + len(temp_invalid_proxies) + len(invalid_proxies) + len(untested_proxies),
            'protocol_distribution': protocol_stats,
            'country_distribution': country_stats,
            'average_response_time': avg_response_time,
            'last_updated': datetime.now().isoformat()
        }
    
    def export_proxies(self, format_type: str = 'json', status: ProxyStatus = ProxyStatus.VALID) -> str:
        """導出代理"""
        proxies = self._load_proxies(status)
        export_dir = self.data_dir / "exports"
        export_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{status.value}_proxies_{timestamp}.{format_type}"
        file_path = export_dir / filename
        
        if format_type == 'json':
            data = [proxy.to_dict() for proxy in proxies]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        elif format_type == 'txt':
            with open(file_path, 'w', encoding='utf-8') as f:
                for proxy in proxies:
                    f.write(f"{proxy.ip}:{proxy.port}\n")
        
        elif format_type == 'csv':
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                if proxies:
                    fieldnames = ['ip', 'port', 'protocol', 'country', 'anonymity', 'response_time', 'status', 'source']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for proxy in proxies:
                        writer.writerow({
                            'ip': proxy.ip,
                            'port': proxy.port,
                            'protocol': proxy.protocol,
                            'country': proxy.country,
                            'anonymity': proxy.anonymity,
                            'response_time': proxy.response_time,
                            'status': proxy.status.value,
                            'source': proxy.source
                        })
        
        logger.info(f"導出 {len(proxies)} 個 {status.value} 代理到 {file_path}")
        return str(file_path)
    
    def run_full_cycle(self):
        """運行完整的代理管理週期"""
        logger.info("開始完整代理管理週期")
        
        # 1. 重試暫時無效代理
        logger.info("步驟1: 重試暫時無效代理")
        retried_proxies = self.retry_temp_invalid_proxies()
        
        # 2. 獲取新代理
        logger.info("步驟2: 獲取新代理")
        new_proxies = self.fetch_proxies_from_multiple_sources()
        
        # 3. 驗證代理
        logger.info("步驟3: 驗證代理")
        all_untested = new_proxies + [p for p in retried_proxies if p.status == ProxyStatus.UNTESTED]
        validated_proxies = self.validate_proxy_batch(all_untested)
        
        # 4. 保存結果
        logger.info("步驟4: 保存結果")
        self._save_proxies(validated_proxies)
        
        # 5. 更新統計
        logger.info("步驟5: 更新統計")
        stats = self.get_proxy_statistics()
        self._save_stats(stats)
        
        logger.info("完整代理管理週期完成")
        return stats
    
    def __del__(self):
        """析構函數"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)


if __name__ == "__main__":
    # 測試綜合代理管理器
    manager = ComprehensiveProxyManager()
    
    # 運行完整週期
    stats = manager.run_full_cycle()
    
    # 打印統計信息
    print("代理統計信息:")
    print(f"有效代理: {stats['valid_count']}")
    print(f"暫時無效代理: {stats['temp_invalid_count']}")
    print(f"永久失效代理: {stats['invalid_count']}")
    print(f"未測試代理: {stats['untested_count']}")
    print(f"總代理數: {stats['total_proxies']}")
    print(f"平均響應時間: {stats['average_response_time']:.2f}秒")