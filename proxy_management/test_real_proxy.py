#!/usr/bin/env python3
"""
測試實際的代理連接功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.proxy_validator import ProxyValidator

def test_real_proxies():
    """測試實際的代理連接"""
    print('=== 測試實際代理連接 ===')
    
    # 創建驗證器，設置較短的超時時間
    validator = ProxyValidator(timeout=5, max_workers=5)
    
    # 從現有的有效代理中選擇幾個進行測試
    proxies = [
        {'ip': '23.237.210.82', 'port': 80, 'type': 'http', 'country': 'Unknown', 'source': 'test'},
        {'ip': '23.247.136.254', 'port': 80, 'type': 'http', 'country': 'Unknown', 'source': 'test'}
    ]
    
    print(f'開始測試 {len(proxies)} 個代理的連接性...')
    
    # 執行驗證
    results = validator.validate_proxies(proxies)
    
    # 統計結果
    working_count = sum(1 for r in results if r['is_working'])
    print(f'\n測試完成！')
    print(f'總代理數: {len(results)}')
    print(f'有效代理: {working_count}')
    if len(results) > 0:
        print(f'成功率: {(working_count/len(results)*100):.1f}%')
    else:
        print('成功率: 0% (沒有測試結果)')
    
    print('\n詳細結果:')
    for result in results:
        status = '✅有效' if result['is_working'] else '❌無效'
        if result['is_working']:
            response_time = f"{result['response_time']}ms"
            anonymity = result.get('anonymity_level', 'Unknown')
            print(f'{status} {result["ip"]}:{result["port"]} - {response_time} - {anonymity}')
        else:
            error = result.get('error_message', 'Unknown error')
            print(f'{status} {result["ip"]}:{result["port"]} - {error}')
    
    return working_count > 0

if __name__ == "__main__":
    success = test_real_proxies()
    if success:
        print('\n🎉 代理連接測試成功！')
    else:
        print('\n⚠️  代理連接測試失敗，可能需要更新代理列表')