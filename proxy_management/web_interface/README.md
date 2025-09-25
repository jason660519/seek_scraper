# Proxifly 代理 IP 有效性驗證系統

一個企業級的代理 IP 有效性驗證系統，提供多層次、全方位的代理 IP 質量評估服務。

## 🌟 系統特點

- **多層次驗證體系**：連接性、性能、地理位置、匿名性、可靠性全面評估
- **智能評分算法**：基於多維度指標的智能評分與分類
- **實時監控系統**：WebSocket 實時推送測試進度和結果
- **可視化界面**：直觀的圖表展示和交互式操作界面
- **模塊化設計**：易於擴展和維護的架構設計

## 📁 項目結構

```
proxy_testing/
├── 📄 Proxifly 代理 IP 有效性驗證方法與流程.md  # 詳細技術文檔
├── 🐍 comprehensive_proxy_validator.py            # 綜合驗證器
├── 🐍 multi_layer_validation_system.py            # 多層次驗證系統
├── 🐍 geolocation_validator.py                     # 地理位置驗證器
├── 🐍 anonymity_level_tester.py                   # 匿名等級測試器
├── 🐍 reliability_tester.py                        # 可靠性測試器
├── 🌐 app.py                                       # Web 應用主程序
├── 🌐 simple_app.py                               # 簡化版 Web 應用
├── 📄 templates/
│   ├── 🌐 index.html                             # 完整版前端界面
│   └── 🌐 simple.html                            # 簡化版前端界面
├── 🚀 run_simple.py                               # 簡化版運行腳本
├── 🧪 test_validator.py                           # 測試腳本
└── 📁 data/                                       # 數據存儲目錄
    ├── 📄 proxies.json                            # 代理列表
    └── 📄 test_results.json                      # 測試結果
```

## 🚀 快速開始

### 1. 環境準備

```bash
# 創建虛擬環境
python -m venv venv

# 激活虛擬環境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 2. 運行簡化版系統

```bash
# 直接運行簡化版系統
python run_simple.py
```

系統會自動：
- ✅ 安裝必要的依賴
- ✅ 創建示例數據
- ✅ 啟動 Web 服務器
- ✅ 自動打開瀏覽器

### 3. 訪問系統

打開瀏覽器訪問：`http://localhost:5000`

## 🎯 核心功能

### 1. 多層次驗證體系

#### 🔗 基礎連接性驗證
- HTTP/HTTPS 連接測試
- TCP 端口連通性檢查
- 協議兼容性驗證

#### ⚡ 響應性能分析
- 多級響應時間檢測（快速/標準/慢速）
- 吞吐量性能測試
- 穩定性指標評估

#### 🌍 地理位置精準驗證
- 多服務交叉驗證（IP-API、IPInfo、FreeGeoIP 等）
- 地理位置共識算法
- 準確性評分系統

#### 🎭 匿名等級深度測試
- IP 洩漏檢測
- DNS 洩漏檢測
- WebRTC 洩漏檢測
- 瀏覽器指紋分析

#### 🔧 可靠性綜合評估
- 穩定性測試（長時間運行）
- 負載測試（高並發場景）
- 故障恢復能力測試
- 網絡質量評估

### 2. 智能評分系統

```python
# 評分標準
- 90-100分: 優秀（推薦使用）
- 70-89分: 良好（可以使用）
- 50-69分: 一般（謹慎使用）
- 30-49分: 較差（不建議使用）
- 0-29分: 無效（無法使用）
```

### 3. Web 管理界面

#### 📊 儀表板
- 實時統計數據展示
- 代理狀態分布圖表
- 性能評分分布圖表
- 測試進度監控

#### 🖥️ 代理管理
- 代理列表管理（增刪改查）
- 批量導入/導出功能
- 代理狀態實時更新

#### 🧪 測試中心
- 測試配置自定義
- 多層次測試選項
- 實時測試進度顯示
- 測試日誌查看

#### 📈 結果分析
- 測試結果篩選和排序
- 詳細結果展示
- 結果導出功能
- 歷史數據查詢

## 🛠️ 技術架構

### 後端技術
- **Python 3.8+**: 主要開發語言
- **Flask**: Web 框架
- **aiohttp**: 異步 HTTP 客戶端
- **dataclasses**: 數據模型定義
- **asyncio**: 異步編程支持

### 前端技術
- **HTML5 + CSS3**: 頁面結構和樣式
- **Bootstrap 5**: UI 框架
- **JavaScript (ES6+)**: 交互邏輯
- **Chart.js**: 數據可視化
- **Socket.IO**: 實時通信

### 驗證服務
- **IP-API**: 地理位置查詢
- **IPInfo**: IP 信息查詢
- **FreeGeoIP**: 免費地理位置服務
- **ExtremeIP**: IP 信息服務

## 📊 測試結果示例

```json
{
  "proxy": "http://8.8.8.8:8080",
  "status": "valid",
  "score": 85,
  "response_time": 1.23,
  "country": "United States",
  "anonymity_level": "elite",
  "errors": [],
  "tested_at": "2024-01-01T12:00:00"
}
```

## 🔧 配置選項

### 測試配置
```json
{
  "timeout": 30,           // 超時時間（秒）
  "max_retries": 3,        // 最大重試次數
  "concurrent_limit": 10, // 並發數量限制
  "tests": {
    "connectivity": true,  // 連接性測試
    "performance": true,   // 性能測試
    "geolocation": true,   // 地理位置測試
    "anonymity": true      // 匿名性測試
  }
}
```

## 🧪 開發測試

### 運行測試腳本
```bash
# 運行所有測試
python test_validator.py

# 測試特定模塊
python -m pytest tests/
```

### 代碼質量檢查
```bash
# 代碼格式化
black *.py

# 類型檢查
mypy *.py

# 代碼風格檢查
flake8 *.py
```

## 📈 性能指標

- **測試速度**: 單個代理平均測試時間 < 5秒
- **並發能力**: 支持最多 50 個並發測試
- **內存使用**: 單個測試進程 < 100MB
- **準確率**: 代理有效性判斷準確率 > 95%

## 🔒 安全特性

- **超時保護**: 防止長時間阻塞
- **錯誤處理**: 完善的異常處理機制
- **資源限制**: 內存和CPU使用限制
- **數據加密**: 敏感數據加密存儲

## 🚀 部署建議

### 開發環境
```bash
# 使用開發模式
python simple_app.py
```

### 生產環境
```bash
# 使用生產級 WSGI 服務器
gunicorn -w 4 -b 0.0.0.0:5000 simple_app:app
```

### Docker 部署
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "simple_app.py"]
```

## 🤝 貢獻指南

1. Fork 本項目
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 許可證

本項目採用 MIT 許可證 - 詳情請查看 [LICENSE](LICENSE) 文件

## 🙏 致謝

- [Proxifly](https://proxifly.dev/) - 提供免費代理服務
- [IP-API](https://ip-api.com/) - 地理位置查詢服務
- [Chart.js](https://www.chartjs.org/) - 數據可視化庫
- [Bootstrap](https://getbootstrap.com/) - UI 框架

## 📞 聯繫方式

如有問題或建議，請通過以下方式聯繫：

- 📧 郵件: your-email@example.com
- 💬 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 文檔: [項目文檔](Proxifly 代理 IP 有效性驗證方法與流程.md)

---

⭐ 如果這個項目對你有幫助，請給個 Star 支持一下！