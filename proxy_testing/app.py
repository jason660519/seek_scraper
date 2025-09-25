"""
代理 IP 驗證系統 Web 應用

這個 Flask 應用提供了一個完整的 Web 界面來管理和監控代理 IP 驗證過程。
功能包括：
1. 代理列表管理和導入
2. 多層次驗證測試
3. 實時測試進度和結果展示
4. 歷史數據分析和可視化
5. 測試報告生成和下載
6. 系統配置和監控
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from concurrent.futures import ThreadPoolExecutor
import threading
import time

from flask import Flask, render_template, request, jsonify, send_file, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# 導入我們的驗證模組
from comprehensive_proxy_validator import ComprehensiveProxyValidator, ProxyInfo
from multi_layer_validation_system import MultiLayerValidationSystem
from geolocation_validator import PrecisionGeolocationValidator
from anonymity_level_tester import AdvancedAnonymityTester
from reliability_tester import AdvancedReliabilityTester


# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 創建 Flask 應用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'proxy-testing-secret-key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局變量來存儲測試狀態和結果
test_status = {
    'is_running': False,
    'current_test': None,
    'progress': 0,
    'total_proxies': 0,
    'tested_proxies': 0,
    'results': [],
    'errors': []
}

# 測試歷史記錄
test_history = []

# 線程池執行器
executor = ThreadPoolExecutor(max_workers=4)


# ==================== 路由和視圖 ====================

@app.route('/')
def index():
    """主頁"""
    return render_template('index.html')


@app.route('/api/proxies', methods=['GET', 'POST'])
def manage_proxies():
    """管理代理列表"""
    if request.method == 'GET':
        # 獲取代理列表
        proxies = load_proxies_from_file()
        return jsonify({
            'success': True,
            'proxies': proxies,
            'count': len(proxies)
        })
    
    elif request.method == 'POST':
        # 添加代理
        data = request.get_json()
        proxy_url = data.get('proxy_url')
        
        if not proxy_url:
            return jsonify({
                'success': False,
                'error': '請提供代理地址'
            })
        
        try:
            # 解析代理地址
            proxy_info = parse_proxy_url(proxy_url)
            
            # 保存到文件
            save_proxy_to_file(proxy_info)
            
            return jsonify({
                'success': True,
                'message': '代理添加成功',
                'proxy': proxy_info
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'添加代理失敗: {str(e)}'
            })


@app.route('/api/proxies/bulk', methods=['POST'])
def bulk_import_proxies():
    """批量導入代理"""
    data = request.get_json()
    proxy_urls = data.get('proxy_urls', [])
    
    if not proxy_urls:
        return jsonify({
            'success': False,
            'error': '請提供代理地址列表'
        })
    
    try:
        imported_proxies = []
        errors = []
        
        for proxy_url in proxy_urls:
            try:
                proxy_info = parse_proxy_url(proxy_url)
                save_proxy_to_file(proxy_info)
                imported_proxies.append(proxy_info)
            except Exception as e:
                errors.append(f"{proxy_url}: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': f'成功導入 {len(imported_proxies)} 個代理',
            'imported_count': len(imported_proxies),
            'error_count': len(errors),
            'errors': errors
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'批量導入失敗: {str(e)}'
        })


@app.route('/api/test/start', methods=['POST'])
def start_test():
    """開始測試"""
    if test_status['is_running']:
        return jsonify({
            'success': False,
            'error': '測試正在進行中'
        })
    
    data = request.get_json()
    test_config = data.get('config', {})
    
    # 重置測試狀態
    test_status.update({
        'is_running': True,
        'current_test': None,
        'progress': 0,
        'total_proxies': 0,
        'tested_proxies': 0,
        'results': [],
        'errors': []
    })
    
    # 在後台線程中運行測試
    def run_test_in_background():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(run_comprehensive_test(test_config))
        except Exception as e:
            logger.error(f"測試執行失敗: {e}")
            test_status['errors'].append(str(e))
        finally:
            test_status['is_running'] = False
            loop.close()
    
    thread = threading.Thread(target=run_test_in_background)
    thread.start()
    
    return jsonify({
        'success': True,
        'message': '測試已開始'
    })


@app.route('/api/test/stop', methods=['POST'])
def stop_test():
    """停止測試"""
    if not test_status['is_running']:
        return jsonify({
            'success': False,
            'error': '沒有正在進行的測試'
        })
    
    test_status['is_running'] = False
    
    return jsonify({
        'success': True,
        'message': '測試已停止'
    })


@app.route('/api/test/status')
def get_test_status():
    """獲取測試狀態"""
    return jsonify(test_status)


@app.route('/api/test/results')
def get_test_results():
    """獲取測試結果"""
    return jsonify({
        'success': True,
        'results': test_status['results'],
        'count': len(test_status['results'])
    })


@app.route('/api/test/history')
def get_test_history():
    """獲取測試歷史"""
    return jsonify({
        'success': True,
        'history': test_history,
        'count': len(test_history)
    })


@app.route('/api/test/report/<format>')
def download_report(format):
    """下載測試報告"""
    if format not in ['json', 'csv', 'html']:
        return jsonify({
            'success': False,
            'error': '不支持的報告格式'
        })
    
    try:
        if format == 'json':
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_proxies': test_status['total_proxies'],
                    'tested_proxies': test_status['tested_proxies'],
                    'results_count': len(test_status['results'])
                },
                'results': test_status['results'],
                'errors': test_status['errors']
            }
            
            # 創建臨時文件
            filename = f"proxy_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join('reports', filename)
            os.makedirs('reports', exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            return send_file(filepath, as_attachment=True, download_name=filename)
            
        elif format == 'csv':
            import csv
            
            filename = f"proxy_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join('reports', filename)
            os.makedirs('reports', exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 寫入標題行
                if test_status['results']:
                    headers = list(test_status['results'][0].keys())
                    writer.writerow(headers)
                    
                    # 寫入數據
                    for result in test_status['results']:
                        writer.writerow([str(value) for value in result.values()])
            
            return send_file(filepath, as_attachment=True, download_name=filename)
            
        elif format == 'html':
            # 生成 HTML 報告
            html_content = generate_html_report(test_status['results'])
            
            filename = f"proxy_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = os.path.join('reports', filename)
            os.makedirs('reports', exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return send_file(filepath, as_attachment=True, download_name=filename)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'生成報告失敗: {str(e)}'
        })


@app.route('/api/config', methods=['GET', 'PUT'])
def manage_config():
    """管理系統配置"""
    config_file = 'config.json'
    
    if request.method == 'GET':
        # 獲取配置
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = get_default_config()
            
            return jsonify({
                'success': True,
                'config': config
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'讀取配置失敗: {str(e)}'
            })
    
    elif request.method == 'PUT':
        # 更新配置
        try:
            new_config = request.get_json()
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, ensure_ascii=False, indent=2)
            
            return jsonify({
                'success': True,
                'message': '配置已更新'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'更新配置失敗: {str(e)}'
            })


# ==================== WebSocket 事件 ====================

@socketio.on('connect')
def handle_connect():
    """客戶端連接"""
    logger.info("客戶端已連接")
    emit('connected', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """客戶端斷開連接"""
    logger.info("客戶端已斷開連接")


@socketio.on('request_status_update')
def handle_status_request():
    """請求狀態更新"""
    emit('status_update', test_status)


# ==================== 輔助函數 ====================

def get_default_config():
    """獲取默認配置"""
    return {
        'validation': {
            'timeout': 30,
            'max_retries': 3,
            'concurrent_limit': 10
        },
        'tests': {
            'connectivity': True,
            'performance': True,
            'geolocation': True,
            'anonymity': True,
            'reliability': True
        },
        'reliability': {
            'stability_test_duration': 180,
            'load_concurrent_requests': 50,
            'network_ping_count': 100
        },
        'output': {
            'save_csv': True,
            'save_json': True,
            'generate_html_report': True
        }
    }


def parse_proxy_url(proxy_url: str) -> Dict[str, str]:
    """解析代理 URL"""
    from urllib.parse import urlparse
    
    parsed = urlparse(proxy_url)
    
    return {
        'ip': parsed.hostname,
        'port': str(parsed.port),
        'protocol': parsed.scheme,
        'username': parsed.username or '',
        'password': parsed.password or '',
        'url': proxy_url,
        'added_time': datetime.now().isoformat()
    }


def load_proxies_from_file() -> List[Dict[str, str]]:
    """從文件加載代理"""
    proxy_file = 'proxies.json'
    
    if os.path.exists(proxy_file):
        try:
            with open(proxy_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加載代理文件失敗: {e}")
            return []
    
    return []


def save_proxy_to_file(proxy_info: Dict[str, str]) -> None:
    """保存代理到文件"""
    proxy_file = 'proxies.json'
    
    # 加載現有代理
    proxies = load_proxies_from_file()
    
    # 檢查是否已存在
    existing = next((p for p in proxies if p['url'] == proxy_info['url']), None)
    if existing:
        return
    
    # 添加新代理
    proxies.append(proxy_info)
    
    # 保存到文件
    with open(proxy_file, 'w', encoding='utf-8') as f:
        json.dump(proxies, f, ensure_ascii=False, indent=2)


async def run_comprehensive_test(test_config: Dict[str, Any]):
    """運行綜合測試"""
    try:
        # 加載代理
        proxies = load_proxies_from_file()
        if not proxies:
            test_status['errors'].append("沒有可測試的代理")
            return
        
        test_status['total_proxies'] = len(proxies)
        
        # 創建驗證器
        validator = ComprehensiveProxyValidator()
        
        # 運行測試
        for i, proxy_info in enumerate(proxies):
            if not test_status['is_running']:
                break
            
            test_status['current_test'] = f"正在測試: {proxy_info['ip']}:{proxy_info['port']}"
            test_status['tested_proxies'] = i + 1
            test_status['progress'] = int((i + 1) / len(proxies) * 100)
            
            try:
                # 創建代理字典
                proxy_dict = {
                    'http': proxy_info['url'],
                    'https': proxy_info['url']
                }
                
                # 運行驗證
                result = await validator.validate_proxy(proxy_dict)
                
                # 保存結果
                test_status['results'].append({
                    'proxy': f"{proxy_info['ip']}:{proxy_info['port']}",
                    'status': result.overall_status,
                    'score': result.overall_score,
                    'connectivity_score': result.connectivity_score,
                    'performance_score': result.performance_score,
                    'anonymity_score': result.anonymity_score,
                    'reliability_score': result.reliability_score,
                    'response_time': result.response_time,
                    'country': result.country,
                    'city': result.city,
                    'anonymity_level': result.anonymity_level,
                    'test_timestamp': result.test_timestamp,
                    'errors': result.errors
                })
                
            except Exception as e:
                test_status['errors'].append(f"測試 {proxy_info['url']} 失敗: {str(e)}")
            
            # 發送狀態更新
            socketio.emit('status_update', test_status)
            
            # 等待一段時間避免過快
            await asyncio.sleep(0.5)
        
        # 保存測試歷史
        test_history.append({
            'timestamp': datetime.now().isoformat(),
            'total_proxies': test_status['total_proxies'],
            'tested_proxies': test_status['tested_proxies'],
            'results': test_status['results'],
            'errors': test_status['errors']
        })
        
        logger.info("測試完成")
        
    except Exception as e:
        logger.error(f"測試過程錯誤: {e}")
        test_status['errors'].append(str(e))


def generate_html_report(results: List[Dict[str, Any]]) -> str:
    """生成 HTML 報告"""
    html_template = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>代理 IP 測試報告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f4f4f4; padding: 20px; border-radius: 5px; }
        .summary { margin: 20px 0; }
        .results { margin-top: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .status-valid { color: green; font-weight: bold; }
        .status-invalid { color: red; font-weight: bold; }
        .score-high { color: green; }
        .score-medium { color: orange; }
        .score-low { color: red; }
    </style>
</head>
<body>
    <div class="header">
        <h1>代理 IP 測試報告</h1>
        <p>生成時間: {timestamp}</p>
    </div>
    
    <div class="summary">
        <h2>測試摘要</h2>
        <p>總代理數: {total_proxies}</p>
        <p>有效代理: {valid_count}</p>
        <p>無效代理: {invalid_count}</p>
    </div>
    
    <div class="results">
        <h2>詳細結果</h2>
        <table>
            <thead>
                <tr>
                    <th>代理地址</th>
                    <th>狀態</th>
                    <th>總分</th>
                    <th>連接性</th>
                    <th>性能</th>
                    <th>匿名性</th>
                    <th>可靠性</th>
                    <th>響應時間</th>
                    <th>地理位置</th>
                    <th>錯誤信息</th>
                </tr>
            </thead>
            <tbody>
                {result_rows}
            </tbody>
        </table>
    </div>
</body>
</html>
    """
    
    # 統計信息
    valid_count = sum(1 for r in results if r['status'] == 'valid')
    invalid_count = sum(1 for r in results if r['status'] != 'valid')
    
    # 生成結果行
    result_rows = ""
    for result in results:
        status_class = "status-valid" if result['status'] == 'valid' else "status-invalid"
        
        # 分數樣式
        score_class = "score-high" if result['score'] >= 80 else "score-medium" if result['score'] >= 60 else "score-low"
        
        row = f"""
        <tr>
            <td>{result['proxy']}</td>
            <td class="{status_class}">{result['status']}</td>
            <td class="{score_class}">{result['score']}</td>
            <td>{result['connectivity_score']}</td>
            <td>{result['performance_score']}</td>
            <td>{result['anonymity_score']}</td>
            <td>{result['reliability_score']}</td>
            <td>{result['response_time']:.2f}s</td>
            <td>{result['country']} - {result['city']}</td>
            <td>{'<br>'.join(result['errors']) if result['errors'] else '-'}</td>
        </tr>
        """
        result_rows += row
    
    # 填充模板
    html_content = html_template.format(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_proxies=len(results),
        valid_count=valid_count,
        invalid_count=invalid_count,
        result_rows=result_rows
    )
    
    return html_content


# ==================== 主函數 ====================

if __name__ == '__main__':
    # 創建必要的目錄
    os.makedirs('reports', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # 啟動應用
    logger.info("啟動代理 IP 驗證系統 Web 應用")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)