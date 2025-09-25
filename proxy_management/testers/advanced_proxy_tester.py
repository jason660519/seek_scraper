"""
SEEK 爬蟲專案 - 進階代理 IP 測試工具 (支援所有國家)

此模組支援從 Proxifly 獲取所有可用國家的代理列表，
並提供 Web API 介面供前端使用。

功能特點:
- 支援 60+ 國家的代理獲取
- 提供 REST API 介面
- 支援多種代理類型 (HTTP, SOCKS4, SOCKS5)
- 自動驗證代理有效性
- 提供統計和分析功能
"""

import requests
import pandas as pd
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union
import json
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from countries import COUNTRIES
from flask import Flask, jsonify, request, render_template_string, send_from_directory
import threading

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('advanced_proxy_tester.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AdvancedProxyTester:
    def validate_proxies(self, proxies: List[Dict], max_workers: int = 20) -> Dict[str, List[Dict]]:
        """多線程驗證代理，分為有效與無效"""
        import requests
        from concurrent.futures import ThreadPoolExecutor, as_completed
        valid, invalid = [], []

        def check(proxy):
            proxy_url = f"{proxy.get('type','http')}://{proxy['ip']}:{proxy['port']}"
            try:
                resp = requests.get('http://httpbin.org/ip', proxies={'http': proxy_url, 'https': proxy_url}, timeout=5)
                if resp.status_code == 200:
                    proxy['is_working'] = True
                    return proxy, True
                else:
                    proxy['is_working'] = False
                    return proxy, False
            except Exception:
                proxy['is_working'] = False
                return proxy, False

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {executor.submit(check, p): p for p in proxies}
            for future in as_completed(future_to_proxy):
                proxy, is_valid = future.result()
                if is_valid:
                    valid.append(proxy)
                else:
                    invalid.append(proxy)
        return {'valid': valid, 'invalid': invalid}
    """進階代理 IP 測試器類別"""
    
    def __init__(self):
        """初始化代理測試器"""
        self.base_urls = {
            'all': 'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/all/data.txt',
            'http': 'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt',
            'socks4': 'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks4/data.txt',
            'socks5': 'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.txt'
        }
        
        self.country_base_url = 'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/countries'
        self.countries = COUNTRIES
        
        self.data_dir = Path("data/proxies")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 儲存歷史數據
        self.history_file = self.data_dir / "advanced_proxy_history.json"
        self.load_history()
    
    def load_history(self):
        """載入歷史記錄"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
                self.history = {
                    'fetch_times': history_data.get('fetch_times', []),
                    'proxy_counts': history_data.get('proxy_counts', []),
                    'country_stats': history_data.get('country_stats', {}),
                    'unique_proxies_seen': set(history_data.get('unique_proxies_seen', []))
                }
        else:
            self.history = {
                'fetch_times': [],
                'proxy_counts': [],
                'country_stats': {},
                'unique_proxies_seen': set()
            }
    
    def save_history(self):
        """儲存歷史記錄"""
        history_to_save = self.history.copy()
        history_to_save['unique_proxies_seen'] = list(self.history['unique_proxies_seen'])
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history_to_save, f, indent=2, ensure_ascii=False)
    
    def get_available_countries(self) -> Dict[str, str]:
        """獲取可用國家列表"""
        return self.countries.copy()
    
    def fetch_proxies_by_type(self, proxy_type: str = 'all') -> Optional[List[Dict]]:
        """
        根據類型獲取代理列表
        
        Args:
            proxy_type: 代理類型 ('all', 'http', 'socks4', 'socks5')
        
        Returns:
            代理列表或 None（如果失敗）
        """
        if proxy_type not in self.base_urls:
            logger.error(f"不支援的代理類型: {proxy_type}")
            return None
            
        url = self.base_urls[proxy_type]
        return self._fetch_from_url(url, proxy_type)
    
    def fetch_proxies_by_country(self, country_code: str) -> Optional[List[Dict]]:
        """
        根據國家獲取代理列表
        
        Args:
            country_code: 國家代碼 (如 'US', 'CN', 'JP')
        
        Returns:
            代理列表或 None（如果失敗）
        """
        if country_code.upper() not in self.countries:
            logger.error(f"不支援的國家代碼: {country_code}")
            return None
        
        country_code = country_code.upper()
        url = f"{self.country_base_url}/{country_code}/data.txt"
        
        proxies = self._fetch_from_url(url, f"country-{country_code}")
        
        # 更新國家統計
        if proxies:
            if country_code not in self.history['country_stats']:
                self.history['country_stats'][country_code] = {
                    'total_fetches': 0,
                    'total_proxies': 0,
                    'last_fetch': None
                }
            
            self.history['country_stats'][country_code]['total_fetches'] += 1
            self.history['country_stats'][country_code]['total_proxies'] += len(proxies)
            self.history['country_stats'][country_code]['last_fetch'] = datetime.now().isoformat()
            
            self.save_history()
        
        return proxies
    
    def _fetch_from_url(self, url: str, source_type: str) -> Optional[List[Dict]]:
        """從指定 URL 獲取代理"""
        try:
            logger.info(f"正在從 {source_type} 獲取代理列表...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            proxies = []
            for line in response.text.strip().split('\n'):
                if line.strip():
                    proxy_info = self._parse_proxy_line(line.strip())
                    if proxy_info:
                        proxy_info['source'] = source_type
                        proxies.append(proxy_info)
            
            logger.info(f"成功獲取 {len(proxies)} 個來自 {source_type} 的代理")
            
            # 記錄歷史
            fetch_time = datetime.now().isoformat()
            self.history['fetch_times'].append(fetch_time)
            self.history['proxy_counts'].append(len(proxies))
            
            # 追蹤唯一代理
            for proxy in proxies:
                proxy_id = f"{proxy.get('ip')}:{proxy.get('port')}"
                self.history['unique_proxies_seen'].add(proxy_id)
            
            return proxies
            
        except requests.exceptions.RequestException as e:
            logger.error(f"請求失敗: {e}")
            return None
        except Exception as e:
            logger.error(f"未預期的錯誤: {e}")
            return None
    
    def _parse_proxy_line(self, line: str) -> Optional[Dict]:
        """解析代理行"""
        try:
            if '://' in line:
                # 格式: protocol://ip:port
                protocol, address = line.split('://', 1)
                if ':' in address:
                    ip, port = address.rsplit(':', 1)
                    return {
                        'ip': ip,
                        'port': int(port) if port.isdigit() else port,
                        'type': protocol,
                        'anonymity': 'unknown',
                        'country': 'unknown',
                        'fetched_at': datetime.now().isoformat()
                    }
            elif ':' in line:
                # 格式: ip:port
                ip, port = line.rsplit(':', 1)
                return {
                    'ip': ip,
                    'port': int(port) if port.isdigit() else port,
                    'type': 'unknown',
                    'anonymity': 'unknown', 
                    'country': 'unknown',
                    'fetched_at': datetime.now().isoformat()
                }
        except Exception as e:
            logger.warning(f"解析代理行失敗: {line} - {e}")
        
        return None
    
    def fetch_multiple_countries(self, country_codes: List[str]) -> Dict[str, List[Dict]]:
        """
        批量獲取多個國家的代理
        
        Args:
            country_codes: 國家代碼列表
            
        Returns:
            國家代碼對應代理列表的字典
        """
        results = {}
        
        def fetch_country(country_code):
            proxies = self.fetch_proxies_by_country(country_code)
            return country_code, proxies
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            # 提交所有任務
            future_to_country = {
                executor.submit(fetch_country, country): country 
                for country in country_codes
            }
            
            # 收集結果
            for future in as_completed(future_to_country):
                country_code, proxies = future.result()
                results[country_code] = proxies or []
        
        return results
    
    def get_statistics(self) -> Dict:
        """獲取詳細統計資訊"""
        stats = {
            'total_fetches': len(self.history['fetch_times']),
            'total_unique_proxies': len(self.history['unique_proxies_seen']),
            'countries_accessed': len(self.history['country_stats']),
            'available_countries': len(self.countries),
            'country_stats': self.history['country_stats'].copy()
        }
        
        # 計算平均代理數量
        if self.history['proxy_counts']:
            stats['avg_proxies_per_fetch'] = sum(self.history['proxy_counts']) / len(self.history['proxy_counts'])
            stats['max_proxies_in_fetch'] = max(self.history['proxy_counts'])
            stats['min_proxies_in_fetch'] = min(self.history['proxy_counts'])
        
        # 計算時間統計
        if len(self.history['fetch_times']) >= 2:
            times = [datetime.fromisoformat(t) for t in self.history['fetch_times']]
            intervals = [(times[i] - times[i-1]).total_seconds() / 60 for i in range(1, len(times))]
            stats['avg_fetch_interval_minutes'] = sum(intervals) / len(intervals)
        
        return stats

# Flask Web API
app = Flask(__name__)
import tempfile
import csv
def save_proxies_to_csv(proxies: List[Dict]) -> str:
    """將代理列表存成臨時CSV檔，回傳檔案路徑"""
    fd, path = tempfile.mkstemp(suffix='.csv')
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['ip','port','type','source','is_working'])
        writer.writeheader()
        for p in proxies:
            writer.writerow({k: p.get(k, '') for k in ['ip','port','type','source','is_working']})
    return path
@app.route('/api/validate', methods=['POST'])
def api_validate():
    """驗證代理，分有效/無效，回傳統計"""
    proxies = request.json.get('proxies', [])
    result = proxy_tester.validate_proxies(proxies)
    return jsonify({
        'success': True,
        'valid_count': len(result['valid']),
        'invalid_count': len(result['invalid']),
        'valid': result['valid'],
        'invalid': result['invalid'],
        'all': proxies
    })

@app.route('/api/download_csv')
def api_download_csv():
    """下載有效/無效/全部代理CSV"""
    which = request.args.get('which', 'all')
    # 這裡假設前端會傳送要下載的代理清單
    import json
    proxies = json.loads(request.args.get('proxies', '[]'))
    path = save_proxies_to_csv(proxies)
    return send_from_directory(
        directory=str(Path(path).parent),
        path=Path(path).name,
        as_attachment=True,
        download_name=f'{which}_proxies_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mimetype='text/csv')
proxy_tester = AdvancedProxyTester()

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>代理 IP 抓取工具</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            padding: 30px;
            margin-bottom: 20px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #555;
        }
        
        select, button {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
        
        .results {
            margin-top: 30px;
        }
        
        .results h3 {
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        .proxy-list {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #e9ecef;
        }
        
        .proxy-item {
            background: white;
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
            font-family: 'Courier New', monospace;
        }
        
        .proxy-item:last-child {
            margin-bottom: 0;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .stat-item {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            display: block;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .loading::after {
            content: '';
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #f5c6cb;
            margin-top: 20px;
        }
        
        .success {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #c3e6cb;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 代理 IP 抓取工具</h1>
            <p>支援 60+ 國家的免費代理列表獲取</p>
        </div>
        
        <div class="card">
            <div class="grid">
                <div class="form-group">
                    <label for="proxy-type">代理類型:</label>
                    <select id="proxy-type">
                        <option value="all">所有類型</option>
                        <option value="http">HTTP</option>
                        <option value="socks4">SOCKS4</option>
                        <option value="socks5">SOCKS5</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="country">國家:</label>
                    <select id="country">
                        <option value="">選擇國家（可選）</option>
                    </select>
                </div>
            </div>
            
            <div class="form-group">
                <button id="fetch-btn" onclick="fetchProxies()">🚀 獲取代理列表</button>
            </div>
            
            <div class="form-group">
                <button id="stats-btn" onclick="getStats()">📊 查看統計資訊</button>
            </div>
        </div>
        
        <div id="results"></div>
    </div>

    <script>
        let countries = {};
        
        // 載入國家列表
        async function loadCountries() {
            try {
                const response = await fetch('/api/countries');
                countries = await response.json();
                
                const countrySelect = document.getElementById('country');
                Object.entries(countries).forEach(([code, name]) => {
                    const option = document.createElement('option');
                    option.value = code;
                    option.textContent = `${name} (${code})`;
                    countrySelect.appendChild(option);
                });
            } catch (error) {
                console.error('載入國家列表失敗:', error);
            }
        }
        
        async function fetchProxies() {
            const proxyType = document.getElementById('proxy-type').value;
            const country = document.getElementById('country').value;
            const resultsDiv = document.getElementById('results');
            const fetchBtn = document.getElementById('fetch-btn');
            
            fetchBtn.disabled = true;
            fetchBtn.textContent = '獲取中...';
            
            resultsDiv.innerHTML = '<div class="loading">正在獲取代理列表...</div>';
            
            try {
                let url = '/api/proxies';
                const params = new URLSearchParams();
                
                if (proxyType !== 'all') {
                    params.append('type', proxyType);
                }
                if (country) {
                    params.append('country', country);
                }
                
                if (params.toString()) {
                    url += '?' + params.toString();
                }
                
                const response = await fetch(url);
                const data = await response.json();
                
                if (data.success) {
                    displayResults(data.data, data.count);
                } else {
                    resultsDiv.innerHTML = `<div class="error">錯誤: ${data.error}</div>`;
                }
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">請求失敗: ${error.message}</div>`;
            } finally {
                fetchBtn.disabled = false;
                fetchBtn.textContent = '🚀 獲取代理列表';
            }
        }
        
        function displayResults(proxies, count) {
            const resultsDiv = document.getElementById('results');
            if (proxies.length === 0) {
                resultsDiv.innerHTML = '<div class="error">沒有找到代理</div>';
                return;
            }
            let html = `
                <div class="card">
                    <h3>🎯 獲取結果 (共 ${count} 個代理)</h3>
                    <div class="success">成功獲取 ${count} 個代理！</div>
                    <div class="proxy-list">
            `;
            proxies.forEach(proxy => {
                const protocol = proxy.type !== 'unknown' ? proxy.type + '://' : '';
                html += `
                    <div class="proxy-item">
                        <strong>${protocol}${proxy.ip}:${proxy.port}</strong>
                        ${proxy.type !== 'unknown' ? `<span style="margin-left: 15px; color: #666;">類型: ${proxy.type}</span>` : ''}
                        ${proxy.source ? `<span style="margin-left: 15px; color: #666;">來源: ${proxy.source}</span>` : ''}
                    </div>
                `;
            });
            html += `
                    </div>
                    <button onclick="validateProxies()" style="margin-top: 15px;">🧪 驗證代理有效性</button>
                </div>
            `;
            resultsDiv.innerHTML = html;
            window.currentProxies = proxies;
        }

        async function validateProxies() {
            if (!window.currentProxies) {
                alert('請先獲取代理列表');
                return;
            }
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<div class="loading">正在驗證代理有效性...</div>';
            try {
                const response = await fetch('/api/validate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ proxies: window.currentProxies })
                });
                const data = await response.json();
                if (data.success) {
                    displayValidationResults(data);
                } else {
                    resultsDiv.innerHTML = `<div class="error">驗證失敗: ${data.error}</div>`;
                }
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">驗證請求失敗: ${error.message}</div>`;
            }
        }

        function displayValidationResults(data) {
            const resultsDiv = document.getElementById('results');
            let html = `
                <div class="card">
                    <h3>🧪 代理有效性測試結果</h3>
                    <div class="success">有效代理: ${data.valid_count}，無效代理: ${data.invalid_count}</div>
                    <div style="margin:10px 0;">
                        <button onclick="downloadValidated('valid')">下載有效代理</button>
                        <button onclick="downloadValidated('invalid')">下載無效代理</button>
                        <button onclick="downloadValidated('all')">下載全部代理</button>
                    </div>
                    <div class="proxy-list">
                        <b>有效代理 (前10):</b><br>
                        ${data.valid.slice(0,10).map(p=>`${p.type}://${p.ip}:${p.port}`).join('<br>')}
                        <br><b>無效代理 (前10):</b><br>
                        ${data.invalid.slice(0,10).map(p=>`${p.type}://${p.ip}:${p.port}`).join('<br>')}
                    </div>
                </div>
            `;
            resultsDiv.innerHTML = html;
            window.validatedProxies = data;
        }

        function downloadValidated(which) {
            if (!window.validatedProxies) {
                alert('請先驗證代理');
                return;
            }
            let proxies = [];
            if (which === 'valid') proxies = window.validatedProxies.valid;
            else if (which === 'invalid') proxies = window.validatedProxies.invalid;
            else proxies = window.validatedProxies.all;
            const url = `/api/download_csv?which=${which}&proxies=${encodeURIComponent(JSON.stringify(proxies))}`;
            window.open(url, '_blank');
        }
        
        async function getStats() {
            const resultsDiv = document.getElementById('results');
            const statsBtn = document.getElementById('stats-btn');
            
            statsBtn.disabled = true;
            resultsDiv.innerHTML = '<div class="loading">載入統計資訊...</div>';
            
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                displayStats(stats);
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">載入統計失敗: ${error.message}</div>`;
            } finally {
                statsBtn.disabled = false;
            }
        }
        
        function displayStats(stats) {
            const resultsDiv = document.getElementById('results');
            
            let html = `
                <div class="card">
                    <h3>📊 統計資訊</h3>
                    <div class="stats">
                        <div class="stat-item">
                            <span class="stat-value">${stats.total_fetches || 0}</span>
                            <span class="stat-label">總獲取次數</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${stats.total_unique_proxies || 0}</span>
                            <span class="stat-label">唯一代理數</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${stats.countries_accessed || 0}</span>
                            <span class="stat-label">已訪問國家</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${stats.available_countries || 0}</span>
                            <span class="stat-label">可用國家</span>
                        </div>
                    </div>
            `;
            
            if (stats.country_stats && Object.keys(stats.country_stats).length > 0) {
                html += '<h4 style="margin-top: 30px; margin-bottom: 15px;">國家統計</h4>';
                html += '<div class="proxy-list">';
                
                Object.entries(stats.country_stats).forEach(([code, data]) => {
                    const countryName = countries[code] || code;
                    html += `
                        <div class="proxy-item">
                            <strong>${countryName} (${code})</strong><br>
                            <small>獲取次數: ${data.total_fetches} | 總代理數: ${data.total_proxies} | 最後獲取: ${new Date(data.last_fetch).toLocaleString()}</small>
                        </div>
                    `;
                });
                
                html += '</div>';
            }
            
            html += '</div>';
            resultsDiv.innerHTML = html;
        }
        
        function downloadCSV() {
            if (!window.currentProxies) {
                alert('沒有可下載的資料');
                return;
            }
            
            const csv = convertToCSV(window.currentProxies);
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            
            link.setAttribute('href', url);
            link.setAttribute('download', `proxies_${new Date().toISOString().slice(0,10)}.csv`);
            link.style.visibility = 'hidden';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        
        function convertToCSV(data) {
            const headers = ['ip', 'port', 'type', 'source', 'fetched_at'];
            const csvContent = [
                headers.join(','),
                ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
            ].join('\\n');
            
            return csvContent;
        }
        
        // 頁面載入完成後初始化
        document.addEventListener('DOMContentLoaded', loadCountries);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """主頁"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/countries')
def api_countries():
    """獲取可用國家列表"""
    return jsonify(proxy_tester.get_available_countries())

@app.route('/api/proxies')
def api_proxies():
    """獲取代理列表"""
    try:
        proxy_type = request.args.get('type', 'all')
        country = request.args.get('country', '').upper()
        
        if country and country in proxy_tester.countries:
            # 獲取特定國家的代理
            proxies = proxy_tester.fetch_proxies_by_country(country)
        else:
            # 獲取指定類型的代理
            proxies = proxy_tester.fetch_proxies_by_type(proxy_type)
        
        if proxies is None:
            return jsonify({
                'success': False,
                'error': '獲取代理失敗',
                'data': [],
                'count': 0
            })
        
        return jsonify({
            'success': True,
            'data': proxies,
            'count': len(proxies),
            'type': proxy_type,
            'country': country if country else None
        })
    
    except Exception as e:
        logger.error(f"API 錯誤: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': [],
            'count': 0
        }), 500

