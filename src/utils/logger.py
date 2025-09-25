#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日誌管理系統

提供統一的日誌記錄功能，支持文件和控制台輸出，支持日誌輪轉。
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from src.config.config import config_manager

class LoggerManager:
    """日誌管理器"""
    
    def __init__(self):
        """初始化日誌管理器"""
        self.log_dir = Path("data/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.loggers = {}
        self.logging_config = config_manager.logging_config
        
    def get_logger(self, name: str) -> logging.Logger:
        """獲取指定名稱的日誌器"""
        if name in self.loggers:
            return self.loggers[name]
            
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, self.logging_config.level.upper()))
        
        # 避免重複添加處理器
        if logger.handlers:
            self.loggers[name] = logger
            return logger
        
        # 創建格式化器
        formatter = logging.Formatter(self.logging_config.format)
        
        # 控制台處理器
        if self.logging_config.console_enabled:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # 文件處理器
        if self.logging_config.file_enabled:
            log_file = self.log_dir / f"{name}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.logging_config.max_file_size,
                backupCount=self.logging_config.backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        self.loggers[name] = logger
        return logger
        
    def get_crawler_logger(self) -> logging.Logger:
        """獲取爬蟲日誌器"""
        return self.get_logger("crawler")
        
    def get_parser_logger(self) -> logging.Logger:
        """獲取解析器日誌器"""
        return self.get_logger("parser")
        
    def get_proxy_logger(self) -> logging.Logger:
        """獲取代理日誌器"""
        return self.get_logger("proxy")
        
    def get_database_logger(self) -> logging.Logger:
        """獲取數據庫日誌器"""
        return self.get_logger("database")
        
    def get_api_logger(self) -> logging.Logger:
        """獲取API日誌器"""
        return self.get_logger("api")
        
    def log_system_info(self):
        """記錄系統信息"""
        system_logger = self.get_logger("system")
        system_logger.info("=" * 60)
        system_logger.info(f"SEEK Job Crawler 系統啟動")
        system_logger.info(f"版本: {config_manager.app_config.version}")
        system_logger.info(f"環境: {config_manager.app_config.environment}")
        system_logger.info(f"調試模式: {config_manager.app_config.debug}")
        system_logger.info(f"啟動時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        system_logger.info("=" * 60)
        
    def log_error_summary(self, errors: list):
        """記錄錯誤摘要"""
        error_logger = self.get_logger("error_summary")
        if errors:
            error_logger.error(f"發現 {len(errors)} 個錯誤:")
            for error in errors:
                error_logger.error(f"  - {error}")
        else:
            error_logger.info("未發現錯誤")
            
    def cleanup_old_logs(self, days: int = 30):
        """清理舊日誌文件"""
        cleanup_logger = self.get_logger("cleanup")
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        cleaned_count = 0
        for log_file in self.log_dir.glob("*.log*"):
            try:
                if log_file.stat().st_mtime < cutoff_date:
                    log_file.unlink()
                    cleaned_count += 1
                    cleanup_logger.info(f"刪除舊日誌文件: {log_file.name}")
            except Exception as e:
                cleanup_logger.error(f"刪除日誌文件失敗 {log_file.name}: {e}")
                
        cleanup_logger.info(f"清理完成，共刪除 {cleaned_count} 個文件")

# 全局日誌管理器實例
logger_manager = LoggerManager()

def get_logger(name: str) -> logging.Logger:
    """獲取日誌器的快捷函數"""
    return logger_manager.get_logger(name)

def setup_logging():
    """設置日誌系統"""
    logger_manager.log_system_info()
    
if __name__ == "__main__":
    # 測試日誌系統
    setup_logging()
    
    logger = get_logger("test")
    logger.debug("這是一條調試信息")
    logger.info("這是一條信息")
    logger.warning("這是一條警告信息")
    logger.error("這是一條錯誤信息")
    logger.critical("這是一條嚴重錯誤信息")
    
    print("日誌測試完成，請查看 data/logs/test.log 文件")