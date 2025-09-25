# 🔍 Seek Job Crawler & Proxy Management System

> 一個專業的求職爬蟲系統，整合智能代理管理與雲端定時任務

## 📋 目錄

- [系統概述](#系統概述)
- [代理管理系統](#代理管理系統)
- [檔案結構說明](#檔案結構說明)
- [使用指南](#使用指南)
- [GitHub Actions 自動化](#github-actions-自動化)
- [驗證機制](#驗證機制)
- [開發環境設定](#開發環境設定)

---

## 🎯 系統概述

本系統包含兩個主要功能模組：

1. **求職爬蟲系統** - 自動抓取各大求職網站職缺資訊
2. **代理管理系統** - 智能代理 IP 收集、驗證與管理

### ✨ 主要特性

- 🔄 **全自動運行**：GitHub Actions 每小時自動執行
- 🌍 **全球代理**：支援 HTTP/HTTPS/SOCKS4/SOCKS5 協議
- ⚡ **智能驗證**：多層次代理驗證機制
- 📊 **統計報告**：完整的執行報告與統計數據
- 🗃️ **歷史追蹤**：自動存檔歷史數據
- 🔧 **易於擴展**：模組化設計，易於添加新功能

---

## 🚀 代理管理系統

### 📁 代理檔案匯出目錄結構

```
proxy_management/exports/
├── 📁 working-proxies/          # 高品質已驗證代理
│   ├── working_proxies.csv     # 主要工作代理清單
│   ├── best_proxies.json       # 最佳代理 JSON 格式
│   ├── best_proxies.txt        # 最佳代理文字格式
│   └── README.md               # 詳細使用說明
├── 📁 proxy-lists/              # 原始代理列表
│   ├── all.txt                 # 所有類型代理
│   ├── http.txt                # HTTP 代理
│   ├── socks4.txt              # SOCKS4 代理
│   ├── socks5.txt              # SOCKS5 代理
│   └── us_proxies.txt          # 美國地區代理
└── README.md                    # 本目錄使用說明
```

### 🎯 代理品質分類

#### 🟢 工作代理 (Working Proxies)
- **可用率**: >95%
- **驗證狀態**: 已通過多層次驗證
- **回應時間**: <2000ms
- **更新頻率**: 每小時更新
- **使用建議**: 生產環境、重要任務

#### 🟡 原始代理 (Raw Proxy Lists)
- **來源**: Proxifly 免費代理 API
- **驗證狀態**: 未經驗證
- **數量**: 大量 (>1000個)
- **使用建議**: 自行驗證、測試用途

---

## 📊 檔案格式說明

### CSV 格式 (working_proxies.csv)
```
IP:PORT,代理類型,回應時間(ms),國家代碼,代理URL
192.168.1.100:8080,HTTP,1500,US,http://192.168.1.100:8080
10.0.0.50:3128,SOCKS5,800,GB,socks5://10.0.0.50:3128
```

### JSON 格式 (best_proxies.json)
```json
{
  "proxy": "192.168.1.100:8080",
  "type": "HTTP",
  "response_time": 1500,
  "country": "US",
  "anonymity": "Elite",
  "last_verified": "2025-09-26T10:30:00Z"
}
```

### TXT 格式 (best_proxies.txt)
```
192.168.1.100:8080
10.0.0.50:3128
203.0.113.45:8080
```

---

## 🛠️ 使用指南

### 📥 下載代理

1. **直接下載**：從 GitHub 倉庫頁面下載所需文件
2. **API 獲取**：使用 GitHub API 獲取文件內容
3. **Git 拉取**：`git clone` 或 `git pull` 獲取最新文件

### 🐍 Python 使用範例

```python
import csv
import requests

# 讀取工作代理
with open('proxy_management/exports/working-proxies/working_proxies.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        ip_port, proxy_type, response_time, country, url = row
        print(f"使用代理: {ip_port}")
        
        # 測試代理
        try:
            response = requests.get('https://httpbin.org/ip', 
                                  proxies={'http': f'http://{ip_port}'}, 
                                  timeout=10)
            print(f"代理可用: {response.status_code}")
        except Exception as e:
            print(f"代理不可用: {e}")
```

### 🔄 命令列使用

```bash
# 使用 curl 測試代理
curl -x http://192.168.1.100:8080 https://httpbin.org/ip

# 使用 wget 通過代理下載
wget -e use_proxy=yes -e http_proxy=192.168.1.100:8080 https://example.com
```

---

## 🤖 GitHub Actions 自動化

### ⏰ 執行排程

- **定時執行**：每小時自動執行 (`0 * * * *`)
- **手動觸發**：可通過 GitHub 界面手動執行
- **變更觸發**：proxy_management 目錄變更時自動執行

### 📈 執行流程

1. **環境準備**：設置 Python 3.11 和依賴環境
2. **代理收集**：從 Proxifly 獲取最新代理列表
3. **多層驗證**：執行完整的代理驗證流程
4. **文件生成**：更新所有代理文件和統計數據
5. **自動提交**：將結果提交回 GitHub 倉庫
6. **報告生成**：生成詳細的執行報告

### 📊 執行報告

每次執行後會生成詳細報告，包含：
- ✅ 有效代理數量統計
- 📊 各類型代理分布
- ⏱️ 平均回應時間
- 🌍 地理分布統計
- 📈 歷史趨勢分析

---

## 🔍 驗證機制詳解

### 🧪 多層次驗證架構

```
基礎驗證器 → 簡化驗證器 → 綜合驗證器 → 多層次驗證系統
   (快速)      (輕量)       (完整)         (企業級)
```

### ✅ 驗證項目

#### 1. 基礎連接性測試
- **HTTP 連接**：訪問 `http://httpbin.org/ip`
- **HTTPS 連接**：訪問 `https://www.google.com/generate_204`
- **響應時間**：記錄連接耗時（<10秒）
- **超時控制**：防止無限等待

#### 2. 進階性能測試
- **多級文件測試**：1KB / 10KB / 100KB 文件下載
- **穩定性測試**：多次重複連接測試
- **速度評估**：下載速度分級（優秀/良好/一般/較差）

#### 3. 匿名性檢測
- **🥇 Elite (高匿)**：完全隱藏真實IP
- **🥈 Anonymous (匿名)**：隱藏真實IP，部分標頭信息
- **🥉 Distorting (扭曲)**：修改部分信息
- **⚠️ Transparent (透明)**：完全暴露真實IP

#### 4. 地理位置驗證
- **交叉驗證**：使用多個地理API進行驗證
- **位置比對**：聲稱位置 vs 實際位置
- **準確性評估**：地理位置準確度評分

### 🎯 判定標準

#### 有效代理條件（必須全部滿足）
- ✅ 連接成功：HTTP或HTTPS連接成功
- ✅ 響應及時：響應時間 < 10秒
- ✅ 無連接錯誤：無網絡層面錯誤
- ✅ 協議正確：支援聲明的代理協議

#### 質量指標分級
```python
# 響應時間分級
'excellent': '< 1秒'      # 優秀
'good': '1-3秒'           # 良好
'acceptable': '3-10秒'     # 可接受

# 成功率分級
'high': '> 90%'           # 高
'medium': '70-90%'        # 中等
'low': '< 70%'            # 低
```

---

## 🗃️ 檔案管理系統

### 📁 目錄結構

```
proxy_management/
├── data/
│   ├── archived/           # 歷史數據存檔
│   ├── comprehensive/      # 綜合統計數據
│   ├── proxies/           # 當前代理數據
│   └── sources/           # 代理源數據
├── exports/               # 匯出文件
├── logs/                  # 日誌文件
│   ├── system/           # 系統日誌
│   └── validation/       # 驗證日誌
└── core/                  # 核心模組
```

### 🔄 更新機制

- **增量更新**：保留歷史數據，只更新變化部分
- **版本控制**：所有變更通過 Git 進行版本管理
- **自動備份**：重要數據自動存檔到 `archived/` 目錄
- **清理策略**：可配置自動清理舊文件（默認保留7天）

---

## ⚙️ 開發環境設定

### 📋 系統需求

- **Python**: 3.11+
- **作業系統**: Windows 10 / Linux / macOS
- **依賴管理**: uv (推薦) 或 pip

### 🚀 快速開始

```bash
# 1. 克隆倉庫
git clone https://github.com/jason660519/seek_scraper.git
cd seek_scraper

# 2. 創建虛擬環境
uv venv
uv shell

# 3. 安裝依賴
uv pip install -e .

# 4. 運行代理管理器
python proxy_management/cloud_scheduler.py
```

### 🔧 環境變量

```bash
# 可選配置
export MAX_PROXIES_TO_FETCH=1000    # 最大代理數量
export VALIDATION_TIMEOUT=10         # 驗證超時時間
export MAX_WORKERS=50               # 最大工作線程
export RETRY_INVALID_PROXIES=true   # 重試無效代理
export CLEANUP_OLDER_THAN_DAYS=7     # 清理天數
```

---

## 📞 支援與聯繫

### 📚 相關文檔

- [專案架構文檔](Docs/PROJECT_STRUCTURE.md)
- [代理使用指南](Docs/PROXY_USAGE.md)
- [技術堆疊說明](Docs/tech_stack_spec.md)
- [系統設計規範](Docs/system_design_spec.md)

### 🐛 問題回報

如發現問題，請在 GitHub Issues 中回報，包含：
- 問題描述
- 重現步驟
- 環境信息
- 錯誤日誌

### 🤝 貢獻指南

歡迎提交 Pull Request，請確保：
- 代碼通過測試
- 遵循 PEP 8 規範
- 添加適當註釋
- 更新相關文檔

---

## 📄 授權

本專案採用 MIT 授權，詳見 [LICENSE](LICENSE) 文件。

---

> **💡 提示**: 本系統每小時自動更新代理數據，建議定期 `git pull` 獲取最新代理列表！

---

*最後更新: 2025年9月26日*