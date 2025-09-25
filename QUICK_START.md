# 🚀 快速開始使用代理測試工具

## 安裝和設置

```powershell
# 1. 執行 scripts/setup_env.ps1 完成依賴安裝與測試
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
./scripts/setup_env.ps1 -SkipTests

# 2. 切換至專案根目錄以便執行以下指令
```

## 基本使用命令

### 1. 獲取所有類型代理 (推薦)

```powershell
uv run proxy_tester.py --test-once --proxy-type all
```

### 2. 獲取 HTTP 代理

```powershell
uv run proxy_tester.py --test-once --proxy-type http
```

### 3. 驗證代理有效性

```powershell
uv run proxy_tester.py --validate-proxies --proxy-type http
```

### 4. 監控模式（每 5 分鐘檢查一次，運行 12 次 = 1 小時）

```powershell
uv run proxy_tester.py --monitor --interval 5 --max-runs 12 --proxy-type http
```

### 5. 測試更新頻率（運行 30 分鐘的監控）

```powershell
uv run python proxy_update_monitor.py
```

## 檔案位置

所有輸出檔案都在 `data/proxies/` 目錄中：

- 代理列表：`proxies_YYYYMMDD_HHMMSS.csv`
- 驗證結果：`proxy_validation_YYYYMMDD_HHMMSS.csv`
- 運行日誌：`proxy_tester.log`

## 測試結果預期

- **代理數量**：300-500 個
- **有效率**：5-15% (免費代理特性)
- **更新頻率**：官方聲稱每 5 分鐘
- **代理類型**：HTTP, SOCKS4, SOCKS5
