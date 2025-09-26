"""
日誌工具模組

提供統一的日誌記錄功能，支援不同的日誌等級和格式。
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    獲取配置好的日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        level: 日誌等級 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日誌檔案路徑，如果為 None 則只輸出到控制台
        format_string: 自訂日誌格式
        
    Returns:
        logging.Logger: 配置好的日誌記錄器
    """
    # 創建日誌記錄器
    logger = logging.getLogger(name)
    
    # 如果已經有處理器，直接返回
    if logger.handlers:
        return logger
    
    # 設置日誌等級
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # 預設格式
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(format_string)
    
    # 控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 檔案處理器（如果指定了檔案路徑）
    if log_file:
        # 確保日誌目錄存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def setup_global_logging(
    level: str = "INFO",
    log_dir: Optional[str] = None,
    enable_file_logging: bool = True
) -> None:
    """
    設置全局日誌配置
    
    Args:
        level: 全局日誌等級
        log_dir: 日誌檔案目錄
        enable_file_logging: 是否啟用檔案日誌
    """
    # 設置根日誌記錄器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # 清理現有的處理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 檔案處理器
    if enable_file_logging and log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # 按日期創建日誌檔案
        log_file = log_path / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


class LoggerMixin:
    """
    日誌混合類，為類別提供日誌功能
    """
    
    @property
    def logger(self) -> logging.Logger:
        """獲取日誌記錄器"""
        return get_logger(self.__class__.__name__)