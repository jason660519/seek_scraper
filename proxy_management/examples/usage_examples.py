"""
代理管理系統使用示例
展示如何使用全新的代理獲取與管理模組
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

# 導入核心模組
from comprehensive_proxy_manager import ComprehensiveProxyManager
from proxy_lifecycle_manager import ProxyLifecycleManager
from proxy_automation_scheduler import ProxyAutomationScheduler


def example_basic_usage():
    """基本使用示例"""
    print("=== 代理管理系統基本使用示例 ===\n")
    
    # 1. 創建代理管理器
    manager = ComprehensiveProxyManager()
    print("✓ 代理管理器創建完成")
    
    # 2. 獲取代理
    print("\n正在獲取代理...")
    proxies = manager.fetch_proxies_from_multiple_sources()
    print(f"✓ 成功獲取 {len(proxies)} 個代理")
    
    # 3. 驗證代理
    print("\n正在驗證代理...")
    validated_proxies = manager.validate_proxy_batch(proxies, batch_size=50)
    print(f"✓ 驗證完成：{len(validated_proxies)} 個代理")
    
    # 4. 查看統計
    stats = manager.get_proxy_statistics()
    print(f"\n代理統計:")
    print(f"  - 有效代理: {stats['valid_count']}")
    print(f"  - 暫時無效: {stats['temp_invalid_count']}")
    print(f"  - 無效代理: {stats['invalid_count']}")
    print(f"  - 未測試: {stats['untested_count']}")
    
    # 5. 導出結果
    print("\n正在導出結果...")
    json_file = manager.export_proxies('json', manager.ProxyStatus.VALID)
    txt_file = manager.export_proxies('txt', manager.ProxyStatus.VALID)
    print(f"✓ JSON格式: {json_file}")
    print(f"✓ TXT格式: {txt_file}")


def example_lifecycle_management():
    """生命週期管理示例"""
    print("\n\n=== 代理生命週期管理示例 ===\n")
    
    # 創建管理器
    manager = ComprehensiveProxyManager()
    lifecycle_manager = ProxyLifecycleManager(manager)
    
    # 獲取一些代理進行測試
    proxies = manager.fetch_proxies_from_multiple_sources(country='US', limit=20)
    print(f"獲取 {len(proxies)} 個美國代理進行生命週期測試")
    
    # 模擬代理狀態變化
    print("\n模擬代理狀態變化...")
    
    # 1. 追蹤獲取
    lifecycle_manager.track_proxy_fetching(proxies)
    print("✓ 追蹤代理獲取")
    
    # 2. 驗證代理
    validated_proxies = manager.validate_proxy_batch(proxies[:10])
    lifecycle_manager.track_proxy_validation(validated_proxies)
    print("✓ 追蹤代理驗證")
    
    # 3. 模擬狀態變化
    if validated_proxies:
        test_proxy = validated_proxies[0]
        
        # 從有效變為暫時無效
        old_status = test_proxy.status
        test_proxy.status = manager.ProxyStatus.TEMP_INVALID
        test_proxy.fail_count = 1
        lifecycle_manager.track_status_change(test_proxy, old_status, test_proxy.status)
        print(f"✓ 追蹤狀態變化: {old_status.value} -> {test_proxy.status.value}")
    
    # 4. 獲取分析報告
    analytics = lifecycle_manager.get_lifecycle_analytics()
    print(f"\n生命週期分析:")
    print(f"  - 總代理數: {analytics['total_proxies']}")
    print(f"  - 狀態變化次數: {analytics['total_transitions']}")
    print(f"  - 平均生命週期: {analytics['avg_lifecycle_hours']:.1f} 小時")
    
    # 5. 導出報告
    report_file = lifecycle_manager.export_lifecycle_report('json')
    print(f"✓ 生命週期報告: {report_file}")


def example_automation_scheduler():
    """自動化調度器示例"""
    print("\n\n=== 自動化調度器示例 ===\n")
    
    # 創建調度器
    scheduler = ProxyAutomationScheduler()
    print("✓ 自動化調度器創建完成")
    
    # 查看當前狀態
    status = scheduler.get_status()
    print(f"\n調度器狀態:")
    print(f"  - 運行狀態: {status['is_running']}")
    print(f"  - 下一個任務: {len(status['next_tasks'])} 個")
    
    # 手動執行任務
    print("\n手動執行任務測試...")
    
    # 執行獲取任務
    print("1. 執行獲取代理任務")
    scheduler.run_task_now('fetch')
    
    # 執行驗證任務
    print("2. 執行驗證代理任務")
    scheduler.run_task_now('validate')
    
    # 執行報告任務
    print("3. 執行生成報告任務")
    scheduler.run_task_now('report')
    
    # 查看任務歷史
    task_history = status['task_status']['task_history']
    print(f"\n最近任務歷史 ({len(task_history[-5:])} 個):")
    for task in task_history[-5:]:
        print(f"  - {task['task_name']}: {task['status']} ({task['timestamp']})")


def example_custom_configuration():
    """自定義配置示例"""
    print("\n\n=== 自定義配置示例 ===\n")
    
    # 創建自定義配置
    custom_config = {
        'fetch_schedule': {
            'enabled': True,
            'interval_hours': 2,  # 每2小時獲取一次
            'max_proxies_per_fetch': 500,
            'retry_failed_interval_hours': 1
        },
        'validation_schedule': {
            'enabled': True,
            'interval_hours': 1,  # 每小時驗證一次
            'batch_size': 50,
            'retry_temp_invalid_interval_hours': 3
        },
        'notification_config': {
            'enabled': True,
            'notify_on_errors': True,
            'notify_on_low_proxies': True,
            'min_valid_proxies_threshold': 100  # 有效代理少於100個時通知
        }
    }
    
    # 保存配置到文件
    config_file = Path("custom_proxy_config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(custom_config, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 自定義配置已保存: {config_file}")
    
    # 使用自定義配置創建調度器
    scheduler = ProxyAutomationScheduler(str(config_file))
    print("✓ 使用自定義配置的調度器創建完成")
    
    # 顯示配置
    print(f"\n自定義配置:")
    print(f"  - 獲取間隔: {custom_config['fetch_schedule']['interval_hours']} 小時")
    print(f"  - 驗證間隔: {custom_config['validation_schedule']['interval_hours']} 小時")
    print(f"  - 通知閾值: {custom_config['notification_config']['min_valid_proxies_threshold']} 個代理")


def example_error_handling():
    """錯誤處理示例"""
    print("\n\n=== 錯誤處理示例 ===\n")
    
    manager = ComprehensiveProxyManager()
    
    try:
        # 嘗試獲取不存在的國家代理
        print("嘗試獲取不存在的國家代理...")
        proxies = manager.fetch_proxies_from_multiple_sources(country='XX')
        
    except Exception as e:
        print(f"✓ 捕獲到預期錯誤: {e}")
    
    try:
        # 嘗試驗證空代理列表
        print("\n嘗試驗證空代理列表...")
        manager.validate_proxy_batch([])
        
    except Exception as e:
        print(f"✓ 捕獲到預期錯誤: {e}")
    
    # 顯示錯誤日誌位置
    log_dir = Path("logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        if log_files:
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
            print(f"\n錯誤日誌位置: {latest_log}")


def main():
    """主函數 - 運行所有示例"""
    print("代理管理系統完整示例")
    print("=" * 50)
    
    # 運行所有示例
    try:
        example_basic_usage()
        example_lifecycle_management()
        example_automation_scheduler()
        example_custom_configuration()
        example_error_handling()
        
        print("\n\n" + "=" * 50)
        print("✓ 所有示例執行完成！")
        print("\n系統已準備就緒，您現在可以：")
        print("1. 使用代理管理器手動管理代理")
        print("2. 啟動自動化調度器進行定時管理")
        print("3. 查看生成的報告和日誌")
        print("4. 根據需要自定義配置")
        
    except KeyboardInterrupt:
        print("\n\n用戶中斷，示例提前結束")
    except Exception as e:
        print(f"\n\n執行過程中發生錯誤: {e}")
        print("請查看日誌文件獲取詳細信息")


if __name__ == "__main__":
    main()