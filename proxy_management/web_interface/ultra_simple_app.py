#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
極簡版代理IP驗證系統 Web應用程序
使用內置庫，無需額外安裝依賴
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import urllib.parse
from datetime import datetime
import threading
import time
import random
import socketserver

# 全局變量
proxies = [
    {"id": 1, "ip": "8.8.8.8", "port": 8080, "protocol": "http", "country": "United States", "status": "unknown", "score": 0, "last_tested": None},
    {"id": 2, "ip": "1.1.1.1", "port": 3128, "protocol": "https", "country": "United States", "status": "unknown", "score": 0, "last_tested": None}
]

test_results = []
testing_status = {
    "is_running": False,
    "progress": 0,
    "current_proxy": "",
    "total_tests": 0,
    "completed_tests": 0
}

class ProxyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        """處理GET請求"""
        if self.path == '/':
            self.serve_index()
        elif self.path == '/api/status':
            self.serve_status()
        elif self.path == '/api/proxies':
            self.serve_proxies()
        elif self.path == '/api/results':
            self.serve_results()
        elif self.path == '/api/test/status':
            self.serve_test_status()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """處理POST請求"""
        if self.path == '/api/proxies':
            self.add_proxy()
        elif self.path == '/api/test/start':
            self.start_testing()
        elif self.path == '/api/test/stop':
            self.stop_testing()
        elif self.path == '/api/import':
            self.import_proxies()
        else:
            self.send_error(404)
    
    def do_DELETE(self):
        """處理DELETE請求"""
        if self.path.startswith('/api/proxies/'):
            self.delete_proxy()
        else:
            self.send_error(404)
    
    def serve_index(self):
        """提供主頁面"""
        html_content = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>代理IP驗證系統</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; margin-bottom: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #2980b9; }
        .btn-success { background: #27ae60; }
        .btn-danger { background: #e74c3c; }
        .proxy-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #eee; }
        .proxy-status { padding: 4px 8px; border-radius: 4px; font-size: 12px; }
        .status-valid { background: #27ae60; color: white; }
        .status-invalid { background: #e74c3c; color: white; }
        .status-unknown { background: #95a5a6; color: white; }
        .progress-bar { width: 100%; height: 20px; background: #ecf0f1; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .progress-fill { height: 100%; background: #3498db; transition: width 0.3s; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #3498db; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 代理IP驗證系統</h1>
        <p>企業級代理IP有效性驗證平台</p>
    </div>
    
    <div class="container">
        <!-- 統計信息 -->
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="total-proxies">0</div>
                <div>總代理數</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="valid-proxies">0</div>
                <div>有效代理</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="test-status">待機</div>
                <div>測試狀態</div>
            </div>
        </div>
        
        <!-- 控制面板 -->
        <div class="card">
            <h2>🎮 控制面板</h2>
            <button class="btn btn-success" onclick="startTesting()">開始測試</button>
            <button class="btn btn-danger" onclick="stopTesting()">停止測試</button>
            <button class="btn" onclick="loadProxies()">刷新列表</button>
            
            <div class="progress-bar" id="progress-container" style="display: none;">
                <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
            </div>
            <div id="current-test" style="margin-top: 10px; font-size: 14px; color: #666;"></div>
        </div>
        
        <!-- 代理列表 -->
        <div class="card">
            <h2>📋 代理列表</h2>
            <div id="proxy-list"></div>
        </div>
        
        <!-- 測試結果 -->
        <div class="card">
            <h2>📊 測試結果</h2>
            <div id="test-results"></div>
        </div>
    </div>

    <script>
        // 加載代理列表
        function loadProxies() {
            fetch('/api/proxies')
                .then(response => response.json())
                .then(data => {
                    displayProxies(data);
                    updateStats(data);
                })
                .catch(error => console.error('Error loading proxies:', error));
        }
        
        // 顯示代理列表
        function displayProxies(proxies) {
            const container = document.getElementById('proxy-list');
            container.innerHTML = '';
            
            proxies.forEach(proxy => {
                const item = document.createElement('div');
                item.className = 'proxy-item';
                
                const statusClass = proxy.status === 'valid' ? 'status-valid' : 
                                  proxy.status === 'invalid' ? 'status-invalid' : 'status-unknown';
                
                item.innerHTML = `
                    <div>
                        <strong>${proxy.ip}:${proxy.port}</strong>
                        <span style="margin-left: 10px; color: #666;">${proxy.protocol}</span>
                    </div>
                    <div>
                        <span class="proxy-status ${statusClass}">${proxy.status || 'unknown'}</span>
                        <span style="margin-left: 10px;">評分: ${proxy.score || 0}</span>
                    </div>
                `;
                
                container.appendChild(item);
            });
        }
        
        // 更新統計信息
        function updateStats(proxies) {
            document.getElementById('total-proxies').textContent = proxies.length;
            document.getElementById('valid-proxies').textContent = 
                proxies.filter(p => p.status === 'valid').length;
        }
        
        // 開始測試
        function startTesting() {
            fetch('/api/test/start', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    console.log('Testing started:', data);
                    document.getElementById('test-status').textContent = '測試中';
                    document.getElementById('progress-container').style.display = 'block';
                    checkTestStatus();
                })
                .catch(error => console.error('Error starting test:', error));
        }
        
        // 停止測試
        function stopTesting() {
            fetch('/api/test/stop', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    console.log('Testing stopped:', data);
                    document.getElementById('test-status').textContent = '已停止';
                    document.getElementById('progress-container').style.display = 'none';
                })
                .catch(error => console.error('Error stopping test:', error));
        }
        
        // 檢查測試狀態
        function checkTestStatus() {
            fetch('/api/test/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('progress-fill').style.width = data.progress + '%';
                    document.getElementById('current-test').textContent = 
                        data.current_proxy ? `正在測試: ${data.current_proxy}` : '';
                    
                    if (data.is_running) {
                        setTimeout(checkTestStatus, 1000);
                    } else {
                        document.getElementById('test-status').textContent = '完成';
                        document.getElementById('progress-container').style.display = 'none';
                        loadResults();
                        loadProxies();
                    }
                })
                .catch(error => console.error('Error checking test status:', error));
        }
        
        // 加載測試結果
        function loadResults() {
            fetch('/api/results')
                .then(response => response.json())
                .then(data => {
                    displayResults(data);
                })
                .catch(error => console.error('Error loading results:', error));
        }
        
        // 顯示測試結果
        function displayResults(results) {
            const container = document.getElementById('test-results');
            container.innerHTML = '';
            
            if (results.length === 0) {
                container.innerHTML = '<p style="color: #666;">暫無測試結果</p>';
                return;
            }
            
            results.forEach(result => {
                const item = document.createElement('div');
                item.className = 'proxy-item';
                item.style.marginBottom = '10px';
                
                const statusClass = result.status === 'valid' ? 'status-valid' : 'status-invalid';
                
                item.innerHTML = `
                    <div>
                        <strong>${result.ip}:${result.port}</strong>
                        <div style="font-size: 12px; color: #666;">
                            響應時間: ${result.response_time}s | 國家: ${result.country}
                        </div>
                    </div>
                    <div>
                        <span class="proxy-status ${statusClass}">${result.status}</span>
                        <span style="margin-left: 10px;">評分: ${result.score}</span>
                    </div>
                `;
                
                container.appendChild(item);
            });
        }
        
        // 頁面加載時初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadProxies();
            loadResults();
        });
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def serve_status(self):
        """提供系統狀態"""
        status = {
            "status": "running",
            "version": "1.0.0",
            "testing": testing_status["is_running"]
        }
        self.send_json_response(status)
    
    def serve_proxies(self):
        """提供代理列表"""
        self.send_json_response(proxies)
    
    def serve_results(self):
        """提供測試結果"""
        self.send_json_response(test_results)
    
    def serve_test_status(self):
        """提供測試狀態"""
        self.send_json_response(testing_status)
    
    def add_proxy(self):
        """添加代理"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
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
        self.send_json_response({"message": "代理添加成功", "id": new_id})
    
    def delete_proxy(self):
        """刪除代理"""
        proxy_id = int(self.path.split('/')[-1])
        global proxies
        proxies = [p for p in proxies if p["id"] != proxy_id]
        self.send_json_response({"message": "代理刪除成功"})
    
    def start_testing(self):
        """開始測試"""
        if testing_status["is_running"]:
            self.send_json_response({"error": "測試正在進行中"}, 400)
            return
        
        testing_status["is_running"] = True
        testing_status["progress"] = 0
        testing_status["current_proxy"] = ""
        testing_status["total_tests"] = len(proxies)
        testing_status["completed_tests"] = 0
        
        # 啟動測試線程
        thread = threading.Thread(target=simulate_testing)
        thread.start()
        
        self.send_json_response({"message": "測試已啟動"})
    
    def stop_testing(self):
        """停止測試"""
        testing_status["is_running"] = False
        self.send_json_response({"message": "測試已停止"})
    
    def import_proxies(self):
        """批量導入代理"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        proxy_list = data.get("proxies", [])
        
        start_id = max([p.get("id", 0) for p in proxies]) + 1 if proxies else 1
        
        for i, proxy_data in enumerate(proxy_list):
            new_proxy = {
                "id": start_id + i,
                "ip": proxy_data.get("ip", ""),
                "port": proxy_data.get("port", 80),
                "protocol": proxy_data.get("protocol", "http"),
                "country": proxy_data.get("country", "Unknown"),
                "status": "unknown",
                "score": 0,
                "last_tested": None,
                "username": proxy_data.get("username", ""),
                "password": proxy_data.get("password", "")
            }
            proxies.append(new_proxy)
        
        self.send_json_response({"message": f"成功導入 {len(proxy_list)} 個代理"})
    
    def send_json_response(self, data, status=200):
        """發送JSON響應"""
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

def simulate_testing():
    """模擬測試過程"""
    global test_results
    
    try:
        if not proxies:
            testing_status["is_running"] = False
            return
        
        test_results = []
        
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
            
            test_results.append(result)
            
            # 更新代理狀態
            proxy["status"] = status
            proxy["score"] = score
            proxy["last_tested"] = result["tested_at"]
        
    except Exception as e:
        print(f"測試過程出錯: {e}")
    
    finally:
        testing_status["is_running"] = False
        testing_status["progress"] = 0
        testing_status["current_proxy"] = ""

def run_server():
    """運行Web服務器"""
    port = 5000
    handler = ProxyHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🚀 代理IP驗證系統已啟動")
        print(f"🌐 訪問地址: http://localhost:{port}")
        print(f"📊 API 端點:")
        print(f"  - GET  /api/status     : 系統狀態")
        print(f"  - GET  /api/proxies    : 代理列表")
        print(f"  - POST /api/proxies    : 添加代理")
        print(f"  - POST /api/test/start : 開始測試")
        print(f"  - GET  /api/results    : 測試結果")
        print("\n📝 提示: 按 Ctrl+C 停止服務器")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 正在關閉服務器...")
            httpd.shutdown()

if __name__ == '__main__':
    run_server()