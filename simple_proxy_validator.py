#!/usr/bin/env python3
"""
簡化版代理IP有效性驗證工具
專門針對 Proxifly 代理進行測試
"""

import argparse
import pandas as pd
import csv
from datetime import datetime
import logging
from pathlib import Path
import time
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import requests
import sys

# 設置控制台輸出編碼
sys.stdout.reconfigure(encoding='utf-8')

# 設置日誌 - 避免 Unicode 問題
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('proxy_validator.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SimpleProxyValidator:
    """簡化版代理IP驗證器"""
    
    def __init__(self, timeout: int = 5, max_workers: int = 20):
        self.timeout = timeout
        self.max_workers = max_workers
        self.test_url = 'http://httpbin.org/ip'
        self.results = []
        
    def load_proxies_from_csv(self, csv_file: str) -> list:
        """從CSV檔案載入代理列表"""
        proxies = []
        try:
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                if 'ip' in row and 'port' in row:
                    # 如果類型是 Unknown，預設為 http
                    proxy_type = 'http' if row.get('type', 'Unknown') == 'Unknown' else row['type'].lower()
                    
                    proxies.append({
                        'ip': str(row['ip']).strip(),
                        'port': int(row['port']),
                        'type': proxy_type,
                        'country': row.get('country', 'Unknown'),
                        'source': csv_file
                    })
        except Exception as e:
            logger.error(f"載入CSV檔案失敗 {csv_file}: {e}")
        
        logger.info(f"成功載入 {len(proxies)} 個代理")
        return proxies
    
    def test_single_proxy(self, proxy: dict) -> dict:
        """測試單個代理"""
        proxy_url = f"{proxy['type']}://{proxy['ip']}:{proxy['port']}"
        
        result = {
            'ip': proxy['ip'],
            'port': proxy['port'],
            'type': proxy['type'],
            'country': proxy['country'],
            'is_working': False,
            'response_time_ms': None,
            'error': None,
            'test_time': datetime.now().isoformat(),
            'status': 'Failed'
        }
        
        try:
            proxies_dict = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            start_time = time.time()
            
            response = requests.get(
                self.test_url,
                proxies=proxies_dict,
                timeout=self.timeout,
                headers={'User-Agent': 'ProxyValidator/1.0'}
            )
            
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                result['is_working'] = True
                result['response_time_ms'] = response_time
                result['status'] = 'Success'
                logger.info(f"OK: {proxy['ip']}:{proxy['port']} ({response_time}ms)")
                return result
            else:
                result['error'] = f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            result['error'] = 'Timeout'
        except requests.exceptions.ConnectionError:
            result['error'] = 'Connection Error'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def validate_proxies(self, proxies: list) -> list:
        """批量驗證代理"""
        logger.info(f"開始驗證 {len(proxies)} 個代理...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.test_single_proxy, proxy) for proxy in proxies]
            
            results = []
            completed = 0
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    if completed % 10 == 0 or completed == len(proxies):
                        working_count = sum(1 for r in results if r['is_working'])
                        logger.info(f"進度: {completed}/{len(proxies)} - 有效: {working_count}")
                        
                except Exception as e:
                    logger.error(f"代理測試異常: {e}")
                    completed += 1
        
        self.results = results
        return results
    
    def save_results(self, results: list, output_file: str = None) -> str:
        """儲存驗證結果"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"data/proxies/proxy_validation_{timestamp}.csv"
        
        # 確保目錄存在
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # 儲存為CSV
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        # 統計
        total_count = len(results)
        working_count = sum(1 for r in results if r['is_working'])
        working_rate = (working_count / total_count * 100) if total_count > 0 else 0
        
        logger.info(f"驗證完成!")
        logger.info(f"總代理數: {total_count}")
        logger.info(f"有效代理: {working_count}")
        logger.info(f"成功率: {working_rate:.2f}%")
        logger.info(f"結果已儲存: {output_file}")
        
        return output_file
    
    def get_working_proxies(self) -> list:
        """獲取有效的代理列表"""
        return [r for r in self.results if r['is_working']]
    
    def show_working_proxies(self, limit: int = 10):
        """顯示有效的代理"""
        working = self.get_working_proxies()
        if not working:
            print("沒有找到有效的代理")
            return
        
        print(f"\n找到 {len(working)} 個有效代理:")
        print("=" * 60)
        
        for i, proxy in enumerate(working[:limit]):
            print(f"{i+1:2d}. {proxy['ip']:15s}:{proxy['port']:5d} "
                  f"({proxy['response_time_ms']:6.0f}ms) - {proxy['country']}")
        
        if len(working) > limit:
            print(f"... 還有 {len(working) - limit} 個代理")

def main():
    parser = argparse.ArgumentParser(description='簡化版代理IP驗證工具')
    parser.add_argument('--csv-file', help='要驗證的CSV代理檔案')
    parser.add_argument('--timeout', type=int, default=5, help='連接超時時間(秒)')
    parser.add_argument('--max-workers', type=int, default=20, help='最大併發數')
    parser.add_argument('--output', help='輸出檔案路徑')
    parser.add_argument('--validate-latest', action='store_true', help='驗證最新的代理檔案')
    parser.add_argument('--show-working', type=int, default=10, help='顯示有效代理數量')
    
    args = parser.parse_args()
    
    validator = SimpleProxyValidator(timeout=args.timeout, max_workers=args.max_workers)
    
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
    
    # 顯示有效代理
    validator.show_working_proxies(args.show_working)
    
    # 統計資訊
    total_count = len(results)
    working_count = sum(1 for r in results if r['is_working'])
    
    print(f"\n" + "="*50)
    print(f"驗證摘要")
    print("="*50)
    print(f"總代理數: {total_count}")
    print(f"有效代理: {working_count}")
    print(f"成功率: {(working_count/total_count*100):.2f}%")
    print(f"結果檔案: {output_file}")

if __name__ == "__main__":
    main()