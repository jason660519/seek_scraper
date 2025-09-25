#!/usr/bin/env python3
"""
代理驗證器測試腳本
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from comprehensive_proxy_validator import ComprehensiveProxyValidator, ProxyInfo
from multi_layer_validation_system import MultiLayerValidationSystem
from geolocation_validator import PrecisionGeolocationValidator
from anonymity_level_tester import AdvancedAnonymityTester
from reliability_tester import AdvancedReliabilityTester

async def test_comprehensive_validator():
    """測試綜合驗證器"""
    print("🧪 測試綜合代理驗證器...")
    
    validator = ComprehensiveProxyValidator()
    
    # 創建測試代理
    test_proxies = [
        ProxyInfo(ip="8.8.8.8", port=8080, protocol="http", country="US", anonymity="elite", source="test"),
        ProxyInfo(ip="1.1.1.1", port=3128, protocol="http", country="US", anonymity="anonymous", source="test"),
    ]
    
    results = []
    for proxy in test_proxies:
        print(f"  測試代理: {proxy.ip}:{proxy.port}")
        result = validator.validate_proxy(proxy)
        results.append(result)
        
        print(f"    狀態: {'有效' if result.overall_score > 60 else '無效'}")
        print(f"    總分: {result.overall_score}")
        print(f"    連接性: {result.connectivity.status}")
        print(f"    性能: {result.performance.average_response_time if result.performance else 'N/A'}s")
        print(f"    地理位置: {result.geolocation.country if result.geolocation else 'N/A'}")
        print(f"    匿名等級: {result.anonymity.level if result.anonymity else 'N/A'}")
        print(f"    可靠性: {result.reliability.stability_score if result.reliability else 'N/A'}")
        print()
    
    return results

async def test_multi_layer_system():
    """測試多層次驗證系統"""
    print("🔍 測試多層次驗證系統...")
    
    system = MultiLayerValidationSystem()
    
    # 創建測試代理
    test_proxies = [
        ProxyInfo(ip="8.8.8.8", port=8080, protocol="http", country="US", anonymity="elite", source="test"),
        ProxyInfo(ip="1.1.1.1", port=3128, protocol="http", country="US", anonymity="anonymous", source="test"),
    ]
    
    print("  運行多層次驗證...")
    results = await system.validate_proxies(test_proxies)
    
    for i, result in enumerate(results):
        print(f"  代理 {i+1}:")
        print(f"    綜合評分: {result.overall_score}")
        print(f"    分類: {result.classification}")
        print(f"    建議: {result.recommendation}")
        print()
    
    return results

async def test_geolocation_validator():
    """測試地理位置驗證器"""
    print("🌍 測試地理位置驗證器...")
    
    validator = PrecisionGeolocationValidator()
    
    # 測試IP地址
    test_ips = ["8.8.8.8", "1.1.1.1"]
    
    for ip in test_ips:
        print(f"  測試IP: {ip}")
        result = await validator.validate_location(ip)
        
        print(f"    準確性分數: {result.accuracy_score}")
        print(f"    共識位置: {result.consensus_location}")
        print(f"    服務數量: {len(result.service_results)}")
        print()
    
    return True

async def test_anonymity_tester():
    """測試匿名等級測試器"""
    print("🎭 測試匿名等級測試器...")
    
    tester = AdvancedAnonymityTester()
    
    # 創建測試代理
    test_proxies = [
        ProxyInfo(ip="8.8.8.8", port=8080, protocol="http", country="US", anonymity="elite", source="test"),
    ]
    
    for proxy in test_proxies:
        print(f"  測試代理: {proxy.ip}:{proxy.port}")
        result = await tester.test_proxy(proxy)
        
        print(f"    匿名等級: {result.anonymity_level}")
        print(f"    洩漏數量: {len(result.leaks)}")
        print(f"    指紋分數: {result.fingerprint_score}")
        print()
    
    return True

async def test_reliability_tester():
    """測試可靠性測試器"""
    print("🔧 測試可靠性測試器...")
    
    tester = AdvancedReliabilityTester()
    
    # 創建測試代理
    test_proxies = [
        ProxyInfo(ip="8.8.8.8", port=8080, protocol="http", country="US", anonymity="elite", source="test"),
    ]
    
    for proxy in test_proxies:
        print(f"  測試代理: {proxy.ip}:{proxy.port}")
        result = await tester.test_proxy(proxy)
        
        print(f"    穩定性分數: {result.stability_score}")
        print(f"    負載分數: {result.load_score}")
        print(f"    故障恢復: {result.fault_recovery_score}")
        print(f"    網絡質量: {result.network_quality_score}")
        print(f"    資源使用: {result.resource_usage_score}")
        print()
    
    return True

def save_test_results(results, filename_prefix="test_results"):
    """保存測試結果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"
    
    # 轉換為可序列化的格式
    serializable_results = []
    for result in results:
        if hasattr(result, '__dict__'):
            serializable_results.append(result.__dict__)
        else:
            serializable_results.append(str(result))
    
    # 保存到文件
    output_path = Path("data") / filename
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_results, f, ensure_ascii=False, indent=2)
    
    print(f"💾 測試結果已保存到: {output_path}")
    return str(output_path)

async def main():
    """主函數"""
    print("🚀 開始代理驗證器測試")
    print("=" * 50)
    
    try:
        # 運行所有測試
        comprehensive_results = await test_comprehensive_validator()
        multi_layer_results = await test_multi_layer_system()
        
        # 地理位置測試（簡化版）
        await test_geolocation_validator()
        
        # 匿名性測試（簡化版）
        await test_anonymity_tester()
        
        # 可靠性測試（簡化版）
        await test_reliability_tester()
        
        print("=" * 50)
        print("✅ 所有測試完成！")
        
        # 保存結果
        save_test_results(comprehensive_results, "comprehensive_test_results")
        save_test_results(multi_layer_results, "multi_layer_test_results")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())