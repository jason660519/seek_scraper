# Seek Job Crawler 專案結構

這個專案已經重新組織為以下結構：

```
seek-job-crawler/
├── src/                          # 核心原始碼
│   ├── main.py                   # 主程式入口
│   ├── main_simple.py            # 簡化版主程式
│   ├── config/                   # 配置模組
│   ├── models/                   # 資料模型
│   ├── scrapers/                 # 爬蟲模組
│   ├── parsers/                  # 解析器模組
│   ├── services/                 # 服務模組
│   └── utils/                    # 工具模組
├── proxy_management/             # 代理管理系統
│   ├── core/                     # 核心代理管理
│   │   └── proxy_update_monitor.py
│   ├── validators/               # 代理驗證器
│   │   ├── simple_proxy_validator.py
│   │   └── geolocation_validator.py
│   ├── testers/                  # 代理測試工具
│   │   ├── advanced_proxy_tester.py
│   │   ├── comprehensive_proxy_validator.py
│   │   ├── multi_layer_validation_system.py
│   │   ├── proxy_tester.py
│   │   └── test_fixed_system.py
│   ├── web_interface/            # Web 測試界面
│   │   ├── app.py
│   │   ├── fixed_app.py
│   │   ├── simple_app.py
│   │   ├── templates/
│   │   └── requirements.txt
│   └── data/                     # 代理數據文件
│       ├── all.txt
│       ├── best_proxies.json
│       ├── best_proxies.txt
│       ├── http.txt
│       ├── socks4.txt
│       ├── socks5.txt
│       └── us_proxies.txt
├── config/                       # 專案配置
│   ├── data_schemas/             # 數據架構定義
│   │   ├── data_schema_spec.json
│   │   └── search_parameters_spec.json
│   └── job_categories/           # 職位分類配置
│       └── job_categories.json
├── tests/                        # 測試文件
├── docs/                         # 專案文檔
├── scripts/                      # 腳本工具
├── logs/                         # 日誌文件
├── tools/                        # 獨立工具
│   └── countries.py
└── data/                         # 數據文件

## 使用說明

### 代理管理系統
所有代理相關的功能現在都集中在 `proxy_management/` 目錄下：

- **測試工具**：使用 `proxy_management/testers/` 中的工具來測試代理
- **驗證器**：使用 `proxy_management/validators/` 來驗證代理
- **Web 界面**：運行 `proxy_management/web_interface/app.py` 來啟動 Web 測試界面
- **代理數據**：所有代理列表文件都在 `proxy_management/data/` 中

### 核心爬蟲
主要的爬蟲邏輯在 `src/` 目錄中，保持原有的模組化結構。

### 配置文件
- 數據架構定義：`config/data_schemas/`
- 職位分類配置：`config/job_categories/`
- 代理列表：`proxy_management/data/`

## 更新日誌
- 重新組織了專案結構，將代理管理相關文件分類整理
- 創建了清晰的目錄層次結構
- 將測試工具、驗證器和 Web 界面分別歸類
- 統一管理所有代理數據文件