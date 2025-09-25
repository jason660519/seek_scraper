# 🚀 快速開始使用代理測試工具

## 安裝和設置

```bash
# 1. 已設置好 uv 環境，依賴已安裝
# 2. 所有必要檔案都在當前目錄中
```

## 基本使用命令

### 1. 獲取所有類型代理 (推薦)
```bash
uv run proxy_tester.py --test-once --proxy-type all
```

### 2. 獲取 HTTP 代理
```bash
uv run proxy_tester.py --test-once --proxy-type http
```

### 3. 驗證代理有效性
```bash
uv run proxy_tester.py --validate-proxies --proxy-type http
```

### 4. 監控模式（每 5 分鐘檢查一次，運行 12 次 = 1 小時）
```bash
uv run proxy_tester.py --monitor --interval 5 --max-runs 12 --proxy-type http
```

### 5. 測試更新頻率（運行 30 分鐘的監控）
```bash
python proxy_update_monitor.py
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