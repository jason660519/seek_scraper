#!/usr/bin/env python3
"""
簡化版代理測試腳本
專門用於驗證GitHub Actions配置和代理更新功能
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

def test_proxy_update():
    """測試代理更新功能"""
    print("🚀 開始代理更新測試...")
    
    try:
        # 導入代理管理器
        sys.path.append('proxy_management')
        from core.comprehensive_proxy_manager import ComprehensiveProxyManager, ProxyStatus
        
        # 創建管理器實例
        manager = ComprehensiveProxyManager()
        print("✅ 代理管理器初始化成功")
        
        # 測試獲取代理
        print("\n📡 獲取代理...")
        proxies = manager.fetch_proxies_from_multiple_sources()
        print(f"✅ 成功獲取 {len(proxies)} 個代理")
        
        # 顯示代理分布
        protocol_counts = {}
        for proxy in proxies:
            protocol = proxy.protocol
            protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1
        
        print("📊 代理分布：")
        for protocol, count in protocol_counts.items():
            print(f"   - {protocol.upper()}: {count} 個")
        
        # 測試保存代理
        print("\n💾 保存代理...")
        manager._save_proxies(proxies)
        print("✅ 代理保存成功")
        
        # 測試統計
        print("\n📈 生成統計...")
        stats = manager.get_proxy_statistics()
        print(f"✅ 統計完成：")
        print(f"   - 總代理數: {stats['total_proxies']}")
        print(f"   - 有效代理: {stats['valid_count']}")
        print(f"   - 暫時無效: {stats['temp_invalid_count']}")
        print(f"   - 永久無效: {stats['invalid_count']}")
        print(f"   - 未測試: {stats['untested_count']}")
        
        # 測試導出
        print("\n📤 導出代理...")
        export_path = manager.export_proxies('json', ProxyStatus.UNTESTED)
        if export_path:
            print(f"✅ 導出成功：{export_path}")
        else:
            print("❌ 導出失敗")
        
        # 檢查文件更新時間
        print("\n⏰ 檢查文件更新時間...")
        data_dir = Path("proxy_management/data/comprehensive")
        if data_dir.exists():
            for file_path in data_dir.glob("*.json"):
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                print(f"   - {file_path.name}: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗：{e}")
        import traceback
        traceback.print_exc()
        return False

def check_github_action_config():
    """檢查GitHub Actions配置"""
    print("\n🔧 檢查GitHub Actions配置...")
    
    workflow_file = Path(".github/workflows/proxy-scheduler.yml")
    if not workflow_file.exists():
        print("❌ 工作流文件不存在")
        return False
    
    with open(workflow_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查cron表達式
    if "*/30 * * * *" in content:
        print("✅ ✅ Cron表達式已設置為每30分鐘執行")
        return True
    else:
        print("❌ Cron表達式未正確設置")
        return False

def main():
    """主函數"""
    print("=" * 50)
    print("🚀 代理更新功能測試")
    print("=" * 50)
    print(f"測試時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 檢查配置
    config_ok = check_github_action_config()
    
    # 測試代理功能
    proxy_ok = test_proxy_update()
    
    # 總結
    print("\n" + "=" * 50)
    print("📊 測試結果")
    print("=" * 50)
    print(f"GitHub配置：{'✅ 通過' if config_ok else '❌ 失敗'}")
    print(f"代理功能：{'✅ 通過' if proxy_ok else '❌ 失敗'}")
    
    if config_ok and proxy_ok:
        print("\n🎉 所有測試通過！")
        print("✅ GitHub Actions將每30分鐘自動更新代理數據")
        print("✅ 代理獲取和保存功能正常")
        return True
    else:
        print("\n⚠️  部分測試失敗，請檢查錯誤信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)