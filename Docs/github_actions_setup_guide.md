# GitHub Actions 代理調度器配置指南

## 🚀 快速開始

本指南將幫助您配置 GitHub Actions 自動代理調度系統。

## 📋 必要步驟

### 1. 創建 GitHub 倉庫 Secrets

在您的 GitHub 倉庫中，進入 **Settings → Secrets and variables → Actions**，添加以下 Secrets：

#### 必需 Secrets：

| Secret 名稱 | 說明 | 示例值 |
|------------|------|--------|
| `MAX_PROXIES_TO_FETCH` | 每次抓取的最大代理數量 | `1000` |
| `VALIDATION_TIMEOUT` | 代理驗證超時時間（秒） | `10` |
| `MAX_WORKERS` | 最大並發工作線程數 | `50` |

#### 可選 Secrets：

| Secret 名稱 | 說明 | 默認值 |
|------------|------|--------|
| `PROXY_SOURCES` | 代理源列表（逗號分隔） | `proxifly,freeproxy` |
| `RETRY_INVALID_PROXIES` | 是否重試暫時無效的代理 | `true` |
| `CLEANUP_OLDER_THAN_DAYS` | 清理多少天前的舊數據 | `7` |
| `ENABLE_NOTIFICATIONS` | 是否啟用通知 | `true` |

### 2. 設置倉庫權限

確保 GitHub Actions 有權限提交代碼到您的倉庫：

1. 進入 **Settings → Actions → General**
2. 找到 **Workflow permissions**
3. 選擇 **Read and write permissions**
4. 勾選 **Allow GitHub Actions to create and approve pull requests**

### 3. 創建必要的目錄結構

確保您的倉庫中有以下目錄（腳本會自動創建，但提前創建更好）：

```
proxy_management/
├── data/
│   ├── proxies/
│   └── archived/
├── exports/
│   └── working-proxies/
└── logs/
    ├── system/
    └── validation/
```

## ⚙️ 配置選項詳解

### 代理源配置 (`PROXY_SOURCES`)

支持的代理源：
- `proxifly` - 從 Proxifly API 獲取代理（推薦）
- `freeproxy` - 從免費代理列表獲取
- 可以同時使用多個源，用逗號分隔

示例：`proxifly,freeproxy`

### 性能配置

| 參數 | 建議值 | 說明 |
|------|--------|------|
| `MAX_PROXIES_TO_FETCH` | 500-2000 | 根據 GitHub Actions 的時間限制調整 |
| `MAX_WORKERS` | 20-100 | 並發驗證線程數，太高可能導致超時 |
| `VALIDATION_TIMEOUT` | 5-15 | 單個代理驗證超時時間 |

### 清理配置

| 參數 | 建議值 | 說明 |
|------|--------|------|
| `CLEANUP_OLDER_THAN_DAYS` | 3-14 | 保留多少天的歷史數據 |
| `RETRY_INVALID_PROXIES` | true/false | 是否重試暫時無效的代理 |

## 🔧 手動觸發工作流

配置完成後，您可以：

1. **手動觸發**：進入 Actions 頁面，選擇 "代理定時抓取與驗證" 工作流，點擊 "Run workflow"
2. **查看日誌**：每次執行後，可以在 Actions 頁面查看詳細的執行日誌
3. **下載結果**：執行完成後，可以在 Artifacts 中下載執行日誌

## 📊 監控和調試

### 查看執行狀態

1. 進入 GitHub 倉庫的 **Actions** 頁面
2. 點擊最新的工作流運行
3. 查看每個步驟的執行結果和日誌

### 檢查生成的文件

工作流會自動提交以下文件到您的倉庫：
- `proxy_management/data/proxies/` - 代理數據文件
- `proxy_management/exports/working-proxies/` - 有效代理導出文件
- `proxy_management/logs/system/scheduler_report.json` - 執行報告

### 常見問題排查

#### 工作流失敗

1. **檢查 Secrets 配置**：確保所有必需的 Secrets 都已設置
2. **查看日誌**：點擊失敗的工作流運行，查看詳細的錯誤信息
3. **檢查權限**：確保 GitHub Actions 有足夠的權限

#### 代理獲取失敗

1. **檢查網絡連接**：GitHub Actions 運行器是否能訪問外部 API
2. **檢查代理源**：某些代理源可能暫時不可用
3. **調整超時時間**：增加 `VALIDATION_TIMEOUT` 的值

#### 提交失敗

1. **檢查權限**：確保有寫入倉庫的權限
2. **檢查 Git 配置**：工作流中的 Git 配置是否正確

## 🎯 最佳實踐

### 1. 逐步啟動

建議按以下順序啟動：
1. 先設置每天執行一次，觀察幾天
2. 確認一切正常後，改為每小時執行
3. 根據需要調整參數

### 2. 監控執行

- 定期檢查執行日誌
- 關注成功率和錯誤率
- 根據執行情況調整參數

### 3. 數據管理

- 定期清理舊的日誌文件
- 監控倉庫大小，避免過大
- 重要數據建議備份

### 4. 安全考慮

- 不要在代碼中硬編碼敏感信息
- 使用 Secrets 管理敏感配置
- 定期更新依賴包

## 📈 性能優化

### 提高成功率

1. **增加重試次數**：調整 `RETRY_INVALID_PROXIES=true`
2. **延長超時時間**：增加 `VALIDATION_TIMEOUT`
3. **使用多個代理源**：配置 `PROXY_SOURCES=proxifly,freeproxy`

### 減少執行時間

1. **減少代理數量**：降低 `MAX_PROXIES_TO_FETCH`
2. **減少工作線程**：降低 `MAX_WORKERS`
3. **縮短超時時間**：減少 `VALIDATION_TIMEOUT`

## 🎉 成功指標

配置成功後，您應該看到：

1. ✅ Actions 頁面顯示成功的綠色標記
2. ✅ 倉庫中出現新的代理數據文件
3. ✅ 每小時自動執行一次
4. ✅ 詳細的執行報告和統計數據

## 📞 獲得幫助

如果遇到問題：

1. 查看 GitHub Actions 的執行日誌
2. 檢查工作流配置文件
3. 確認所有 Secrets 設置正確
4. 根據錯誤信息調整配置

祝您使用愉快！🚀