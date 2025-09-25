#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復版代理IP驗證系統 Web應用程序
簡化依賴，增強穩定性
"""

from flask import Flask, render_template_string, jsonify, request
import json
import os
import threading
import time
import random
from datetime import datetime

app = Flask(__name__)

# 數據存儲路徑
DATA_DIR = "data"
PROXIES_FILE = os.path.join(DATA_DIR, "proxies.json")
RESULTS_FILE = os.path.join(DATA_DIR, "test_results.json")

# 確保數據目錄存在
os.makedirs(DATA_DIR, exist_ok=True)

# 全局變量
testing_status = {
    "is_running": False,
    "progress": 0,
    "current_proxy": "",
    "total_tests": 0,
    "completed_tests": 0
}

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>代理IP驗證系統</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .status-card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .progress-bar { width: 100%; height: 20px; background: #ecf0f1; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background: #3498db; transition: width 0.3s ease; }
        .proxy-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .proxy-table th, .proxy-table td { padding: 12px; text-align: left; border-bottom: 1px solid #ecf0f1; }
        .proxy-table th { background-color: #34495e; color: white; }
        .btn { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        .btn-primary { background: #3498db; color: white; }
        .btn-success { background: #27ae60; color: white; }
        .btn-danger { background: #e74c3c; color: white; }
        .status-valid { color: #27ae60; font-weight: bold; }
        .status-invalid { color: #e74c3c; font-weight: bold; }
        .status-unknown { color: #95a5a6; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 代理IP驗證系統</h1>
            <p>系統狀態: <span id="system-status">檢測中...</span></p>
        </div>
        
        <div class="status-card">
            <h2>📊 測試狀態</h2>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <span>測試進度: <span id="progress-text">0%</span></span>
                <span>當前代理: <span id="current-proxy">無</span></span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="progress-bar" style="width: 0%"></div>
            </div>
            <div style="margin-top: 15px;">
                <button class="btn btn-success" onclick="startTesting()">🚀 開始測試</button>
                <button class="btn btn-danger" onclick="stopTesting()">⏹️ 停止測試</button>
                <button class="btn btn-primary" onclick="refreshData()">🔄 刷新數據</button>
            </div>
        </div>
        
        <div class="status-card">
            <h2>🌐 代理列表</h2>
            <table class="proxy-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>IP地址</th>
                        <th>端口</th>
                        <th>協議</th>
                        <th>國家</th>
                        <th>狀態</th>
                        <th>評分</th>
                        <th>最後測試</th>
                    </tr>
                </thead>
                <tbody id="proxy-tbody">
                    <tr><td colspan="8" style="text-align: center; color: #95a5a6;">加載中...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // 獲取系統狀態
        async function getSystemStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                document.getElementById('system-status').textContent = data.testing ? '測試中' : '待機中';
                return data;
            } catch (error) {
                document.getElementById('system-status').textContent = '連接失敗';
                console.error('獲取系統狀態失敗:', error);
            }
        }

        // 獲取代理列表
        async function getProxies() {
            try {
                const response = await fetch('/api/proxies');
                const proxies = await response.json();
                displayProxies(proxies);
            } catch (error) {
                console.error('獲取代理列表失敗:', error);
            }
        }

        // 顯示代理列表
        function displayProxies(proxies) {
            const tbody = document.getElementById('proxy-tbody');
            if (proxies.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #95a5a6;">暫無代理數據</td></tr>';
                return;
            }
            
            tbody.innerHTML = proxies.map(proxy => `
                <tr>
                    <td>${proxy.id}</td>
                    <td>${proxy.ip}</td>
                    <td>${proxy.port}</td>
                    <td>${proxy.protocol}</td>
                    <td>${proxy.country}</td>
                    <td class="status-${proxy.status}">${getStatusText(proxy.status)}</td>
                    <td>${proxy.score || 0}</td>
                    <td>${formatDate(proxy.last_tested)}</td>
                </tr>
            `).join('');
        }

        // 獲取狀態文本
        function getStatusText(status) {
            const statusMap = {
                'valid': '有效',
                'invalid': '無效',
                'unknown': '未知'
            };
            return statusMap[status] || status;
        }

        // 格式化日期
        function formatDate(dateString) {
            if (!dateString) return '從未';
            const date = new Date(dateString);
            return date.toLocaleString('zh-CN');
        }

        // 開始測試
        async function startTesting() {
            try {
                const response = await fetch('/api/test/start', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({})
                });
                const result = await response.json();
                if (result.message) {
                    alert(result.message);
                }
            } catch (error) {
                console.error('開始測試失敗:', error);
                alert('開始測試失敗');
            }
        }

        // 停止測試
        async function stopTesting() {
            testing = false;
            alert('測試已停止');
        }

        // 刷新數據
        function refreshData() {
            getSystemStatus();
            getProxies();
        }

        // 定期更新
        setInterval(() => {
            getSystemStatus();
            getProxies();
        }, 5000);

        // 頁面加載時初始化
        document.addEventListener('DOMContentLoaded', function() {
            refreshData();
        });
    </script>
</body>
</html>
"""

