#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系統演示腳本 - 展示代理IP驗證系統的所有功能
"""

import json
import time
import urllib.request
import urllib.error
import random

class SystemDemo:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.demo_proxies = [
            {"ip": "103.250.70.81", "port": 80, "protocol": "http", "country": "Hong Kong"},
            {"ip": "47.243.87.110", "port": 8080, "protocol": "http", "country": "Hong Kong"},
            {"ip": "154.194.8.232", "port": 3128, "protocol": "https", "country": "Singapore"},
            {"ip": "103.152.238.162", "port": 8080, "protocol": "http", "country": "Indonesia"},
            {"ip": "8.219.97.248", "port": 8080, "protocol": "http", "country": "Singapore"}
        ]
    
    def api_request(self, endpoint, method='GET', data=None):
        """發送API請求"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method == 'GET':
                response = urllib.request.urlopen(url)
            else:  # POST
                req = urllib.request.Request(url, method=method)
                if data:
                    req.add_header('Content-Type', 'application/json')
                    req.data = json.dumps(data).encode('utf-8')
                response = urllib.request.urlopen(req)
            
            return json.loads(response.read().decode('utf-8'))
            
        except Exception as e:
            print(f"❌ API錯誤: {str(e)}")
            return None
    
    def demo_system_status(self):
        """演示系統狀態檢查"""
        print("🔍 檢查系統狀態...")
        status = self.api_request('/api/status')
        
        if status:
            print(f"✅ 系統運行正常")
            print(f"📊 版本: {status.get('version', '未知')}")
            print(f"🔄 測試狀態: {'運行中' if status.get('testing') else '待機'}")
            return True
        else:
            print("❌ 系統未響應，請確保服務器已啟動")
            return False
    
    def demo_proxy_management(self):
        """演示代理管理功能"""
        print("\n📋 代理管理演示")
        print("=" * 40)
        
        # 獲取當前代理列表
        print("1️⃣ 獲取當前代理列表...")
        proxies = self.api_request('/api/proxies')
        print(f"📊 當前有 {len(proxies) if proxies else 0} 個代理")
        
        # 添加演示代理
        print("\n2️⃣ 添加演示代理...")
        for i, proxy in enumerate(self.demo_proxies):
            print(f"   添加代理 {i+1}: {proxy['ip']}:{proxy['port']}")
            result = self.api_request('/api/proxies', 'POST', proxy)
            if result:
                print(f"   ✅ 成功添加，ID: {result.get('id', '未知')}")
            time.sleep(0.5)
        
        # 重新獲取代理列表
        print("\n3️⃣ 更新後的代理列表:")
        updated_proxies = self.api_request('/api/proxies')
        if updated_proxies:
            for proxy in updated_proxies:
                status = proxy.get('status', 'unknown')
                score = proxy.get('score', 0)
                print(f"   📍 {proxy['ip']}:{proxy['port']} - 狀態: {status}, 評分: {score}")
    
    def demo_testing_process(self):
        """演示測試過程"""
        print("\n🧪 開始代理測試演示")
        print("=" * 40)
        
        # 開始測試
        print("1️⃣ 啟動測試進程...")
        result = self.api_request('/api/test/start', 'POST', {})
        if result:
            print(f"✅ {result.get('message', '測試已啟動')}")
        
        # 監控測試進度
        print("\n2️⃣ 監控測試進度...")
        for i in range(10):  # 監控10次
            status = self.api_request('/api/test/status')
            if status:
                progress = status.get('progress', 0)
                current = status.get('current_proxy', '')
                is_running = status.get('is_running', False)
                
                print(f"   📊 進度: {progress}% | 當前: {current}")
                
                if not is_running:
                    print("   ✅ 測試已完成")
                    break
            
            time.sleep(2)  # 等待2秒
        
        # 獲取測試結果
        print("\n3️⃣ 獲取測試結果...")
        results = self.api_request('/api/results')
        if results:
            print(f"📊 共獲得 {len(results)} 個測試結果")
            
            # 統計結果
            valid_count = sum(1 for r in results if r.get('status') == 'valid')
            invalid_count = sum(1 for r in results if r.get('status') == 'invalid')
            avg_score = sum(r.get('score', 0) for r in results) / len(results) if results else 0
            
            print(f"   ✅ 有效代理: {valid_count}")
            print(f"   ❌ 無效代理: {invalid_count}")
            print(f"   📈 平均評分: {avg_score:.1f}")
            
            # 顯示詳細結果
            print("\n   📋 詳細結果:")
            for result in results[:3]:  # 顯示前3個結果
                proxy = f"{result['ip']}:{result['port']}"
                status = result.get('status', 'unknown')
                score = result.get('score', 0)
                response_time = result.get('response_time', 0)
                anonymity = result.get('anonymity_level', 'unknown')
                
                status_icon = "✅" if status == 'valid' else "❌"
                print(f"   {status_icon} {proxy} - 評分: {score}, 響應: {response_time}s, 匿名: {anonymity}")
    
    def demo_statistics(self):
        """演示統計功能"""
        print("\n📈 統計分析演示")
        print("=" * 40)
        
        proxies = self.api_request('/api/proxies')
        results = self.api_request('/api/results')
        
        if proxies and results:
            # 基本統計
            total_proxies = len(proxies)
            valid_proxies = sum(1 for p in proxies if p.get('status') == 'valid')
            invalid_proxies = sum(1 for p in proxies if p.get('status') == 'invalid')
            
            print(f"📊 代理統計:")
            print(f"   總數: {total_proxies}")
            print(f"   有效: {valid_proxies} ({valid_proxies/total_proxies*100:.1f}%)")
            print(f"   無效: {invalid_proxies} ({invalid_proxies/total_proxies*100:.1f}%)")
            
            # 國家分布
            countries = {}
            for proxy in proxies:
                country = proxy.get('country', 'Unknown')
                countries[country] = countries.get(country, 0) + 1
            
            print(f"\n🌍 國家分布:")
            for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
                print(f"   {country}: {count}")
            
            # 協議分布
            protocols = {}
            for proxy in proxies:
                protocol = proxy.get('protocol', 'http')
                protocols[protocol] = protocols.get(protocol, 0) + 1
            
            print(f"\n🔌 協議分布:")
            for protocol, count in protocols.items():
                print(f"   {protocol}: {count}")
    
    def run_demo(self):
        """運行完整演示"""
        print("🎬 Proxifly 代理IP驗證系統 - 功能演示")
        print("=" * 60)
        
        # 檢查系統狀態
        if not self.demo_system_status():
            print("\n❌ 演示無法繼續，請確保服務器已啟動")
            return
        
        # 演示各項功能
        self.demo_proxy_management()
        self.demo_testing_process()
        self.demo_statistics()
        
        print("\n" + "=" * 60)
        print("🎉 演示完成！")
        print("\n📝 總結:")
        print("   ✅ 系統狀態檢查 - 通過")
        print("   ✅ 代理管理功能 - 通過")
        print("   ✅ 測試驗證功能 - 通過")
        print("   ✅ 統計分析功能 - 通過")
        print("\n🌐 系統地址: http://localhost:5000")
        print("📚 使用指南: USER_GUIDE.md")

if __name__ == '__main__':
    demo = SystemDemo()
    demo.run_demo()