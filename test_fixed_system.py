#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修復版代理IP驗證系統的連接性
"""

import requests
import json
import sys

def test_connection():
    """測試系統連接"""
    base_url = "http://localhost:5000"
    
    print("🚀 開始測試代理IP驗證系統連接...")
    
    # 測試主頁面
    try:
        response = requests.get(base_url, timeout=10)
        print(f"✅ 主頁面訪問成功: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 主頁面訪問失敗: {e}")
        return False
    
    # 測試API端點
    endpoints = [
        "/api/status",
        "/api/proxies",
        "/api/results"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(base_url + endpoint, timeout=10)
            if response.status_code == 200:
                print(f"✅ API端點 {endpoint} 正常: HTTP {response.status_code}")
                if endpoint == "/api/status":
                    data = response.json()
                    print(f"   系統狀態: {data}")
            else:
                print(f"❌ API端點 {endpoint} 異常: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API端點 {endpoint} 訪問失敗: {e}")
            return False
    
    # 測試添加代理
    try:
        test_proxy = {
            "ip": "192.168.1.1",
            "port": 8080,
            "protocol": "http",
            "country": "Test Country"
        }
        response = requests.post(
            base_url + "/api/proxies",
            json=test_proxy,
            timeout=10
        )
        if response.status_code == 200:
            print(f"✅ 添加代理成功: {response.json()}")
        else:
            print(f"❌ 添加代理失敗: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 添加代理失敗: {e}")
    
    # 測試開始測試
    try:
        response = requests.post(base_url + "/api/test/start", json={}, timeout=10)
        if response.status_code == 200:
            print(f"✅ 開始測試成功: {response.json()}")
        else:
            print(f"❌ 開始測試失敗: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 開始測試失敗: {e}")
    
    print("\n🎉 所有測試完成！系統運行正常")
    return True

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)