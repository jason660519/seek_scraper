#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版代理IP驗證系統 Web應用程序
用於快速測試和演示基本功能
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
import threading
import time
import random

app = Flask(__name__)
CORS(app)

# 數據存儲路徑
DATA_DIR = "data"
PROXIES_FILE = os.path.join(DATA_DIR, "proxies.json")
RESULTS_FILE = os.path.join(DATA_DIR, "test_results.json")

# 確保數據目錄存在
os.makedirs(DATA_DIR, exist_ok=True)

# 初始化數據文件
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

# 全局變量
testing_status = {
    "is_running": False,
    "progress": 0,
    "current_proxy": "",
    "total_tests": 0,
    "completed_tests": 0
}

@app.route('/')
def index():
    """主頁面"""
    return render_template('simple.html')

@app.route('/api/status')
def get_status():
    """獲取系統狀態"""
    return jsonify({
        "status": "running",
        "version": "1.0.0",
        "testing": testing_status["is_running"]
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
            time.sleep(1)
            
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
        
        with open(PROXIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(proxies, f, ensure_ascii=False, indent=2)
        
    except Exception as e:
        print(f"測試過程出錯: {e}")
    
    finally:
        testing_status["is_running"] = False
        testing_status["progress"] = 0
        testing_status["current_proxy"] = ""

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
    thread.start()
    
    return jsonify({"message": "測試已啟動"})

@app.route('/api/test/stop', methods=['POST'])
def stop_testing():
    """停止測試"""
    testing_status["is_running"] = False
    return jsonify({"message": "測試已停止"})

@app.route('/api/test/status')
def get_test_status():
    """獲取測試狀態"""
    return jsonify(testing_status)

@app.route('/api/results')
def get_results():
    """獲取測試結果"""
    try:
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/import', methods=['POST'])
def import_proxies():
    """批量導入代理"""
    try:
        data = request.json
        proxy_list = data.get("proxies", [])
        
        with open(PROXIES_FILE, 'r', encoding='utf-8') as f:
            proxies = json.load(f)
        
        # 生成起始ID
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
        
        with open(PROXIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(proxies, f, ensure_ascii=False, indent=2)
        
        return jsonify({"message": f"成功導入 {len(proxy_list)} 個代理"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 初始化數據文件
    init_data_files()
    
    print("🚀 啟動代理IP驗證系統...")
    print("🌐 訪問地址: http://localhost:5000")
    print("📊 API 端點:")
    print("  - GET  /api/status     : 系統狀態")
    print("  - GET  /api/proxies    : 代理列表")
    print("  - POST /api/proxies    : 添加代理")
    print("  - POST /api/test/start : 開始測試")
    print("  - GET  /api/results    : 測試結果")
    
    app.run(host='0.0.0.0', port=5000, debug=True)