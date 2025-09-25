# 代理 IP 測試工具使用說明

這個工具用於測試 Proxifly 免費代理列表 API 的功能和性能。

## 功能特點

- 📋 從 Proxifly API 獲取免費代理列表
- 💾 將代理資料儲存為 CSV 格式
- 🔄 持續監控代理更新頻率
- ✅ 驗證代理的有效性和響應時間
- 📊 統計分析和歷史記錄

## API 限制

- **免費版本**: 每5分鐘更新約500個IP
- **付費版本**: 一個月只能呼叫100次API

## 使用方法

### 1. 單次測試
```bash
uv run proxy_tester.py --test-once
```

### 2. 持續監控（每5分鐘獲取一次）
```bash
uv run proxy_tester.py --monitor
```

### 3. 自訂監控間隔（例如每10分鐘）
```bash
uv run proxy_tester.py --monitor --interval 10 --max-runs 50
```

### 4. 驗證代理有效性
```bash
uv run proxy_tester.py --validate-proxies
```

## 輸出檔案

所有資料將儲存在 `data/proxies/` 目錄中：

- `proxies_YYYYMMDD_HHMMSS.csv`: 代理列表資料
- `proxy_validation_YYYYMMDD_HHMMSS.csv`: 代理驗證結果
- `proxy_history.json`: 歷史記錄和統計資料
- `proxy_tester.log`: 程式運行日誌

## CSV 檔案格式

### 代理列表 CSV 欄位
- `ip`: 代理 IP 地址
- `port`: 代理端口
- `country`: 國家代碼
- `anonymity`: 匿名等級
- `type`: 代理類型 (http/https/socks)
- `speed`: 速度評分
- `uptime`: 正常運行時間
- `fetched_at`: 獲取時間

### 驗證結果 CSV 欄位
- `ip`: 代理 IP 地址
- `port`: 代理端口
- `status`: 狀態 (valid/invalid/failed)
- `response_time`: 響應時間（秒）
- `proxy_ip`: 實際出口 IP（如果成功）
- `error`: 錯誤訊息（如果失敗）

## 統計資訊

程式會自動追蹤以下統計資訊：
- 總共獲取次數
- 平均間隔時間
- 代理數量變化
- 累積唯一代理數量

## 注意事項

1. 免費 API 有使用限制，請勿過度頻繁呼叫
2. 代理驗證會消耗一定時間，建議在網路狀況良好時進行
3. 程式會自動記錄所有操作日誌，方便問題排查