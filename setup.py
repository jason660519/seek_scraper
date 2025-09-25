#!/usr/bin/env python3
"""
項目設置腳本 - 自動化環境配置和初始化
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional

def create_directories():
    """創建必要的目錄結構"""
    directories = [
        "data/raw",
        "data/processed", 
        "data/logs",
        "tests",
        "docker",
        "scripts",
        "docs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ 創建目錄: {directory}")

def setup_environment():
    """設置環境配置文件"""
    env_file = ".env"
    env_example = ".env.example"
    
    if not Path(env_file).exists() and Path(env_example).exists():
        shutil.copy(env_example, env_file)
        print("✓ 創建 .env 配置文件")
    elif Path(env_file).exists():
        print("✓ .env 文件已存在")
    else:
        print("⚠ .env.example 文件不存在，請手動創建 .env 文件")

def check_dependencies():
    """檢查必要的依賴項"""
    try:
        import aiohttp
        import pydantic
        import sqlalchemy
        print("✓ 核心依賴項檢查通過")
        return True
    except ImportError as e:
        print(f"✗ 缺少依賴項: {e}")
        print("請運行: uv pip install -e .")
        return False

def initialize_database():
    """初始化數據庫"""
    try:
        from src.services.data_service import DataService
        from src.config.config import ConfigManager
        
        config = ConfigManager()
        data_service = DataService(config)
        
        # 創建數據表
        data_service.initialize_database()
        print("✓ 數據庫初始化完成")
        return True
    except Exception as e:
        print(f"✗ 數據庫初始化失敗: {e}")
        return False

def main():
    """主設置函數"""
    print("開始設置 SEEK Job Crawler 項目...")
    print("=" * 50)
    
    # 創建目錄
    create_directories()
    
    # 設置環境
    setup_environment()
    
    # 檢查依賴
    if not check_dependencies():
        print("請先安裝依賴項")
        sys.exit(1)
    
    # 初始化數據庫
    initialize_database()
    
    print("\n" + "=" * 50)
    print("設置完成！請執行以下步驟：")
    print("1. 編輯 .env 文件，配置您的設置")
    print("2. 運行: python -m src.main_simple")
    print("3. 或使用: seek-crawler")

if __name__ == "__main__":
    main()