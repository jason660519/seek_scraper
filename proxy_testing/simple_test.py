#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單測試腳本 - 測試代理IP驗證系統
"""

import urllib.request
import urllib.error
import json

def test_api(endpoint, method='GET', data=None):
    """測試API端點"""
    try:
        url = f"http://localhost:5000{endpoint}"
        
        if method == 'GET':
            response = urllib.request.urlopen(url)
        else:  # POST
            req = urllib.request.Request(url, method=method)
            if data:
                req.add_header('Content-Type', 'application/json')
                req.data = json.dumps(data).encode('utf-8')
            response = urllib.request.urlopen(req)
        
        result = json.loads(response.read().decode('utf-8'))
        print(f"✅ {method} {endpoint} - 成功")
        print(f"響應: {result}")
        return result
        
    except urllib.error.HTTPError as e:
        print(f"❌ {method} {endpoint} - HTTP錯誤: {e.code}")
        return None
    except Exception as e:
        print(f"❌ {method} {endpoint} - 錯誤: {str(e)}")
        return None

def main():
    """主測試函數"""
    print("🧪 開始測試代理IP驗證系統...")
    print("=" * 50)
    
    # 測試系統狀態
    status = test_api('/api/status')
    
    # 測試代理列表
    proxies = test_api('/api/proxies')
    
    # 測試添加代理
    new_proxy = {
        "ip": "192.168.1.100",
        "port": 8080,
        "protocol": "http",
        "country": "China"
    }
    add_result = test_api('/api/proxies', 'POST', new_proxy)
    
    # 重新獲取代理列表
    updated_proxies = test_api('/api/proxies')
    
    # 測試開始測試
    test_start = test_api('/api/test/start', 'POST', {})
    
    print("\n" + "=" * 50)
    print("🎉 測試完成！")
    
    if status and proxies:
        print("✅ 系統運行正常")
        print(f"📊 當前代理數量: {len(proxies) if proxies else 0}")
    else:
        print("❌ 系統可能存在問題")

if __name__ == '__main__':
    main()