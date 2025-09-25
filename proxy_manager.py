#!/usr/bin/env python3
"""
代理管理工具
用於管理、篩選和測試代理IP
"""

import argparse
import pandas as pd
import requests
import time
from datetime import datetime
from pathlib import Path
import logging
import sys

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProxyManager:
    """代理管理器"""
    
    def __init__(self):
        self.proxies = []
        self.working_proxies = []
        
    def load_validation_results(self, csv_file: str):
        """載入驗證結果"""
        try:
            df = pd.read_csv(csv_file)
            self.proxies = df.to_dict('records')
            self.working_proxies = df[df['is_working'] == True].to_dict('records')
            logger.info(f"載入 {len(self.proxies)} 個代理，其中 {len(self.working_proxies)} 個有效")
        except Exception as e:
            logger.error(f"載入檔案失敗: {e}")
    
    def get_working_proxies(self, max_response_time: int = None, limit: int = None):
        """獲取有效代理，可按響應時間過濾"""
        proxies = self.working_proxies.copy()
        
        if max_response_time:
            proxies = [p for p in proxies if p.get('response_time_ms', 99999) <= max_response_time]
        
        # 按響應時間排序
        proxies.sort(key=lambda x: x.get('response_time_ms', 99999))
        
        if limit:
            proxies = proxies[:limit]
            
        return proxies
    
    def save_working_proxies(self, output_file: str, max_response_time: int = None, limit: int = None):
        """儲存有效代理到檔案"""
        working = self.get_working_proxies(max_response_time, limit)
        
        if not working:
            logger.error("沒有找到有效的代理")
            return
        
        # 準備資料
        proxy_list = []
        for proxy in working:
            proxy_list.append({
                'ip': proxy['ip'],
                'port': proxy['port'],
                'type': proxy['type'],
                'response_time_ms': proxy.get('response_time_ms', 0),
                'country': proxy.get('country', 'Unknown'),
                'proxy_url': f"{proxy['type']}://{proxy['ip']}:{proxy['port']}"
            })
        
        # 儲存為CSV
        df = pd.DataFrame(proxy_list)
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        logger.info(f"已儲存 {len(proxy_list)} 個有效代理到: {output_file}")
        return output_file
    
    def test_proxy_speed(self, proxy: dict, test_url: str = 'http://httpbin.org/ip') -> float:
        """測試單個代理的速度"""
        proxy_url = f"{proxy['type']}://{proxy['ip']}:{proxy['port']}"
        
        try:
            start_time = time.time()
            response = requests.get(
                test_url,
                proxies={'http': proxy_url, 'https': proxy_url},
                timeout=10
            )
            
            if response.status_code == 200:
                return round((time.time() - start_time) * 1000, 2)
        except:
            pass
        
        return None
    
    def benchmark_proxies(self, limit: int = 10, test_count: int = 3):
        """基準測試代理速度"""
        working = self.get_working_proxies(limit=limit)
        
        print(f"\n正在測試 {len(working)} 個代理的速度...")
        print("="*80)
        
        results = []
        
        for i, proxy in enumerate(working):
            print(f"測試 {i+1}/{len(working)}: {proxy['ip']}:{proxy['port']}", end=" ")
            
            speeds = []
            for j in range(test_count):
                speed = self.test_proxy_speed(proxy)
                if speed:
                    speeds.append(speed)
                print(".", end="")
            
            if speeds:
                avg_speed = sum(speeds) / len(speeds)
                results.append({
                    'ip': proxy['ip'],
                    'port': proxy['port'],
                    'avg_speed_ms': round(avg_speed, 2),
                    'success_rate': len(speeds) / test_count * 100
                })
                print(f" {avg_speed:.0f}ms ({len(speeds)}/{test_count})")
            else:
                print(" 失敗")
        
        # 按速度排序
        results.sort(key=lambda x: x['avg_speed_ms'])
        
        print(f"\n速度排名:")
        print("="*80)
        for i, result in enumerate(results[:10]):
            print(f"{i+1:2d}. {result['ip']:15s}:{result['port']:5d} "
                  f"- {result['avg_speed_ms']:6.0f}ms "
                  f"({result['success_rate']:3.0f}% 成功率)")
    
    def export_for_tools(self, output_format: str, filename: str, max_response_time: int = 5000):
        """匯出代理供其他工具使用"""
        working = self.get_working_proxies(max_response_time=max_response_time)
        
        if not working:
            logger.error("沒有找到符合條件的代理")
            return
        
        if output_format.lower() == 'txt':
            # 輸出為 IP:PORT 格式
            with open(filename, 'w', encoding='utf-8') as f:
                for proxy in working:
                    f.write(f"{proxy['ip']}:{proxy['port']}\n")
                    
        elif output_format.lower() == 'json':
            # 輸出為 JSON 格式
            import json
            proxy_list = []
            for proxy in working:
                proxy_list.append({
                    'ip': proxy['ip'],
                    'port': proxy['port'],
                    'type': proxy['type'],
                    'url': f"{proxy['type']}://{proxy['ip']}:{proxy['port']}"
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(proxy_list, f, indent=2, ensure_ascii=False)
                
        elif output_format.lower() == 'curl':
            # 輸出 curl 代理參數格式
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# Curl proxy parameters\\n")
                for proxy in working:
                    f.write(f'--proxy {proxy["ip"]}:{proxy["port"]}\\n')
        
        logger.info(f"已匯出 {len(working)} 個代理到 {filename} ({output_format} 格式)")

def main():
    parser = argparse.ArgumentParser(description='代理管理工具')
    parser.add_argument('--load-results', required=True, help='載入驗證結果CSV檔案')
    parser.add_argument('--save-working', help='儲存有效代理到檔案')
    parser.add_argument('--max-response-time', type=int, help='最大響應時間過濾(毫秒)')
    parser.add_argument('--limit', type=int, help='限制代理數量')
    parser.add_argument('--benchmark', action='store_true', help='執行速度基準測試')
    parser.add_argument('--export-format', choices=['txt', 'json', 'curl'], help='匯出格式')
    parser.add_argument('--export-file', help='匯出檔案名')
    parser.add_argument('--show-stats', action='store_true', help='顯示統計資訊')
    
    args = parser.parse_args()
    
    manager = ProxyManager()
    
    # 載入驗證結果
    manager.load_validation_results(args.load_results)
    
    if args.show_stats:
        working = manager.get_working_proxies()
        if working:
            response_times = [p.get('response_time_ms', 0) for p in working]
            
            print(f"\n代理統計資訊:")
            print("="*50)
            print(f"總代理數: {len(manager.proxies)}")
            print(f"有效代理: {len(working)}")
            print(f"成功率: {len(working)/len(manager.proxies)*100:.2f}%")
            print(f"平均響應時間: {sum(response_times)/len(response_times):.0f}ms")
            print(f"最快響應時間: {min(response_times):.0f}ms")
            print(f"最慢響應時間: {max(response_times):.0f}ms")
            
            # 響應時間分布
            fast = len([t for t in response_times if t < 1000])
            medium = len([t for t in response_times if 1000 <= t < 3000])
            slow = len([t for t in response_times if t >= 3000])
            
            print(f"\n響應時間分布:")
            print(f"  快速 (<1秒): {fast} 個 ({fast/len(working)*100:.1f}%)")
            print(f"  中等 (1-3秒): {medium} 個 ({medium/len(working)*100:.1f}%)")
            print(f"  較慢 (>3秒): {slow} 個 ({slow/len(working)*100:.1f}%)")
    
    if args.save_working:
        manager.save_working_proxies(
            args.save_working, 
            args.max_response_time, 
            args.limit
        )
    
    if args.benchmark:
        manager.benchmark_proxies(limit=args.limit or 10)
    
    if args.export_format and args.export_file:
        manager.export_for_tools(
            args.export_format, 
            args.export_file, 
            args.max_response_time or 5000
        )

if __name__ == "__main__":
    main()