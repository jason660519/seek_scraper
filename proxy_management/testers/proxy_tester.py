"""
SEEK 爬蟲專案 - 免費代理 IP 測試工具

此模組用於測試 proxifly 免費代理列表 API，
定期獲取代理 IP 並儲存為 CSV 格式，同時監控更新頻率。

API 限制:
- 免費版本：每5分鐘更新約500個IP
- 付費版本：一個月只能呼叫100次API

使用方法:
    python proxy_tester.py --test-once        # 單次測試
    python proxy_tester.py --monitor          # 持續監控
    python proxy_tester.py --validate-proxies # 驗證代理有效性
"""

import requests
import pandas as pd
import time
import schedule
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import csv
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('proxy_tester.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProxyTester:
    """代理 IP 測試器類別"""
    
    def __init__(self):
        """
        初始化代理測試器
        
        注意：Proxifly 免費代理列表不需要 API 金鑰，直接從 GitHub CDN 獲取
        """
        self.base_urls = {
            'all': 'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/all/data.json',
            'http': 'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.json',
            'socks4': 'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks4/data.json',
            'socks5': 'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.json'
        }
        self.data_dir = Path("data/proxies")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 儲存歷史數據以追蹤更新
        self.history_file = self.data_dir / "proxy_history.json"
        self.load_history()
    
    def load_history(self):
        """載入歷史記錄"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
                # 確保 unique_proxies_seen 是 set 類型
                self.history = {
                    'fetch_times': history_data.get('fetch_times', []),
                    'proxy_counts': history_data.get('proxy_counts', []),
                    'unique_proxies_seen': set(history_data.get('unique_proxies_seen', []))
                }
        else:
            self.history = {
                'fetch_times': [],
                'proxy_counts': [],
                'unique_proxies_seen': set()
            }
    
    def save_history(self):
        """儲存歷史記錄"""
        # 將 set 轉換為 list 以便 JSON 序列化
        history_to_save = self.history.copy()
        history_to_save['unique_proxies_seen'] = list(self.history['unique_proxies_seen'])
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history_to_save, f, indent=2, ensure_ascii=False)
    
    def fetch_proxies(self, proxy_type: str = 'all') -> Optional[List[Dict]]:
        """
        從 Proxifly GitHub CDN 獲取代理列表
        
        Args:
            proxy_type: 代理類型 ('all', 'http', 'socks4', 'socks5')
        
        Returns:
            代理列表或 None（如果失敗）
        """
        if proxy_type not in self.base_urls:
            logger.error(f"不支援的代理類型: {proxy_type}")
            return None
            
        url = self.base_urls[proxy_type]
        
        try:
            logger.info(f"正在從 {proxy_type} 類型獲取代理列表...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                # 如果 JSON 解析失敗，嘗試解析為純文字格式
                logger.warning("JSON 解析失敗，嘗試解析為純文字格式...")
                text_url = url.replace('.json', '.txt')
                response = requests.get(text_url, timeout=30)
                response.raise_for_status()
                
                # 解析純文字格式 (ip:port 每行一個)
                proxies = []
                for line in response.text.strip().split('\n'):
                    if ':' in line:
                        ip, port = line.strip().split(':', 1)
                        proxy = {
                            'ip': ip,
                            'port': int(port) if port.isdigit() else port,
                            'type': proxy_type,
                            'country': 'Unknown',
                            'anonymity': 'Unknown'
                        }
                        proxies.append(proxy)
                return proxies
            
            # 如果是 JSON 格式，處理數據結構
            if isinstance(data, list):
                proxies = data
            elif isinstance(data, dict) and 'proxies' in data:
                proxies = data['proxies']
            else:
                logger.error(f"未知的資料格式: {type(data)}")
                return None
            
            logger.info(f"成功獲取 {len(proxies)} 個 {proxy_type} 代理")
            
            # 記錄歷史
            fetch_time = datetime.now().isoformat()
            self.history['fetch_times'].append(fetch_time)
            self.history['proxy_counts'].append(len(proxies))
            
            # 追蹤唯一代理
            for proxy in proxies:
                if isinstance(proxy, dict):
                    proxy_id = f"{proxy.get('ip')}:{proxy.get('port')}"
                else:
                    # 處理純字串格式 "ip:port"
                    proxy_id = str(proxy)
                    
                self.history['unique_proxies_seen'].add(proxy_id)
            
            self.save_history()
            return proxies
            
        except requests.exceptions.RequestException as e:
            logger.error(f"請求失敗: {e}")
            return None
        except Exception as e:
            logger.error(f"未預期的錯誤: {e}")
            return None
    
    def save_proxies_to_csv(self, proxies: List[Dict], filename: Optional[str] = None) -> str:
        """
        將代理列表儲存為 CSV 檔案
        
        Args:
            proxies: 代理列表
            filename: 檔案名稱（可選）
            
        Returns:
            儲存的檔案路徑
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"proxies_{timestamp}.csv"
        
        filepath = self.data_dir / filename
        
        # 準備資料
        rows = []
        for proxy in proxies:
            if isinstance(proxy, dict):
                row = {
                    'ip': proxy.get('ip'),
                    'port': proxy.get('port'),
                    'country': proxy.get('country', 'Unknown'),
                    'anonymity': proxy.get('anonymity', 'Unknown'),
                    'type': proxy.get('type', 'Unknown'),
                    'speed': proxy.get('speed', 'Unknown'),
                    'uptime': proxy.get('uptime', 'Unknown'),
                    'fetched_at': datetime.now().isoformat()
                }
            else:
                # 處理純字串格式 "ip:port"
                if isinstance(proxy, str) and ':' in proxy:
                    ip, port = proxy.split(':', 1)
                    row = {
                        'ip': ip,
                        'port': port,
                        'country': 'Unknown',
                        'anonymity': 'Unknown',
                        'type': 'Unknown',
                        'speed': 'Unknown',
                        'uptime': 'Unknown',
                        'fetched_at': datetime.now().isoformat()
                    }
                else:
                    continue  # 跳過無效格式
            
            rows.append(row)
        
        # 儲存到 CSV
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        logger.info(f"代理列表已儲存至: {filepath}")
        return str(filepath)
    
    def validate_proxy(self, ip: str, port: int, timeout: int = 10) -> Dict:
        """
        驗證單個代理的有效性
        
        Args:
            ip: 代理 IP
            port: 代理端口
            timeout: 超時時間（秒）
            
        Returns:
            驗證結果字典
        """
        proxy_url = f"http://{ip}:{port}"
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        test_url = "http://httpbin.org/ip"
        
        try:
            start_time = time.time()
            response = requests.get(test_url, proxies=proxies, timeout=timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    'ip': ip,
                    'port': port,
                    'status': 'valid',
                    'response_time': round(response_time, 2),
                    'proxy_ip': response.json().get('origin', 'unknown')
                }
            else:
                return {
                    'ip': ip,
                    'port': port,
                    'status': 'invalid',
                    'response_time': round(response_time, 2),
                    'error': f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                'ip': ip,
                'port': port,
                'status': 'failed',
                'response_time': 0,
                'error': str(e)
            }
    
    def validate_proxies_batch(self, proxies: List[Dict], max_workers: int = 50) -> List[Dict]:
        """
        批量驗證代理有效性
        
        Args:
            proxies: 代理列表
            max_workers: 最大線程數
            
        Returns:
            驗證結果列表
        """
        logger.info(f"開始驗證 {len(proxies)} 個代理...")
        
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有驗證任務
            future_to_proxy = {
                executor.submit(
                    self.validate_proxy, 
                    proxy['ip'], 
                    proxy['port']
                ): proxy 
                for proxy in proxies
            }
            
            # 收集結果
            for i, future in enumerate(as_completed(future_to_proxy), 1):
                result = future.result()
                results.append(result)
                
                # 每驗證完 10 個代理就報告一次進度
                if i % 10 == 0:
                    logger.info(f"已驗證 {i}/{len(proxies)} 個代理")
        
        # 統計結果
        valid_count = sum(1 for r in results if r['status'] == 'valid')
        logger.info(f"驗證完成！有效代理: {valid_count}/{len(proxies)} ({valid_count/len(proxies)*100:.1f}%)")
        
        return results
    
    def run_monitoring(self, interval_minutes: int = 5, max_runs: int = 100, proxy_type: str = 'all'):
        """
        運行監控模式，定期獲取代理
        
        Args:
            interval_minutes: 間隔時間（分鐘）
            max_runs: 最大運行次數
            proxy_type: 代理類型
        """
        logger.info(f"開始監控模式 - 每 {interval_minutes} 分鐘獲取一次 {proxy_type} 代理")
        
        def job():
            proxies = self.fetch_proxies(proxy_type)
            if proxies:
                filename = self.save_proxies_to_csv(proxies)
                self.print_statistics()
        
        # 立即運行一次
        job()
        
        # 設定定時任務
        schedule.every(interval_minutes).minutes.do(job)
        
        run_count = 1
        while run_count < max_runs:
            try:
                schedule.run_pending()
                time.sleep(30)  # 每30秒檢查一次
                
                if schedule.jobs and schedule.jobs[0].should_run:
                    run_count += 1
                    
            except KeyboardInterrupt:
                logger.info("監控被用戶中斷")
                break
            except Exception as e:
                logger.error(f"監控過程中發生錯誤: {e}")
                time.sleep(60)  # 發生錯誤時等待1分鐘
        
        logger.info("監控結束")
    
    def print_statistics(self):
        """列印統計資訊"""
        if len(self.history['fetch_times']) < 2:
            logger.info("資料不足，無法計算統計資訊")
            return
        
        # 計算更新間隔
        times = [datetime.fromisoformat(t) for t in self.history['fetch_times']]
        intervals = [(times[i] - times[i-1]).total_seconds() / 60 for i in range(1, len(times))]
        avg_interval = sum(intervals) / len(intervals)
        
        logger.info("=== 代理更新統計 ===")
        logger.info(f"總共獲取次數: {len(self.history['fetch_times'])}")
        logger.info(f"平均間隔時間: {avg_interval:.1f} 分鐘")
        logger.info(f"代理數量範圍: {min(self.history['proxy_counts'])} - {max(self.history['proxy_counts'])}")
        logger.info(f"平均代理數量: {sum(self.history['proxy_counts']) / len(self.history['proxy_counts']):.0f}")
        logger.info(f"累積唯一代理: {len(self.history['unique_proxies_seen'])}")
        logger.info("==================")


def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='Proxifly 免費代理 IP 測試工具')
    parser.add_argument('--test-once', action='store_true', help='單次測試獲取代理')
    parser.add_argument('--monitor', action='store_true', help='持續監控代理更新')
    parser.add_argument('--validate-proxies', action='store_true', help='驗證最新代理的有效性')
    parser.add_argument('--proxy-type', choices=['all', 'http', 'socks4', 'socks5'], 
                        default='all', help='代理類型')
    parser.add_argument('--interval', type=int, default=5, help='監控間隔時間（分鐘）')
    parser.add_argument('--max-runs', type=int, default=100, help='最大運行次數')
    
    args = parser.parse_args()
    
    tester = ProxyTester()
    
    if args.test_once:
        logger.info("執行單次代理獲取測試...")
        proxies = tester.fetch_proxies(args.proxy_type)
        if proxies:
            tester.save_proxies_to_csv(proxies)
            tester.print_statistics()
    
    elif args.monitor:
        logger.info(f"啟動監控模式 - 間隔 {args.interval} 分鐘，最多運行 {args.max_runs} 次")
        tester.run_monitoring(args.interval, args.max_runs, args.proxy_type)
    
    elif args.validate_proxies:
        logger.info("驗證最新代理有效性...")
        proxies = tester.fetch_proxies(args.proxy_type)
        if proxies:
            results = tester.validate_proxies_batch(proxies)
            
            # 儲存驗證結果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"proxy_validation_{timestamp}.csv"
            filepath = tester.data_dir / results_file
            
            pd.DataFrame(results).to_csv(filepath, index=False, encoding='utf-8-sig')
            logger.info(f"驗證結果已儲存至: {filepath}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()