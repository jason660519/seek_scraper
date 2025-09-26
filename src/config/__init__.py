"""
配置管理模組

提供統一的配置載入和管理功能，支援環境變數、檔案配置等。
"""

import os
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class DatabaseConfig:
    """資料庫配置"""
    host: str = "localhost"
    port: int = 5432
    database: str = "seek_jobs"
    username: str = "postgres"
    password: str = ""
    ssl_mode: str = "prefer"
    
    @property
    def connection_string(self) -> str:
        """生成 PostgreSQL 連接字串"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?sslmode={self.ssl_mode}"


@dataclass
class ScraperConfig:
    """爬蟲配置"""
    base_url: str = "https://www.seek.com.au"
    request_delay: float = 1.0  # 請求間隔（秒）
    max_retries: int = 3
    timeout: int = 30
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    max_pages: int = 10  # 最多爬取頁數
    proxy_enabled: bool = False
    proxy_list: list = None
    
    def __post_init__(self):
        if self.proxy_list is None:
            self.proxy_list = []


@dataclass
class LoggingConfig:
    """日誌配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/seek_crawler.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class AppConfig:
    """應用程式總配置"""
    database: DatabaseConfig
    scraper: ScraperConfig
    logging: LoggingConfig
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'AppConfig':
        """從字典載入配置"""
        return cls(
            database=DatabaseConfig(**config_dict.get('database', {})),
            scraper=ScraperConfig(**config_dict.get('scraper', {})),
            logging=LoggingConfig(**config_dict.get('logging', {}))
        )


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """
    載入應用程式配置
    
    優先順序：
    1. 指定的 config_path
    2. 環境變數 SEEK_CONFIG_FILE
    3. 預設路徑 config/app_config.json
    
    Args:
        config_path: 配置文件路徑
        
    Returns:
        AppConfig: 應用程式配置物件
    """
    # 確定配置文件路徑
    if config_path is None:
        config_path = os.getenv('SEEK_CONFIG_FILE', 'config/app_config.json')
    
    config_file = Path(config_path)
    
    # 如果配置文件存在，載入它
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            return AppConfig.from_dict(config_dict)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"警告：無法載入配置文件 {config_path}: {e}")
    
    # 如果配置文件不存在，使用預設配置
    print(f"使用預設配置（配置文件不存在：{config_path}）")
    return AppConfig(
        database=DatabaseConfig(),
        scraper=ScraperConfig(),
        logging=LoggingConfig()
    )


def save_config(config: AppConfig, config_path: str = "config/app_config.json"):
    """儲存配置到文件"""
    config_dict = {
        'database': {
            'host': config.database.host,
            'port': config.database.port,
            'database': config.database.database,
            'username': config.database.username,
            'password': config.database.password,
            'ssl_mode': config.database.ssl_mode
        },
        'scraper': {
            'base_url': config.scraper.base_url,
            'request_delay': config.scraper.request_delay,
            'max_retries': config.scraper.max_retries,
            'timeout': config.scraper.timeout,
            'user_agent': config.scraper.user_agent,
            'max_pages': config.scraper.max_pages,
            'proxy_enabled': config.scraper.proxy_enabled,
            'proxy_list': config.scraper.proxy_list
        },
        'logging': {
            'level': config.logging.level,
            'format': config.logging.format,
            'file_path': config.logging.file_path,
            'max_file_size': config.logging.max_file_size,
            'backup_count': config.logging.backup_count
        }
    }
    
    # 確保目錄存在
    Path(config_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    print(f"配置已儲存到 {config_path}")