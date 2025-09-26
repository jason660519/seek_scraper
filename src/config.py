"""
Seek爬蟲配置文件

包含所有可配置的參數和設置
"""

import os
from pathlib import Path
from typing import Dict, Any, List

# 基礎配置
BASE_CONFIG = {
    # 數據存儲路徑
    'raw_data_dir': 'data/raw',
    'processed_data_dir': 'data/processed',
    'log_dir': 'logs',
    
    # 爬蟲設置
    'headless': True,  # 是否使用無頭模式
    'max_pages': 5,  # 每個搜索組合的最大頁數
    'delay_between_requests': 2,  # 請求間延遲（秒）
    'timeout': 30,  # 頁面加載超時時間
    
    # 代理設置
    'use_proxy': False,  # 是否使用代理
    'proxy_pool_size': 10,  # 代理池大小
    'proxy_rotation_interval': 5,  # 代理輪換間隔（請求數）
    
    # 反爬蟲設置
    'user_agent_rotation': True,  # 是否輪換用戶代理
    'tls_fingerprinting': True,  # 是否使用TLS指紋
    'viewport_randomization': True,  # 是否隨機化視口大小
    
    # 搜索設置
    'default_keywords': [
        'software engineer',
        'data scientist', 
        'machine learning',
        'web developer',
        'devops engineer'
    ],
    'default_locations': [
        'Sydney NSW',
        'Melbourne VIC',
        'Brisbane QLD',
        'Perth WA',
        'Adelaide SA'
    ],
    
    # 日誌設置
    'log_level': 'INFO',
    'log_to_file': True,
    'log_to_console': True,
    'max_log_size_mb': 100,
    'log_backup_count': 5,
    
    # 輸出格式
    'output_formats': ['json', 'csv'],  # 支持的輸出格式
    
    # 重試設置
    'max_retries': 3,  # 最大重試次數
    'retry_delay': 5,  # 重試延遲（秒）
}

def get_config() -> Dict[str, Any]:
    """
    獲取配置
    
    Returns:
        Dict[str, Any]: 配置字典
    """
    config = BASE_CONFIG.copy()
    
    # 從環境變量覆蓋配置
    env_mappings = {
        'SEEK_HEADLESS': ('headless', lambda x: x.lower() == 'true'),
        'SEEK_MAX_PAGES': ('max_pages', int),
        'SEEK_USE_PROXY': ('use_proxy', lambda x: x.lower() == 'true'),
        'SEEK_LOG_LEVEL': ('log_level', str.upper),
        'SEEK_DELAY': ('delay_between_requests', int),
    }
    
    for env_var, (config_key, converter) in env_mappings.items():
        if env_var in os.environ:
            try:
                config[config_key] = converter(os.environ[env_var])
            except (ValueError, TypeError):
                pass  # 保持默認值
    
    return config

def create_directories(config: Dict[str, Any]) -> None:
    """
    創建必要的目錄
    
    Args:
        config: 配置字典
    """
    directories = [
        config['raw_data_dir'],
        config['processed_data_dir'],
        config['log_dir']
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    驗證配置
    
    Args:
        config: 配置字典
        
    Returns:
        List[str]: 錯誤列表
    """
    errors = []
    
    # 檢查數值範圍
    if config['max_pages'] < 1 or config['max_pages'] > 100:
        errors.append("max_pages 必須在 1-100 之間")
    
    if config['delay_between_requests'] < 0:
        errors.append("delay_between_requests 不能為負數")
    
    if config['timeout'] < 5 or config['timeout'] > 300:
        errors.append("timeout 必須在 5-300 秒之間")
    
    # 檢查輸出格式
    valid_formats = ['json', 'csv']
    for fmt in config['output_formats']:
        if fmt not in valid_formats:
            errors.append(f"不支持的輸出格式: {fmt}")
    
    return errors