def init_data_files():
    """初始化數據文件"""
    if not os.path.exists(PROXIES_FILE):
        sample_proxies = [
            {
                "id": 1,
                "ip": "8.8.8.8",
                "port": 8080,
                "protocol": "http",
                "country": "United States",
                "status": "unknown",
                "score": 0,
                "last_tested": None,
                "username": "",
                "password": ""
            },
            {
                "id": 2,
                "ip": "1.1.1.1",
                "port": 3128,
                "protocol": "https",
                "country": "United States",
                "status": "unknown",
                "score": 0,
                "last_tested": None,
                "username": "",
                "password": ""
            }
        ]
        with open(PROXIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(sample_proxies, f, ensure_ascii=False, indent=2)
    
    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def simulate_testing():
    """模擬測試過程"""
    global testing_status
    
    try:
        with open(PROXIES_FILE, 'r', encoding='utf-8') as f:
            proxies = json.load(f)
        
        if not proxies:
            testing_status["is_running"] = False
            return
        
        testing_status["total_tests"] = len(proxies)
        testing_status["completed_tests"] = 0
        
        results = []
        
        for i, proxy in enumerate(proxies):
            if not testing_status["is_running"]:
                break
            
            testing_status["current_proxy"] = f"{proxy['ip']}:{proxy['port']}"
            testing_status["progress"] = int((i + 1) / len(proxies) * 100)
            testing_status["completed_tests"] = i + 1
            
            # 模擬測試延遲
            time.sleep(0.5)
            
            # 模擬測試結果
            score = random.randint(30, 95)
            status = "valid" if score > 60 else "invalid"
            
            result = {
                "proxy_id": proxy["id"],
                "ip": proxy["ip"],
                "port": proxy["port"],
                "status": status,
                "score": score,
                "response_time": round(random.uniform(0.5, 3.0), 2),
                "country": proxy.get("country", "Unknown"),
                "anonymity_level": random.choice(["elite", "anonymous", "transparent"]),
                "tested_at": datetime.now().isoformat(),
                "errors": []
            }
            
            results.append(result)
            
            # 更新代理狀態
            proxy["status"] = status
            proxy["score"] = score
            proxy["last_tested"] = result["tested_at"]
        
        # 保存結果
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 更新代理文件
        with open(PROXIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(proxies, f, ensure_ascii=False, indent=2)
        
    except Exception as e:
        print(f"測試錯誤: {e}")
    finally:
        testing_status["is_running"] = False
        testing_status["progress"] = 0
        testing_status["current_proxy"] = ""

@app.route('/')
def index():
    """主頁面"""
    return HTML_TEMPLATE

@app.route('/api/status')
def get_status():
    """獲取系統狀態"""
    return jsonify({
        "status": "running",
        "version": "1.0.0",
        "testing": testing_status["is_running"],
        "progress": testing_status["progress"],
        "current_proxy": testing_status["current_proxy"],
        "total_tests": testing_status["total_tests"],
        "completed_tests": testing_status["completed_tests"]
    })

@app.route('/api/proxies')
def get_proxies():
    """獲取代理列表"""
    try:
        with open(PROXIES_FILE, 'r', encoding='utf-8') as f:
            proxies = json.load(f)
        return jsonify(proxies)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/proxies', methods=['POST'])
def add_proxy():
    """添加代理"""
    try:
        data = request.json
        
        with open(PROXIES_FILE, 'r', encoding='utf-8') as f:
            proxies = json.load(f)
        
        # 生成新ID
        new_id = max([p.get("id", 0) for p in proxies]) + 1 if proxies else 1
        
        new_proxy = {
            "id": new_id,
            "ip": data.get("ip", ""),
            "port": data.get("port", 80),
            "protocol": data.get("protocol", "http"),
            "country": data.get("country", "Unknown"),
            "status": "unknown",
            "score": 0,
            "last_tested": None,
            "username": data.get("username", ""),
            "password": data.get("password", "")
        }
        
        proxies.append(new_proxy)
        
        with open(PROXIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(proxies, f, ensure_ascii=False, indent=2)
        
        return jsonify({"message": "代理添加成功", "id": new_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/proxies/<int:proxy_id>', methods=['DELETE'])
def delete_proxy(proxy_id):
    """刪除代理"""
    try:
        with open(PROXIES_FILE, 'r', encoding='utf-8') as f:
            proxies = json.load(f)
        
        proxies = [p for p in proxies if p["id"] != proxy_id]
        
        with open(PROXIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(proxies, f, ensure_ascii=False, indent=2)
        
        return jsonify({"message": "代理刪除成功"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test/start', methods=['POST'])
def start_testing():
    """開始測試"""
    if testing_status["is_running"]:
        return jsonify({"error": "測試正在進行中"}), 400
    
    testing_status["is_running"] = True
    testing_status["progress"] = 0
    testing_status["current_proxy"] = ""
    testing_status["total_tests"] = 0
    testing_status["completed_tests"] = 0
    
    # 啟動測試線程
    thread = threading.Thread(target=simulate_testing)
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "測試已啟動"})

@app.route('/api/results')
def get_results():
    """獲取測試結果"""
    try:
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 初始化數據文件
    init_data_files()
    
    print("🚀 代理IP驗證系統已啟動")
    print("🌐 訪問地址: http://localhost:5000")
    print("📊 API 端點:")
    print("  - GET  /api/status     : 系統狀態")
    print("  - GET  /api/proxies    : 代理列表")
    print("  - POST /api/proxies    : 添加代理")
    print("  - POST /api/test/start : 開始測試")
    print("  - GET  /api/results    : 測試結果")
    print("\n📝 提示: 按 Ctrl+C 停止服務器")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 正在關閉服務器...")