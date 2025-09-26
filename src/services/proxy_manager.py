"""
代理管理服務

整合 proxy_management 系統，提供有效的代理 IP 給爬蟲使用。
"""

import asyncio
import json
import logging
import random
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class ProxyConfig:
    """代理配置"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"
    
    @property
    def url(self) -> str:
        """生成代理 URL"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "protocol": self.protocol
        }


class ProxyManager:
    """
    代理管理器
    
    負責從 proxy_management 系統獲取有效的代理 IP，
    並管理代理的生命週期。
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化代理管理器
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.proxies: List[ProxyConfig] = []
        self.current_proxy_index = 0
        self.proxy_management_path = Path("proxy_management")
        self.working_proxies_file = self.proxy_management_path / "proxies" / "working_proxies.csv"
        self.comprehensive_data_path = self.proxy_management_path / "data" / "comprehensive"
        
    async def initialize(self) -> None:
        """初始化代理管理器"""
        self.logger.info("初始化代理管理器...")
        await self.load_proxies()
        
    async def load_proxies(self) -> None:
        """從 proxy_management 系統加載代理"""
        try:
            # 方法 1: 從 working_proxies.csv 加載
            if self.working_proxies_file.exists():
                await self._load_from_csv()
            
            # 方法 2: 從 comprehensive 數據加載
            if self.comprehensive_data_path.exists():
                await self._load_from_comprehensive_data()
            
            # 方法 3: 運行 proxy_management 系統獲取新代理
            if not self.proxies:
                await self._run_proxy_management_system()
            
            self.logger.info(f"成功加載 {len(self.proxies)} 個代理")
            
        except Exception as e:
            self.logger.error(f"加載代理失敗: {e}")
            # 如果所有方法都失敗，使用預設代理池
            self._use_default_proxies()
    
    async def _load_from_csv(self) -> None:
        """從 CSV 文件加載代理"""
        try:
            import csv
            
            with open(self.working_proxies_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('status') == 'active':
                        proxy = ProxyConfig(
                            host=row.get('host', ''),
                            port=int(row.get('port', 0)),
                            username=row.get('username'),
                            password=row.get('password'),
                            protocol=row.get('protocol', 'http')
                        )
                        if proxy.host and proxy.port:
                            self.proxies.append(proxy)
                            
        except Exception as e:
            self.logger.warning(f"從 CSV 加載代理失敗: {e}")
    
    async def _load_from_comprehensive_data(self) -> None:
        """從 comprehensive 數據加載代理"""
        try:
            json_files = list(self.comprehensive_data_path.glob("*.json"))
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    if isinstance(data, list):
                        for item in data:
                            if self._is_valid_proxy_data(item):
                                proxy = ProxyConfig(
                                    host=item.get('host', ''),
                                    port=int(item.get('port', 0)),
                                    username=item.get('username'),
                                    password=item.get('password'),
                                    protocol=item.get('protocol', 'http')
                                )
                                if proxy.host and proxy.port:
                                    self.proxies.append(proxy)
                                    
                except Exception as e:
                    self.logger.warning(f"加載文件 {json_file} 失敗: {e}")
                    continue
                    
        except Exception as e:
            self.logger.warning(f"從 comprehensive 數據加載代理失敗: {e}")
    
    def _is_valid_proxy_data(self, data: Dict[str, Any]) -> bool:
        """檢查代理數據是否有效"""
        required_fields = ['host', 'port']
        return all(field in data and data[field] for field in required_fields)
    
    async def _run_proxy_management_system(self) -> None:
        """運行 proxy_management 系統獲取代理"""
        try:
            # 檢查必要的 Python 文件是否存在
            proxy_manager_script = self.proxy_management_path / "core" / "proxy_manager.py"
            comprehensive_manager = self.proxy_management_path / "core" / "comprehensive_proxy_manager.py"
            
            if comprehensive_manager.exists():
                await self._run_comprehensive_proxy_system()
            elif proxy_manager_script.exists():
                await self._run_basic_proxy_system()
            else:
                self.logger.warning("未找到 proxy_management 系統腳本")
                
        except Exception as e:
            self.logger.error(f"運行 proxy_management 系統失敗: {e}")
    
    async def _run_comprehensive_proxy_system(self) -> None:
        """運行綜合代理系統"""
        try:
            # 導入並運行綜合代理管理器
            import sys
            sys.path.append(str(self.proxy_management_path))
            
            from core.comprehensive_proxy_manager import ComprehensiveProxyManager
            
            manager = ComprehensiveProxyManager()
            await manager.initialize()
            
            # 獲取工作代理
            working_proxies = await manager.get_working_proxies(limit=50)
            
            for proxy_data in working_proxies:
                proxy = ProxyConfig(
                    host=proxy_data.get('host', ''),
                    port=int(proxy_data.get('port', 0)),
                    username=proxy_data.get('username'),
                    password=proxy_data.get('password'),
                    protocol=proxy_data.get('protocol', 'http')
                )
                if proxy.host and proxy.port:
                    self.proxies.append(proxy)
                    
        except Exception as e:
            self.logger.error(f"運行綜合代理系統失敗: {e}")
    
    async def _run_basic_proxy_system(self) -> None:
        """運行基礎代理系統"""
        try:
            # 運行基本的代理管理器
            import subprocess
            import sys
            
            # 運行代理驗證腳本
            result = subprocess.run([
                sys.executable, str(self.proxy_management_path / "test_comprehensive_system.py")
            ], capture_output=True, text=True, timeout=300)  # 5分鐘超時
            
            if result.returncode == 0:
                # 重新加載代理
                await self.load_proxies()
            else:
                self.logger.error(f"代理系統運行失敗: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"運行基礎代理系統失敗: {e}")
    
    def _use_default_proxies(self) -> None:
        """使用預設代理池"""
        self.logger.warning("使用預設代理池")
        
        default_proxies = [
            {"host": "127.0.0.1", "port": 8080, "protocol": "http"},
            {"host": "127.0.0.1", "port": 3128, "protocol": "http"},
        ]
        
        for proxy_data in default_proxies:
            proxy = ProxyConfig(
                host=proxy_data["host"],
                port=proxy_data["port"],
                protocol=proxy_data["protocol"]
            )
            self.proxies.append(proxy)
    
    def get_proxy(self) -> Optional[ProxyConfig]:
        """
        獲取下一個代理
        
        Returns:
            Optional[ProxyConfig]: 代理配置，如果沒有可用的代理返回 None
        """
        if not self.proxies:
            self.logger.warning("沒有可用的代理")
            return None
        
        # 循環使用代理
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        
        self.logger.debug(f"使用代理: {proxy.host}:{proxy.port}")
        return proxy
    
    def get_random_proxy(self) -> Optional[ProxyConfig]:
        """
        隨機獲取代理
        
        Returns:
            Optional[ProxyConfig]: 代理配置，如果沒有可用的代理返回 None
        """
        if not self.proxies:
            self.logger.warning("沒有可用的代理")
            return None
        
        proxy = random.choice(self.proxies)
        self.logger.debug(f"隨機選擇代理: {proxy.host}:{proxy.port}")
        return proxy
    
    def remove_proxy(self, proxy: ProxyConfig) -> None:
        """
        移除失效的代理
        
        Args:
            proxy: 要移除的代理
        """
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            self.logger.info(f"移除失效代理: {proxy.host}:{proxy.port}")
            
            # 調整索引
            if self.current_proxy_index >= len(self.proxies):
                self.current_proxy_index = 0
    
    def get_proxy_count(self) -> int:
        """獲取可用代理數量"""
        return len(self.proxies)
    
    async def refresh_proxies(self) -> None:
        """刷新代理池"""
        self.logger.info("刷新代理池...")
        self.proxies.clear()
        self.current_proxy_index = 0
        await self.load_proxies()
    
    def get_proxy_for_playwright(self, proxy: Optional[ProxyConfig] = None) -> Dict[str, str]:
        """
        獲取 Playwright 使用的代理配置
        
        Args:
            proxy: 代理配置，如果為 None 則獲取下一個代理
            
        Returns:
            Dict[str, str]: Playwright 代理配置
        """
        if proxy is None:
            proxy = self.get_proxy()
        
        if proxy is None:
            return {}
        
        proxy_config = {
            "server": f"{proxy.protocol}://{proxy.host}:{proxy.port}"
        }
        
        if proxy.username and proxy.password:
            proxy_config["username"] = proxy.username
            proxy_config["password"] = proxy.password
        
        return proxy_config
    
    def format_proxy_url(self, proxy: ProxyConfig) -> str:
        """
        格式化代理 URL
        
        Args:
            proxy: 代理配置
            
        Returns:
            str: 格式化後的代理 URL
        """
        return proxy.url
    
    async def validate_proxy(self, proxy: ProxyConfig, test_url: str = "https://httpbin.org/ip") -> bool:
        """
        驗證代理是否有效
        
        Args:
            proxy: 代理配置
            test_url: 測試 URL
            
        Returns:
            bool: 代理是否有效
        """
        try:
            import aiohttp
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                proxy_url = self.format_proxy_url(proxy)
                
                async with session.get(test_url, proxy=proxy_url) as response:
                    if response.status == 200:
                        self.logger.info(f"代理 {proxy.host}:{proxy.port} 驗證成功")
                        return True
                    else:
                        self.logger.warning(f"代理 {proxy.host}:{proxy.port} 驗證失敗，狀態碼: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"代理 {proxy.host}:{proxy.port} 驗證失敗: {e}")
            return False
    
    async def validate_all_proxies(self, test_url: str = "https://httpbin.org/ip") -> None:
        """
        驗證所有代理
        
        Args:
            test_url: 測試 URL
        """
        self.logger.info("開始驗證所有代理...")
        
        valid_proxies = []
        
        for proxy in self.proxies:
            if await self.validate_proxy(proxy, test_url):
                valid_proxies.append(proxy)
            else:
                self.logger.warning(f"代理 {proxy.host}:{proxy.port} 無效，將被移除")
        
        self.proxies = valid_proxies
        self.current_proxy_index = 0
        
        self.logger.info(f"代理驗證完成，有效代理數量: {len(self.proxies)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取代理統計資訊"""
        return {
            "total_proxies": len(self.proxies),
            "current_index": self.current_proxy_index,
            "proxy_protocols": list(set(proxy.protocol for proxy in self.proxies)),
            "proxy_hosts": list(set(proxy.host for proxy in self.proxies))
        }