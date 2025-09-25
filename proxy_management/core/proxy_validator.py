#!/usr/bin/env python3
"""
代理IP有效性驗證工具
支援批量測試代理的連接性、響應時間和匿名性
"""

import argparse
import pandas as pd
import csv
from datetime import datetime
import logging
from pathlib import Path
import time
import json
from typing import List, Dict, Tuple, Optional
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import requests

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('proxy_validator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProxyValidator:
    """代理IP驗證器"""
    
    def __init__(self, timeout: int = 10, max_workers: int = 50):
        self.timeout = timeout
        self.max_workers = max_workers
        self.test_urls = [
            'http://httpbin.org/ip',
            'http://icanhazip.com',
            'http://ipinfo.io/ip',
            'http://checkip.amazonaws.com',
        ]
        self.results = []
        
    def load_proxies_from_csv(self, csv_file: str) -> List[Dict]:
        """從CSV檔案載入代理列表"""
        proxies = []
        try:
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                if 'ip' in row and 'port' in row:
                    proxy_type = row.get('type', 'http').lower()
                    proxies.append({
                        'ip': row['ip'],
                        'port': int(row['port']),
                        'type': proxy_type,
                        'country': row.get('country', 'Unknown'),
                        'source': csv_file
                    })
        except Exception as e:
            logger.error(f"載入CSV檔案失敗 {csv_file}: {e}")
        
        return proxies
    
    def load_proxies_from_txt(self, txt_file: str, proxy_type: str = 'http') -> List[Dict]:
        """從TXT檔案載入代理列表"""
        proxies = []
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line:
                        # 處理可能包含協議前綴的URL
                        if '://' in line:
                            line = line.split('://', 1)[1]
                        
                        # 分割IP和端口
                        if ':' in line:
                            ip, port = line.rsplit(':', 1)
                            try:
                                port_num = int(port.strip())
                                proxies.append({
                                    'ip': ip.strip(),
                                    'port': port_num,
                                    'type': proxy_type,
                                    'country': 'Unknown',
                                    'source': txt_file
                                })
                            except ValueError:
                                logger.warning(f"無效的端口號: {port}")
                                continue
        except Exception as e:
            logger.error(f"載入TXT檔案失敗 {txt_file}: {e}")
        
        return proxies
    
    def test_proxy_sync(self, proxy: Dict) -> Dict:
        """同步測試單個代理"""
        proxy_url = f"{proxy['type']}://{proxy['ip']}:{proxy['port']}"
        
        result = {
            'ip': proxy['ip'],
            'port': proxy['port'],
            'type': proxy['type'],
            'country': proxy['country'],
            'source': proxy['source'],
            'is_working': False,
            'response_time': None,
            'error_message': None,
            'test_time': datetime.now().isoformat(),
            'anonymity_level': 'Unknown'
        }
        
        try:
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            start_time = time.time()
            
            # 測試基本連接性
            response = requests.get(
                self.test_urls[0],
                proxies=proxies,
                timeout=self.timeout,
                headers={'User-Agent': 'ProxyValidator/1.0'}
            )
            
            response_time = round((time.time() - start_time) * 1000, 2)  # ms
            
            if response.status_code == 200:
                result['is_working'] = True
                result['response_time'] = response_time
                
                # 檢查匿名性
                try:
                    response_data = response.json()
                    proxy_ip = response_data.get('origin', '')
                    
                    # 如果返回的IP是代理IP，說明是匿名代理
                    if proxy['ip'] in proxy_ip:
                        result['anonymity_level'] = 'Transparent'
                    else:
                        result['anonymity_level'] = 'Anonymous'
                        
                except:
                    result['anonymity_level'] = 'Unknown'
                    
                logger.info(f"✅ 代理可用: {proxy['ip']}:{proxy['port']} ({response_time}ms)")
            else:
                result['error_message'] = f"HTTP {response.status_code}"
                logger.warning(f"❌ 代理不可用: {proxy['ip']}:{proxy['port']} - HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            result['error_message'] = 'Timeout'
            logger.warning(f"⏱️ 代理超時: {proxy['ip']}:{proxy['port']}")
            
        except requests.exceptions.ConnectionError:
            result['error_message'] = 'Connection Error'
            logger.warning(f"🔌 連接錯誤: {proxy['ip']}:{proxy['port']}")
            
        except Exception as e:
            result['error_message'] = str(e)
            logger.error(f"❌ 測試失敗: {proxy['ip']}:{proxy['port']} - {e}")
        
        return result
    
    def validate_proxies(self, proxies: List[Dict]) -> List[Dict]:
        """批量驗證代理"""
        logger.info(f"開始驗證 {len(proxies)} 個代理...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.test_proxy_sync, proxy) for proxy in proxies]
            
            results = []
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                try:
                    result = future.result()
                    results.append(result)
                    
                    if (i + 1) % 10 == 0:
                        working_count = sum(1 for r in results if r['is_working'])
                        logger.info(f"已測試 {i + 1}/{len(proxies)} 個代理，有效: {working_count}")
                        
                except Exception as e:
                    logger.error(f"代理測試異常: {e}")
        
        self.results = results
        return results
    
    def save_results(self, results: List[Dict], output_file: str = None) -> str:
        """儲存驗證結果"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"data/proxies/proxy_validation_{timestamp}.csv"
        
        # 確保目錄存在
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # 儲存為CSV
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        # 統計資訊
        total_count = len(results)
        working_count = sum(1 for r in results if r['is_working'])
        working_rate = (working_count / total_count * 100) if total_count > 0 else 0
        
        logger.info(f"驗證完成！")
        logger.info(f"總代理數: {total_count}")
        logger.info(f"有效代理: {working_count}")
        logger.info(f"有效率: {working_rate:.2f}%")
        logger.info(f"結果已儲存至: {output_file}")
        
        return output_file
    
    def get_working_proxies(self) -> List[Dict]:
        """獲取有效的代理列表"""
        return [r for r in self.results if r['is_working']]
    
    def get_statistics(self) -> Dict:
        """獲取統計資訊"""
        if not self.results:
            return {}
        
        total_count = len(self.results)
        working_count = sum(1 for r in self.results if r['is_working'])
        
        # 按國家統計
        country_stats = {}
        for result in self.results:
            country = result['country']
            if country not in country_stats:
                country_stats[country] = {'total': 0, 'working': 0}
            country_stats[country]['total'] += 1
            if result['is_working']:
                country_stats[country]['working'] += 1
        
        # 按類型統計
        type_stats = {}
        for result in self.results:
            proxy_type = result['type']
            if proxy_type not in type_stats:
                type_stats[proxy_type] = {'total': 0, 'working': 0}
            type_stats[proxy_type]['total'] += 1
            if result['is_working']:
                type_stats[proxy_type]['working'] += 1
        
        # 響應時間統計
        working_results = self.get_working_proxies()
        response_times = [r['response_time'] for r in working_results if r['response_time']]
        
        stats = {
            'total_proxies': total_count,
            'working_proxies': working_count,
            'success_rate': round((working_count / total_count * 100), 2) if total_count > 0 else 0,
            'country_stats': country_stats,
            'type_stats': type_stats,
            'response_time_stats': {
                'count': len(response_times),
                'min': min(response_times) if response_times else 0,
                'max': max(response_times) if response_times else 0,
                'avg': round(sum(response_times) / len(response_times), 2) if response_times else 0
            }
        }
        
        return stats

def main():
    parser = argparse.ArgumentParser(description='代理IP有效性驗證工具')
    parser.add_argument('--csv-file', help='要驗證的CSV代理檔案')
    parser.add_argument('--txt-file', help='要驗證的TXT代理檔案')
    parser.add_argument('--proxy-type', default='http', choices=['http', 'https', 'socks4', 'socks5'], 
                       help='代理類型 (僅適用於TXT檔案)')
    parser.add_argument('--timeout', type=int, default=10, help='連接超時時間(秒)')
    parser.add_argument('--max-workers', type=int, default=50, help='最大併發數')
    parser.add_argument('--output', help='輸出檔案路徑')
    parser.add_argument('--validate-latest', action='store_true', help='驗證最新的代理檔案')
    parser.add_argument('--show-stats', action='store_true', help='顯示詳細統計資訊')
    
    args = parser.parse_args()
    
    validator = ProxyValidator(timeout=args.timeout, max_workers=args.max_workers)
    
    # 載入代理
    proxies = []
    
    if args.validate_latest:
        # 找到最新的代理檔案
        proxy_dir = Path("data/proxies")
        if proxy_dir.exists():
            csv_files = list(proxy_dir.glob("proxies_*.csv"))
            if csv_files:
                latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
                logger.info(f"載入最新代理檔案: {latest_file}")
                proxies = validator.load_proxies_from_csv(str(latest_file))
    
    elif args.csv_file:
        proxies = validator.load_proxies_from_csv(args.csv_file)
    
    elif args.txt_file:
        proxies = validator.load_proxies_from_txt(args.txt_file, args.proxy_type)
    
    else:
        logger.error("請指定要驗證的代理檔案或使用 --validate-latest 參數")
        return
    
    if not proxies:
        logger.error("沒有找到可驗證的代理")
        return
    
    # 驗證代理
    results = validator.validate_proxies(proxies)
    
    # 儲存結果
    output_file = validator.save_results(results, args.output)
    
    # 顯示統計資訊
    stats = validator.get_statistics()
    
    print("\n" + "="*50)
    print("📊 驗證統計資訊")
    print("="*50)
    print(f"總代理數: {stats['total_proxies']}")
    print(f"有效代理: {stats['working_proxies']}")
    print(f"成功率: {stats['success_rate']}%")
    
    if args.show_stats and stats['response_time_stats']['count'] > 0:
        print(f"\n⏱️ 響應時間統計:")
        print(f"  最快: {stats['response_time_stats']['min']}ms")
        print(f"  最慢: {stats['response_time_stats']['max']}ms")
        print(f"  平均: {stats['response_time_stats']['avg']}ms")
    
    if args.show_stats:
        print(f"\n🌍 按國家統計:")
        for country, stat in stats['country_stats'].items():
            rate = (stat['working'] / stat['total'] * 100) if stat['total'] > 0 else 0
            print(f"  {country}: {stat['working']}/{stat['total']} ({rate:.1f}%)")
        
        print(f"\n📡 按類型統計:")
        for proxy_type, stat in stats['type_stats'].items():
            rate = (stat['working'] / stat['total'] * 100) if stat['total'] > 0 else 0
            print(f"  {proxy_type}: {stat['working']}/{stat['total']} ({rate:.1f}%)")
    
    print(f"\n結果已儲存至: {output_file}")

if __name__ == "__main__":
    main()