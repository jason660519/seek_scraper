#!/usr/bin/env python3
"""
GitHub Actions 配置測試腳本
用於驗證代理定時任務是否能正常工作
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

def test_proxy_functionality():
    """測試代理功能是否正常"""
    print("🧪 開始測試代理功能...")
    
    try:
        # 導入代理管理器
        sys.path.append('proxy_management')
        from core.comprehensive_proxy_manager import ComprehensiveProxyManager
        
        # 創建管理器實例
        manager = ComprehensiveProxyManager()
        print("✅ 代理管理器初始化成功")
        
        # 測試獲取代理
        print("\n📡 測試代理獲取功能...")
        proxies = manager.fetch_proxies_from_multiple_sources()
        print(f"✅ 成功獲取 {len(proxies)} 個代理")
        
        # 測試驗證功能（只驗證前5個）
        print("\n🔍 測試代理驗證功能...")
        if proxies:
            test_proxies = proxies[:5]  # 只測試前5個
            validated = manager.validate_proxy_batch(test_proxies)
            valid_count = sum(1 for p in validated if p.status.value == 'valid')
            print(f"✅ 驗證完成：{valid_count}/{len(test_proxies)} 個代理有效")
        
        # 測試統計功能
        print("\n📊 測試統計功能...")
        stats = manager.get_proxy_statistics()
        print(f"✅ 統計數據獲取成功：")
        print(f"   - 總代理數: {stats['total_proxies']}")
        print(f"   - 有效代理: {stats['valid_count']}")
        print(f"   - 暫時無效: {stats['temp_invalid_count']}")
        print(f"   - 永久無效: {stats['invalid_count']}")
        
        # 測試導出功能
        print("\n💾 測試導出功能...")
        from core.comprehensive_proxy_manager import ProxyStatus
        export_result = manager.export_proxies('json', ProxyStatus.VALID)
        if export_result:
            print(f"✅ 導出成功：{export_result}")
        else:
            print("⚠️  導出功能可能有問題")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗：{e}")
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
        print("✅ Cron表達式已設置為每30分鐘執行")
    else:
        print("❌ Cron表達式未正確設置")
        return False
    
    # 檢查必要的環境變量
    required_env_vars = [
        "MAX_PROXIES_TO_FETCH",
        "VALIDATION_TIMEOUT", 
        "MAX_WORKERS",
        "RETRY_INVALID_PROXIES",
        "CLEANUP_OLDER_THAN_DAYS"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if f"${{{{ secrets.{var} }}}}" not in content and f"{var} ||" not in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  缺少環境變量：{missing_vars}")
    else:
        print("✅ 環境變量配置完整")
    
    return True

def simulate_github_action_run():
    """模擬GitHub Action運行"""
    print("\n🎯 模擬GitHub Action運行環境...")
    
    # 設置環境變量
    os.environ.update({
        'MAX_PROXIES_TO_FETCH': '500',
        'VALIDATION_TIMEOUT': '10',
        'MAX_WORKERS': '30',
        'RETRY_INVALID_PROXIES': 'true',
        'CLEANUP_OLDER_THAN_DAYS': '7'
    })
    
    try:
        # 運行雲端調度器
        print("🚀 運行雲端調度器...")
        result = subprocess.run([
            sys.executable, 'proxy_management/cloud_scheduler.py'
        ], capture_output=True, text=True, timeout=300)
        
        print("📋 執行輸出：")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  錯誤輸出：")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ 雲端調度器執行成功")
            return True
        else:
            print(f"❌ 雲端調度器執行失敗，返回碼：{result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ 執行超時（5分鐘）")
        return False
    except Exception as e:
        print(f"❌ 執行錯誤：{e}")
        return False

def generate_test_report():
    """生成測試報告"""
    print("\n📄 生成測試報告...")
    
    report = {
        "test_time": datetime.now().isoformat(),
        "github_action_config": check_github_action_config(),
        "proxy_functionality": test_proxy_functionality(),
        "simulation_result": simulate_github_action_run(),
        "recommendations": []
    }
    
    # 檢查數據目錄
    data_dirs = [
        "proxy_management/data/proxies",
        "proxy_management/data/archived", 
        "proxy_management/exports/working-proxies",
        "proxy_management/logs/system"
    ]
    
    for dir_path in data_dirs:
        path = Path(dir_path)
        if path.exists():
            files = list(path.glob("*"))
            print(f"✅ {dir_path}: {len(files)} 個文件")
        else:
            print(f"⚠️  {dir_path}: 目錄不存在")
            report["recommendations"].append(f"創建目錄：{dir_path}")
    
    # 保存報告
    report_file = Path("github_action_test_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 測試報告已保存：{report_file}")
    return report

def main():
    """主函數"""
    print("=" * 60)
    print("🚀 GitHub Actions 配置測試工具")
    print("=" * 60)
    print(f"測試時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"工作目錄：{os.getcwd()}")
    print()
    
    # 檢查配置文件
    config_ok = check_github_action_config()
    
    # 測試代理功能
    proxy_ok = test_proxy_functionality()
    
    # 模擬運行（可選）
    simulation_ok = True
    if input("是否模擬GitHub Action運行？（可能耗時較長）[y/N]: ").lower() == 'y':
        simulation_ok = simulate_github_action_run()
    
    # 生成報告
    report = generate_test_report()
    
    # 總結
    print("\n" + "=" * 60)
    print("📊 測試結果總結")
    print("=" * 60)
    print(f"GitHub配置：{'✅ 通過' if config_ok else '❌ 失敗'}")
    print(f"代理功能：{'✅ 通過' if proxy_ok else '❌ 失敗'}")
    print(f"模擬運行：{'✅ 通過' if simulation_ok else '❌ 失敗'}")
    
    if report["recommendations"]:
        print(f"\n🔧 改進建議：")
        for rec in report["recommendations"]:
            print(f"  - {rec}")
    
    # 最終建議
    print("\n💡 配置建議：")
    print("1. 確保在GitHub倉庫設置中添加必要的Secrets")
    print("2. 檢查工作流文件的權限設置")
    print("3. 監控首次自動執行的結果")
    print("4. 根據需要調整定時頻率")
    
    return config_ok and proxy_ok and simulation_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)