# 🎨 SEEK Job Crawler - Figma 設計系統規範

**版本**：v1.0  
**更新日期**：2025-01-26  
**適用專案**：SEEK Job Crawler 代理管理系統  
**設計工具**：Figma

---

## 📋 目錄

1. [系統規範 (System Specification)](#1-系統規範-system-specification)
2. [佈局與網格規範 (Layout & Grid Specification)](#2-佈局與網格規範-layout--grid-specification)
3. [適配與響應規範 (Adaptive & Responsive Specification)](#3-適配與響應規範-adaptive--responsive-specification)
4. [項目設計規範 (Project Design Specification)](#4-項目設計規範-project-design-specification)
5. [項目設計 (Project Design)](#5-項目設計-project-design)
6. [交付與協作模式 (Mode of Delivery & Collaboration)](#6-交付與協作模式-mode-of-delivery--collaboration)

---

## 1. 系統規範 (System Specification)

### 🎨 色彩系統 (Color System)

#### 主色調 (Primary Colors)

基於專案的科技屬性，採用藍色系作為主色調：

| 色值      | 用途                   | 變量名稱                |
| --------- | ---------------------- | ----------------------- |
| `#1890ff` | 主要品牌色、按鈕、鏈接 | `--color-primary`       |
| `#096dd9` | 懸停狀態               | `--color-primary-hover` |
| `#40a9ff` | 輕微強調               | `--color-primary-light` |
| `#e6f7ff` | 背景強調               | `--color-primary-bg`    |

#### 輔助色 (Secondary Colors)

| 色值      | 用途                   | 變量名稱          |
| --------- | ---------------------- | ----------------- |
| `#52c41a` | 成功狀態、有效代理     | `--color-success` |
| `#faad14` | 警告狀態、暫時無效代理 | `--color-warning` |
| `#f5222d` | 錯誤狀態、永久無效代理 | `--color-error`   |
| `#722ed1` | 信息提示               | `--color-info`    |

#### 中性灰階 (Neutral Colors)

**Light Mode**
| 色值 | 用途 | 變量名稱 |
|------|------|----------|
| `#262626` | 主要文字 | `--color-text-primary` |
| `#595959` | 次要文字 | `--color-text-secondary` |
| `#8c8c8c` | 輔助文字 | `--color-text-tertiary` |
| `#d9d9d9` | 邊框色 | `--color-border` |
| `#fafafa` | 背景色 | `--color-bg-secondary` |
| `#ffffff` | 主背景色 | `--color-bg-primary` |

**Dark Mode**
| 色值 | 用途 | 變量名稱 |
|------|------|----------|
| `#ffffff` | 主要文字 | `--color-text-primary-dark` |
| `#d9d9d9` | 次要文字 | `--color-text-secondary-dark` |
| `#8c8c8c` | 輔助文字 | `--color-text-tertiary-dark` |
| `#434343` | 邊框色 | `--color-border-dark` |
| `#1f1f1f` | 背景色 | `--color-bg-secondary-dark` |
| `#141414` | 主背景色 | `--color-bg-primary-dark` |

#### 代理狀態色彩映射

| 狀態                         | 色值      | 用途           |
| ---------------------------- | --------- | -------------- |
| 有效 (Valid)                 | `#52c41a` | 代理驗證成功   |
| 暫時無效 (Temporary Invalid) | `#faad14` | 代理暫時不可用 |
| 永久無效 (Permanent Invalid) | `#f5222d` | 代理永久失效   |
| 未測試 (Untested)            | `#d9d9d9` | 代理尚未驗證   |

### 📝 字體系統 (Typography Scale)

#### 字體家族

- **主要字體**：`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif`
- **等寬字體**：`'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace`

#### 字體層級定義

| 層級    | 大小 | 行高 | 字重 | 用途       | Figma 變量       |
| ------- | ---- | ---- | ---- | ---------- | ---------------- |
| H1      | 32px | 1.2  | 600  | 頁面主標題 | `--text-h1`      |
| H2      | 24px | 1.3  | 600  | 區塊標題   | `--text-h2`      |
| H3      | 20px | 1.4  | 500  | 卡片標題   | `--text-h3`      |
| H4      | 16px | 1.5  | 500  | 表單標題   | `--text-h4`      |
| Body    | 14px | 1.5  | 400  | 主要內容   | `--text-body`    |
| Caption | 12px | 1.4  | 400  | 輔助說明   | `--text-caption` |
| Code    | 13px | 1.4  | 400  | 代碼顯示   | `--text-code`    |

#### 字體使用原則

1. **層次清晰**：使用不同字重和大小建立視覺層次
2. **可讀性優先**：確保最小 12px 字體大小
3. **一致性**：同一層級使用相同的字體樣式
4. **響應式**：字體大小隨螢幕尺寸調整

### 🔧 圖標系統 (Iconography)

#### 圖標風格

- **主要風格**：線性圖標 (Outlined)
- **輔助風格**：面性圖標 (Filled) - 僅用於狀態指示

#### 圖標尺寸網格

| 尺寸 | 用途               | 網格  |
| ---- | ------------------ | ----- |
| 16px | 小圖標、表單內圖標 | 16×16 |
| 20px | 中等圖標、按鈕圖標 | 20×20 |
| 24px | 大圖標、導航圖標   | 24×24 |
| 32px | 特大圖標、功能圖標 | 32×32 |

#### 常用圖標映射

| 功能     | 圖標名稱           | 用途               |
| -------- | ------------------ | ------------------ |
| 代理管理 | `DatabaseOutlined` | 代理列表、數據庫   |
| 系統監控 | `MonitorOutlined`  | 系統狀態、監控面板 |
| 配置中心 | `SettingOutlined`  | 系統設置、配置     |
| 數據分析 | `BarChartOutlined` | 統計圖表、分析     |
| 用戶管理 | `UserOutlined`     | 用戶信息、登錄     |
| 搜索     | `SearchOutlined`   | 搜索功能           |
| 過濾     | `FilterOutlined`   | 篩選功能           |
| 下載     | `DownloadOutlined` | 導出功能           |
| 上傳     | `UploadOutlined`   | 導入功能           |
| 刷新     | `ReloadOutlined`   | 刷新數據           |

### 🌟 陰影與深度 (Shadow & Elevation)

#### 陰影層級定義

| 層級    | 陰影值                            | 用途             | 變量名稱           |
| ------- | --------------------------------- | ---------------- | ------------------ |
| Level 1 | `0 2px 8px rgba(0, 0, 0, 0.06)`   | 卡片、按鈕       | `--shadow-card`    |
| Level 2 | `0 4px 16px rgba(0, 0, 0, 0.12)`  | 模態框、下拉菜單 | `--shadow-modal`   |
| Level 3 | `0 8px 24px rgba(0, 0, 0, 0.18)`  | 彈出層、工具提示 | `--shadow-popover` |
| Level 4 | `0 12px 32px rgba(0, 0, 0, 0.24)` | 浮動面板         | `--shadow-tooltip` |

#### 深度使用原則

1. **層次分明**：不同層級使用不同陰影強度
2. **一致性**：相同功能使用相同陰影層級
3. **適度使用**：避免過度使用陰影影響性能
4. **響應式**：陰影強度隨主題模式調整

---

## 2. 佈局與網格規範 (Layout & Grid Specification)

### 🏗️ 全局框架 (Global Frame)

#### 主要佈局結構

```
┌─────────────────────────────────────────────────────────┐
│                    HeaderBar (64px)                     │
├─────────────┬───────────────────────────────────────────┤
│             │                                           │
│  SideMenu   │            ContentArea                   │
│   (240px)   │                                           │
│             │                                           │
│             │                                           │
└─────────────┴───────────────────────────────────────────┘
```

#### 框架尺寸定義

| 組件        | 寬度/高度    | 固定模式 | 響應式行為     |
| ----------- | ------------ | -------- | -------------- |
| HeaderBar   | 100% × 64px  | 固定高度 | 內容自適應     |
| SideMenu    | 240px × 100% | 固定寬度 | 可折疊至 80px  |
| ContentArea | 剩餘空間     | 自適應   | 最小寬度 320px |
| Footer      | 100% × 48px  | 固定高度 | 可隱藏         |

### 📐 網格系統 (Grid System)

#### 8-Point Grid System

基於 8px 基數的網格系統，確保設計的一致性和對齊：

| 間距值 | 用途     | 示例           |
| ------ | -------- | -------------- |
| 4px    | 最小間距 | 圖標與文字間距 |
| 8px    | 基礎間距 | 表單元素間距   |
| 16px   | 中等間距 | 卡片內間距     |
| 24px   | 大間距   | 區塊間距       |
| 32px   | 特大間距 | 頁面區塊間距   |
| 48px   | 超大間距 | 主要區塊間距   |
| 64px   | 最大間距 | 頁面邊距       |

#### 響應式網格配置

**Desktop (>1024px)**

- 欄數：12
- 水槽：24px
- 邊距：48px
- 最大寬度：1440px

**Tablet (768px-1024px)**

- 欄數：8
- 水槽：16px
- 邊距：24px

**Mobile (<768px)**

- 欄數：4
- 水槽：12px
- 邊距：16px

### 📏 間距系統 (Spacing Scale)

#### 間距尺度定義

```css
:root {
  --spacing-xs: 4px; /* 最小間距 */
  --spacing-sm: 8px; /* 小間距 */
  --spacing-md: 16px; /* 中等間距 */
  --spacing-lg: 24px; /* 大間距 */
  --spacing-xl: 32px; /* 特大間距 */
  --spacing-xxl: 48px; /* 超大間距 */
  --spacing-xxxl: 64px; /* 最大間距 */
}
```

#### 間距使用原則

1. **對齊原則**：所有元素都必須與網格對齊
2. **一致性原則**：相同功能使用相同間距
3. **留白原則**：利用間距創造視覺呼吸感
4. **層次原則**：通過間距大小建立視覺層次

---

## 3. 適配與響應規範 (Adaptive & Responsive Specification)

### 📱 斷點設定 (Breakpoints)

| 設備類型 | 斷點範圍       | 主要特徵           |
| -------- | -------------- | ------------------ |
| Mobile   | < 768px        | 單欄佈局、觸控操作 |
| Tablet   | 768px - 1024px | 雙欄佈局、混合操作 |
| Desktop  | > 1024px       | 多欄佈局、滑鼠操作 |

### 🔄 響應邏輯 (Responsive Behavior)

#### 導航菜單響應

- **Desktop**：側邊菜單固定顯示
- **Tablet**：側邊菜單可折疊
- **Mobile**：側邊菜單變為抽屜式

#### 表格響應

- **Desktop**：完整表格顯示
- **Tablet**：隱藏次要欄位
- **Mobile**：卡片式佈局

#### 圖表響應

- **Desktop**：多圖表並排
- **Tablet**：圖表堆疊
- **Mobile**：單圖表全寬

### 📋 適配示例 (Examples)

#### 代理管理頁面響應式設計

**Desktop 版本**

- 左側：篩選面板 (240px)
- 右側：代理表格 (剩餘空間)
- 操作欄：頂部固定

**Tablet 版本**

- 篩選面板：可折疊側邊欄
- 代理表格：隱藏次要欄位
- 操作欄：響應式按鈕組

**Mobile 版本**

- 篩選面板：底部抽屜
- 代理列表：卡片式佈局
- 操作欄：底部固定

---

## 4. 項目設計規範 (Project Design Specification)

### 🧩 組件庫 (Component Library)

#### 基礎組件

| 組件名稱 | 用途     | 變體                           |
| -------- | -------- | ------------------------------ |
| Button   | 按鈕     | Primary, Secondary, Text, Link |
| Input    | 輸入框   | Text, Password, Number, Search |
| Select   | 選擇器   | Single, Multiple, Searchable   |
| Table    | 表格     | Basic, Sortable, Filterable    |
| Card     | 卡片     | Basic, Hover, Clickable        |
| Modal    | 模態框   | Basic, Confirm, Form           |
| Tooltip  | 工具提示 | Top, Bottom, Left, Right       |
| Badge    | 徽章     | Status, Count, Dot             |

#### 業務組件

| 組件名稱    | 用途     | 特徵                 |
| ----------- | -------- | -------------------- |
| ProxyCard   | 代理卡片 | 狀態指示、操作按鈕   |
| ProxyTable  | 代理表格 | 排序、篩選、批次操作 |
| StatusBadge | 狀態徽章 | 代理狀態視覺化       |
| ChartCard   | 圖表卡片 | 統計數據展示         |
| FilterPanel | 篩選面板 | 多條件篩選           |
| ActionBar   | 操作欄   | 批次操作、導出       |

### 🎯 交互狀態 (Interactive States)

#### 按鈕狀態

| 狀態     | 視覺表現  | 用途       |
| -------- | --------- | ---------- |
| Default  | 正常顏色  | 默認狀態   |
| Hover    | 顏色加深  | 滑鼠懸停   |
| Pressed  | 顏色更深  | 點擊瞬間   |
| Focus    | 外框高亮  | 鍵盤聚焦   |
| Disabled | 灰色+禁用 | 不可用狀態 |
| Loading  | 載入動畫  | 處理中狀態 |

#### 輸入框狀態

| 狀態     | 視覺表現   | 用途     |
| -------- | ---------- | -------- |
| Default  | 正常邊框   | 默認狀態 |
| Focus    | 主色邊框   | 聚焦狀態 |
| Error    | 錯誤色邊框 | 驗證失敗 |
| Success  | 成功色邊框 | 驗證成功 |
| Disabled | 灰色背景   | 禁用狀態 |

### 🎬 動效原則 (Motion Principles)

#### 動畫參數

| 動畫類型 | 持續時間 | 緩動曲線    | 用途       |
| -------- | -------- | ----------- | ---------- |
| 微交互   | 150ms    | ease-out    | 按鈕點擊   |
| 頁面轉場 | 300ms    | ease-in-out | 路由切換   |
| 模態框   | 250ms    | ease-out    | 彈出/關閉  |
| 載入動畫 | 1000ms   | linear      | 載入指示器 |
| 懸停效果 | 200ms    | ease-out    | 滑鼠懸停   |

#### 動效使用原則

1. **有意義**：動效應該有明確的功能目的
2. **適度**：避免過度動效影響性能
3. **一致**：相同功能使用相同動效
4. **可訪問**：尊重用戶的動效偏好設置

---

## 5. 項目設計 (Project Design)

### 🖥️ 關鍵頁面設計 (Key Screens)

#### 1. 登入頁面 (Login)

**設計要點**：

- 居中佈局，簡潔明瞭
- 品牌色彩突出
- 多語言切換
- 響應式適配

**組件結構**：

```
LoginPage
├── Logo展示區
├── LoginForm
│   ├── 用戶名輸入框
│   ├── 密碼輸入框
│   ├── 驗證碼輸入框
│   └── 登入按鈕
├── 語言切換器
└── 記住登入選項
```

#### 2. 主控制台 (Dashboard)

**設計要點**：

- 數據視覺化突出
- 關鍵指標一目了然
- 快速操作入口
- 即時數據更新

**組件結構**：

```
DashboardLayout
├── HeaderBar
│   ├── Logo
│   ├── 快速搜尋
│   ├── 通知中心
│   ├── 用戶菜單
│   └── 主題切換
├── SideMenu
│   ├── 儀表板
│   ├── 代理管理
│   ├── 系統監控
│   ├── 配置中心
│   └── 日誌查看
└── ContentArea
    ├── 統計卡片組
    ├── 圖表網格
    ├── 最近活動
    └── 快捷操作
```

#### 3. 代理管理頁面 (Proxy Management)

**設計要點**：

- 大量數據的高效展示
- 強大的篩選和搜尋功能
- 批次操作支持
- 即時狀態更新

**組件結構**：

```
ProxyManagementPage
├── FilterPanel
│   ├── 協議篩選
│   ├── 狀態篩選
│   ├── 國家篩選
│   └── 響應時間範圍
├── ActionBar
│   ├── 批次驗證
│   ├── 批次刪除
│   ├── 導出功能
│   └── 導入功能
├── ProxyTable
│   ├── 可排序列
│   ├── 行內操作
│   ├── 分頁控制
│   └── 每頁數量選擇
└── DetailModal
    ├── 基本信息
    ├── 歷史圖表
    └── 操作記錄
```

#### 4. 系統監控頁面 (System Monitor)

**設計要點**：

- 即時監控數據
- 多維度圖表展示
- 告警狀態突出
- 性能指標清晰

**組件結構**：

```
SystemMonitorPage
├── RealTimeMetrics
│   ├── CPU使用率
│   ├── 內存使用率
│   ├── 磁碟使用率
│   └── 網絡速率
├── TaskQueueStatus
│   ├── 等待任務
│   ├── 執行任務
│   ├── 失敗任務
│   └── 完成率
├── ErrorRateChart
│   ├── 錯誤趨勢
│   ├── 錯誤分佈
│   └── 錯誤列表
└── PerformanceMetrics
    ├── 響應時間
    ├── 成功率
    ├── 獲取速度
    └── 驗證吞吐量
```

#### 5. 配置中心頁面 (Configuration)

**設計要點**：

- 分類清晰的配置項
- 即時預覽效果
- 配置驗證提示
- 批量配置支持

**組件結構**：

```
ConfigurationPage
├── TabContainer
│   ├── SchedulerConfig
│   │   ├── 獲取間隔
│   │   ├── 驗證間隔
│   │   ├── 清理間隔
│   │   └── 重試策略
│   ├── SourceConfig
│   │   ├── 來源開關
│   │   ├── API密鑰
│   │   ├── 請求限制
│   │   └── 超時配置
│   ├── NotificationConfig
│   │   ├── Webhook設置
│   │   ├── 郵件配置
│   │   ├── 觸發條件
│   │   └── 消息模板
│   └── ExportConfig
│       ├── 導出格式
│       ├── 命名規則
│       ├── 自動導出
│       └── 保留策略
```

### 🔄 流程原型 (Prototypes)

#### 1. 用戶登入流程

```
開始 → 輸入憑證 → 驗證 → 成功/失敗 → 跳轉儀表板
```

#### 2. 代理驗證流程

```
選擇代理 → 發起驗證 → 顯示進度 → 更新狀態 → 完成通知
```

#### 3. 批次操作流程

```
選擇代理 → 選擇操作 → 確認對話框 → 執行操作 → 結果反饋
```

---

## 6. 交付與協作模式 (Mode of Delivery & Collaboration)

### 📁 Frame 命名與分頁結構

#### Figma 文件結構

```
SEEK Job Crawler Design System
├── 📄 01 - Design System
│   ├── Colors & Typography
│   ├── Icons & Components
│   ├── Spacing & Grid
│   └── Shadows & Effects
├── 📄 02 - Layout Templates
│   ├── Desktop Layouts
│   ├── Tablet Layouts
│   └── Mobile Layouts
├── 📄 03 - Component Library
│   ├── Basic Components
│   ├── Business Components
│   └── Chart Components
├── 📄 04 - Page Designs
│   ├── Login Page
│   ├── Dashboard
│   ├── Proxy Management
│   ├── System Monitor
│   └── Configuration
├── 📄 05 - Prototypes
│   ├── User Flows
│   ├── Interactions
│   └── Responsive Behavior
└── 📄 06 - Development Handoff
    ├── Specifications
    ├── Assets Export
    └── Code Generation
```

#### Frame 命名規範

```
[頁面名稱]_[設備類型]_[版本號]
例如：
- Login_Desktop_v1.0
- Dashboard_Mobile_v1.0
- ProxyManagement_Tablet_v1.0
```

### 🔧 開發交接準備

#### Dev Mode 標注規範

1. **尺寸標注**：所有元素提供精確尺寸
2. **顏色標注**：使用 CSS 變量名稱
3. **字體標注**：包含字體家族、大小、行高
4. **間距標注**：使用 8px 網格系統
5. **動效標注**：提供動畫參數和緩動曲線

#### 資源導出規範

- **圖標**：SVG 格式，24px 基準
- **圖片**：PNG/JPG 格式，2x 分辨率
- **字體**：提供字體文件或 Web Font 鏈接
- **顏色**：CSS 變量文件

### 📚 版本控制與更新

#### 版本管理策略

1. **主版本**：重大設計變更
2. **次版本**：新增功能或組件
3. **修訂版本**：細節調整和優化

#### 協作流程

1. **設計階段**：設計師創建分支進行設計
2. **評審階段**：團隊評審設計方案
3. **開發階段**：開發團隊使用 Dev Mode
4. **測試階段**：設計師驗證實現效果
5. **發布階段**：合併到主分支

### 📦 交付物清單

#### 設計文件

- [ ] Figma 設計系統文件
- [ ] 組件庫文件
- [ ] 頁面設計文件
- [ ] 原型文件

#### 開發資源

- [ ] CSS 變量文件
- [ ] 圖標資源包
- [ ] 字體文件
- [ ] 設計規範文檔

#### 協作文檔

- [ ] 設計系統使用指南
- [ ] 組件使用說明
- [ ] 響應式設計指南
- [ ] 動效實現指南

---

## 🎯 實施建議

### 第一階段：設計系統建立

1. 創建 Figma 設計系統文件
2. 建立色彩、字體、圖標規範
3. 創建基礎組件庫
4. 設定響應式網格系統

### 第二階段：頁面設計

1. 設計關鍵頁面佈局
2. 創建業務組件
3. 建立頁面原型
4. 優化響應式適配

### 第三階段：開發交接

1. 完善 Dev Mode 標注
2. 導出開發資源
3. 創建使用文檔
4. 建立協作流程

### 第四階段：迭代優化

1. 收集開發反饋
2. 優化設計細節
3. 擴展組件庫
4. 更新設計規範

---

**文檔版本**：v1.0  
**最後更新**：2025-01-26  
**負責人**：UI/UX 設計團隊  
**審核狀態**：待審核
