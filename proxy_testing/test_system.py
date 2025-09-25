# 快速測試腳本
# 用於驗證代理IP驗證系統的基本功能

import json
import requests
import time

def test_system():
    """測試代理IP驗證系統的基本功能"""
    
    base_url = "http://localhost:5000"
    
    print("🚀 開始測試代理IP驗證系統...")
    
    # 1. 測試系統狀態
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            print("✅ 系統狀態正常")
        else:
            print(f"❌ 系統狀態異常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 無法連接到系統: {e}")
        return False
    
    # 2. 測試代理列表
    try:
        response = requests.get(f"{base_url}/api/proxies")
        if response.status_code == 200:
            proxies = response.json()
            print(f"✅ 代理列表正常，當前有 {len(proxies)} 個代理")
        else:
            print(f"❌ 代理列表獲取失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 代理列表測試失敗: {e}")
        return False
    
    # 3. 測試添加代理
    test_proxy = {
        "ip": "8.8.8.8",
        "port": 8080,
        "protocol": "http",
        "username": "",
        "password": ""
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/proxies",
            json=test_proxy,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code in [200, 201]:
            print("✅ 代理添加成功")
        else:
            print(f"⚠️ 代理添加可能失敗: {response.status_code}")
    except Exception as e:
        print(f"⚠️ 代理添加測試失敗: {e}")
    
    # 4. 測試驗證功能
    print("🧪 開始測試代理驗證功能...")
    try:
        response = requests.post(f"{base_url}/api/test/start")
        if response.status_code == 200:
            print("✅ 驗證測試已啟動")
            
            # 等待幾秒讓測試運行
            time.sleep(3)
            
            # 檢查測試狀態
            response = requests.get(f"{base_url}/api/test/status")
            if response.status_code == 200:
                status = response.json()
                print(f"✅ 測試狀態: {status.get('status', 'unknown')}")
            else:
                print(f"⚠️ 無法獲取測試狀態: {response.status_code}")
                
        else:
            print(f"❌ 驗證測試啟動失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 驗證測試失敗: {e}")
        return False
    
    print("\n🎉 系統測試完成！")
    print(f"🌐 請訪問: {base_url} 查看完整界面")
    return True

if __name__ == "__main__":
    test_system()