@app.route('/api/stats')
def api_stats():
    """獲取統計資訊"""
    try:
        stats = proxy_tester.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"統計 API 錯誤: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/multiple-countries')
def api_multiple_countries():
    """批量獲取多個國家的代理"""
    try:
        countries_param = request.args.get('countries', '')
        if not countries_param:
            return jsonify({
                'success': False,
                'error': '請提供國家代碼列表（用逗號分隔）',
                'data': {}
            })
        
        country_codes = [c.strip().upper() for c in countries_param.split(',')]
        results = proxy_tester.fetch_multiple_countries(country_codes)
        
        total_count = sum(len(proxies) for proxies in results.values())
        
        return jsonify({
            'success': True,
            'data': results,
            'total_count': total_count,
            'countries': len(results)
        })
    
    except Exception as e:
        logger.error(f"多國家 API 錯誤: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {}
        }), 500

def run_web_server(host='0.0.0.0', port=5000, debug=False):
    """運行 Web 伺服器"""
    logger.info(f"啟動 Web 伺服器: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)

def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='進階代理 IP 測試工具')
    parser.add_argument('--web', action='store_true', help='啟動 Web 介面')
    parser.add_argument('--port', type=int, default=5000, help='Web 伺服器端口')
    parser.add_argument('--host', default='127.0.0.1', help='Web 伺服器主機')
    
    # 現有的命令行參數
    parser.add_argument('--test-type', choices=['all', 'http', 'socks4', 'socks5'], 
                        default='all', help='測試代理類型')
    parser.add_argument('--country', help='指定國家代碼')
    parser.add_argument('--multiple-countries', help='多個國家代碼（用逗號分隔）')
    parser.add_argument('--stats', action='store_true', help='顯示統計資訊')
    
    args = parser.parse_args()
    
    if args.web:
        # 啟動 Web 介面
        run_web_server(host=args.host, port=args.port)
    elif args.stats:
        # 顯示統計資訊
        stats = proxy_tester.get_statistics()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    elif args.multiple_countries:
        # 批量獲取多個國家
        countries = [c.strip().upper() for c in args.multiple_countries.split(',')]
        results = proxy_tester.fetch_multiple_countries(countries)
        for country, proxies in results.items():
            print(f"\n{country}: {len(proxies) if proxies else 0} 個代理")
            if proxies:
                for proxy in proxies[:5]:  # 只顯示前5個
                    print(f"  {proxy['ip']}:{proxy['port']}")
    elif args.country:
        # 獲取指定國家的代理
        proxies = proxy_tester.fetch_proxies_by_country(args.country)
        if proxies:
            print(f"獲取到 {len(proxies)} 個來自 {args.country} 的代理")
            for proxy in proxies[:10]:  # 顯示前10個
                print(f"{proxy['ip']}:{proxy['port']} ({proxy['type']})")
    else:
        # 獲取指定類型的代理
        proxies = proxy_tester.fetch_proxies_by_type(args.test_type)
        if proxies:
            print(f"獲取到 {len(proxies)} 個 {args.test_type} 代理")
            for proxy in proxies[:10]:  # 顯示前10個
                print(f"{proxy['ip']}:{proxy['port']} ({proxy['type']})")

if __name__ == "__main__":
    main()