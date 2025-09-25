"""
簡單的代理更新測試腳本
用於測試 Proxifly 是否真的每 5 分鐘更新代理列表
"""

import time
import requests
import hashlib
from datetime import datetime


def get_proxy_list_hash(proxy_type='http'):
    """獲取代理列表的哈希值"""
    url = f'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/{proxy_type}/data.txt'
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 計算內容的 MD5 哈希
        content_hash = hashlib.md5(response.text.encode()).hexdigest()
        proxy_count = len(response.text.strip().split('\n'))
        
        return content_hash, proxy_count, response.text[:100]  # 返回前100個字符用於比較
    except Exception as e:
        print(f"錯誤: {e}")
        return None, 0, ""


def monitor_updates(duration_minutes=30, check_interval_seconds=60):
    """
    監控代理列表更新
    
    Args:
        duration_minutes: 監控持續時間（分鐘）
        check_interval_seconds: 檢查間隔（秒）
    """
    print(f"開始監控代理更新 - 持續 {duration_minutes} 分鐘，每 {check_interval_seconds} 秒檢查一次")
    print("=" * 80)
    
    last_hash = None
    last_update_time = None
    update_count = 0
    
    start_time = datetime.now()
    end_time = start_time.timestamp() + (duration_minutes * 60)
    
    while time.time() < end_time:
        current_time = datetime.now()
        current_hash, proxy_count, content_preview = get_proxy_list_hash()
        
        if current_hash:
            if last_hash is None:
                # 第一次檢查
                print(f"[{current_time.strftime('%H:%M:%S')}] 初始檢查 - 代理數量: {proxy_count}")
                print(f"內容預覽: {content_preview}...")
                print(f"哈希值: {current_hash}")
                last_hash = current_hash
                last_update_time = current_time
            elif current_hash != last_hash:
                # 檢測到更新
                update_count += 1
                time_diff = (current_time - last_update_time).total_seconds() / 60
                print(f"\n🔄 [更新 #{update_count}] [{current_time.strftime('%H:%M:%S')}] 代理列表已更新！")
                print(f"距離上次更新: {time_diff:.1f} 分鐘")
                print(f"新的代理數量: {proxy_count}")
                print(f"新哈希值: {current_hash}")
                print(f"新內容預覽: {content_preview}...")
                
                last_hash = current_hash
                last_update_time = current_time
            else:
                # 沒有更新
                time_diff = (current_time - last_update_time).total_seconds() / 60
                print(f"[{current_time.strftime('%H:%M:%S')}] 無更新 - 距離上次更新 {time_diff:.1f} 分鐘 (代理數量: {proxy_count})")
        
        time.sleep(check_interval_seconds)
    
    print("\n" + "=" * 80)
    print("監控結束")
    print(f"監控時長: {duration_minutes} 分鐘")
    print(f"檢測到更新次數: {update_count}")
    if update_count > 0:
        avg_interval = duration_minutes / update_count if update_count > 0 else 0
        print(f"平均更新間隔: {avg_interval:.1f} 分鐘")


if __name__ == "__main__":
    # 測試 15 分鐘，每分鐘檢查一次
    monitor_updates(duration_minutes=15, check_interval_seconds=60)