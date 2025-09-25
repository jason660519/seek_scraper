#!/usr/bin/env python3
"""
測試 proxy management 系統
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.proxy_manager import ProxyManager
from core.proxy_validator import ProxyValidator
import pandas as pd

def test_proxy_manager():
    """測試 ProxyManager"""
    print('=== 測試 ProxyManager ===')
    manager = ProxyManager()
    try:
        manager.load_validation_results('proxies/working_proxies.csv')
        working_proxies = manager.get_working_proxies(limit=5)
        print(f'成功載入 {len(working_proxies)} 個有效代理')
        for i, proxy in enumerate(working_proxies[:3]):
            print(f'{i+1}. {proxy["ip"]}:{proxy["port"]} ({proxy["type"]}) - {proxy["response_time_ms"]}ms')
        return True
    except Exception as e:
        print(f'ProxyManager 錯誤: {e}')
        return False

def test_proxy_validator():
    """測試 ProxyValidator"""
    print('\n=== 測試 ProxyValidator ===')
    validator = ProxyValidator()
    try:
        # 測試從CSV載入
        proxies = validator.load_proxies_from_csv('proxies/working_proxies.csv')
        print(f'從CSV載入 {len(proxies)} 個代理')
        
        # 測試從TXT載入
        txt_proxies = validator.load_proxies_from_txt('data/http.txt')
        print(f'從TXT載入 {len(txt_proxies)} 個HTTP代理')
        
        return True
    except Exception as e:
        print(f'ProxyValidator 錯誤: {e}')
        return False

def test_data_files():
    """測試資料檔案是否存在"""
    print('\n=== 測試資料檔案 ===')
    test_files = [
        'proxies/working_proxies.csv',
        'data/http.txt',
        'data/all.txt',
        'core/proxy_manager.py',
        'core/proxy_validator.py'
    ]
    
    for file_path in test_files:
        exists = os.path.exists(file_path)
        status = "✅ 存在" if exists else "❌ 不存在"
        print(f'{file_path}: {status}')

if __name__ == "__main__":
    print("開始測試 Proxy Management 系統...")
    
    # 測試資料檔案
    test_data_files()
    
    # 測試 ProxyManager
    manager_success = test_proxy_manager()
    
    # 測試 ProxyValidator
    validator_success = test_proxy_validator()
    
    print(f'\n=== 測試結果 ===')
    print(f'ProxyManager: {"✅ 正常" if manager_success else "❌ 異常"}')
    print(f'ProxyValidator: {"✅ 正常" if validator_success else "❌ 異常"}')
    
    if manager_success and validator_success:
        print('\n🎉 Proxy Management 系統運作正常！')
    else:
        print('\n⚠️  部分功能異常，需要檢查')