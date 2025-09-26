# 🤝 Figma 交付與協作模式指南

**版本**：v1.0  
**更新日期**：2025-01-26  
**適用專案**：SEEK Job Crawler 代理管理系統  
**目標**：建立高效的設計開發協作流程和交付標準

---

## 📋 目錄

1. [Figma 文件組織結構](#1-figma-文件組織結構)
2. [Frame 命名與分頁規範](#2-frame-命名與分頁規範)
3. [Dev Mode 開發交接配置](#3-dev-mode-開發交接配置)
4. [版本控制與協作流程](#4-版本控制與協作流程)
5. [交付物清單與標準](#5-交付物清單與標準)
6. [質量控制與審核](#6-質量控制與審核)

---

## 1. Figma 文件組織結構

### 📁 主文件結構

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

### 🏷️ 文件命名規範

| 文件類型 | 命名格式                   | 示例                                  |
| -------- | -------------------------- | ------------------------------------- |
| 主文件   | `[專案名稱] Design System` | `SEEK Job Crawler Design System`      |
| 分支文件 | `[專案名稱] - [功能名稱]`  | `SEEK Job Crawler - Proxy Management` |
| 版本文件 | `[專案名稱] v[版本號]`     | `SEEK Job Crawler v1.0`               |

### 👥 權限設置

#### 設計團隊權限

- **設計師**：Edit 權限
- **設計主管**：Edit + Admin 權限
- **設計實習生**：View + Comment 權限

#### 開發團隊權限

- **前端開發**：View + Dev Mode 權限
- **後端開發**：View 權限
- **技術主管**：View + Dev Mode 權限

#### 產品團隊權限

- **產品經理**：View + Comment 權限
- **產品總監**：View + Comment 權限

---

## 2. Frame 命名與分頁規範

### 📐 Frame 命名規範

#### 基本格式

```
[頁面名稱]_[設備類型]_[版本號]_[狀態]
```

#### 命名示例

| Frame 名稱                           | 說明                 |
| ------------------------------------ | -------------------- |
| `Login_Desktop_v1.0_Final`           | 登入頁面桌面版最終版 |
| `Dashboard_Mobile_v1.0_Draft`        | 儀表板手機版草稿     |
| `ProxyManagement_Tablet_v1.1_Review` | 代理管理平板版審核中 |

#### 狀態標識

| 狀態       | 說明   | 使用時機     |
| ---------- | ------ | ------------ |
| `Draft`    | 草稿   | 初步設計階段 |
| `Review`   | 審核中 | 等待評審     |
| `Revision` | 修訂中 | 根據反饋修改 |
| `Final`    | 最終版 | 確認交付版本 |
| `Archive`  | 歸檔   | 歷史版本保存 |

### 📄 分頁組織規範

#### 設計系統頁面 (01 - Design System)

```
Colors & Typography
├── Color Palette
├── Color Variables
├── Typography Scale
├── Text Styles
└── Font Variables

Icons & Components
├── Icon Library
├── Icon Variants
├── Component Overview
└── Component States

Spacing & Grid
├── 8pt Grid System
├── Spacing Scale
├── Layout Grids
└── Responsive Breakpoints

Shadows & Effects
├── Elevation Levels
├── Shadow Styles
├── Blur Effects
└── Animation Principles
```

#### 頁面設計頁面 (04 - Page Designs)

```
Login Page
├── Login_Desktop_v1.0_Final
├── Login_Tablet_v1.0_Final
└── Login_Mobile_v1.0_Final

Dashboard
├── Dashboard_Desktop_v1.0_Final
├── Dashboard_Tablet_v1.0_Final
└── Dashboard_Mobile_v1.0_Final

Proxy Management
├── ProxyManagement_Desktop_v1.0_Final
├── ProxyManagement_Tablet_v1.0_Final
└── ProxyManagement_Mobile_v1.0_Final

System Monitor
├── SystemMonitor_Desktop_v1.0_Final
├── SystemMonitor_Tablet_v1.0_Final
└── SystemMonitor_Mobile_v1.0_Final

Configuration
├── Configuration_Desktop_v1.0_Final
├── Configuration_Tablet_v1.0_Final
└── Configuration_Mobile_v1.0_Final
```

---

## 3. Dev Mode 開發交接配置

### 🔧 Dev Mode 設置

#### 啟用 Dev Mode

1. 點擊右上角 "Dev Mode" 按鈕
2. 切換到開發模式視圖
3. 設置開發團隊權限

#### 標注配置

1. **尺寸標注**：自動生成 CSS 屬性
2. **顏色標注**：顯示 CSS 變量名稱
3. **字體標注**：包含字體家族、大小、行高
4. **間距標注**：使用 8px 網格系統
5. **動效標注**：提供動畫參數

### 📝 標注規範

#### 組件標注

```css
/* 按鈕組件標注 */
.button-primary {
  width: 80px;
  height: 32px;
  background: var(--color-primary-500);
  color: var(--color-white);
  border-radius: 8px;
  font-family: var(--font-family-primary);
  font-size: 14px;
  font-weight: 500;
  line-height: 1.5;
  border: none;
  cursor: pointer;
}

.button-primary:hover {
  background: var(--color-primary-600);
}

.button-primary:disabled {
  background: var(--color-gray-200);
  color: var(--color-gray-400);
  cursor: not-allowed;
}
```

#### 佈局標注

```css
/* 主佈局標注 */
.main-layout {
  display: flex;
  height: 100vh;
}

.header-bar {
  height: 64px;
  background: var(--color-white);
  border-bottom: 1px solid var(--color-gray-200);
  display: flex;
  align-items: center;
  padding: 0 24px;
}

.side-menu {
  width: 240px;
  background: var(--color-gray-50);
  border-right: 1px solid var(--color-gray-200);
  padding: 24px 0;
}

.content-area {
  flex: 1;
  background: var(--color-white);
  padding: 24px;
  overflow: auto;
}
```

### 🎨 資源導出設置

#### 圖標導出

- **格式**：SVG
- **尺寸**：24px 基準
- **優化**：啟用 SVG 優化
- **命名**：`icon-[名稱]-[尺寸].svg`

#### 圖片導出

- **格式**：PNG/JPG
- **分辨率**：2x (Retina)
- **壓縮**：啟用圖片壓縮
- **命名**：`image-[名稱]-[尺寸].png`

#### 字體導出

- **格式**：WOFF2/WOFF
- **子集**：僅包含使用字符
- **命名**：`font-[名稱]-[字重].woff2`

---

## 4. 版本控制與協作流程

### 🔄 版本管理策略

#### 版本號規則

```
主版本.次版本.修訂版本
例如：v1.2.3
```

| 版本類型 | 觸發條件       | 示例            |
| -------- | -------------- | --------------- |
| 主版本   | 重大設計變更   | v1.0.0 → v2.0.0 |
| 次版本   | 新增功能或組件 | v1.0.0 → v1.1.0 |
| 修訂版本 | 細節調整和優化 | v1.0.0 → v1.0.1 |

#### 版本標記

1. **設計完成**：標記為 `v1.0.0`
2. **開發完成**：標記為 `v1.0.1`
3. **測試完成**：標記為 `v1.0.2`
4. **發布完成**：標記為 `v1.0.3`

### 🤝 協作流程

#### 設計階段流程

```
1. 設計師創建分支
   ↓
2. 設計師完成設計
   ↓
3. 設計主管評審
   ↓
4. 產品經理確認
   ↓
5. 合併到主分支
```

#### 開發階段流程

```
1. 開發團隊查看設計
   ↓
2. 開發團隊提出問題
   ↓
3. 設計師解答問題
   ↓
4. 開發團隊實現設計
   ↓
5. 設計師驗證實現
```

#### 評審流程

1. **設計評審**：設計主管評審設計質量
2. **產品評審**：產品經理確認需求符合
3. **技術評審**：技術主管評估實現難度
4. **用戶評審**：用戶測試驗證可用性

### 📋 協作工具

#### Figma 內建功能

- **Comments**：設計評審和反饋
- **Branches**：版本控制和分支管理
- **Dev Mode**：開發交接和標注
- **Version History**：版本歷史追蹤

#### 外部工具整合

- **Slack**：即時溝通和通知
- **Jira**：任務管理和追蹤
- **Confluence**：文檔協作和知識管理
- **GitHub**：代碼版本控制

---

## 5. 交付物清單與標準

### 📦 設計文件交付物

#### 必需交付物

- [ ] **Figma 設計系統文件**

  - 顏色變量和樣式
  - 字體樣式和變量
  - 圖標組件庫
  - 基礎組件庫
  - 業務組件庫

- [ ] **頁面設計文件**

  - 登入頁面 (Desktop/Tablet/Mobile)
  - 主控制台 (Desktop/Tablet/Mobile)
  - 代理管理頁面 (Desktop/Tablet/Mobile)
  - 系統監控頁面 (Desktop/Tablet/Mobile)
  - 配置中心頁面 (Desktop/Tablet/Mobile)

- [ ] **原型文件**

  - 用戶流程原型
  - 交互行為原型
  - 響應式行為原型

- [ ] **開發交接文件**
  - Dev Mode 標注
  - 資源導出包
  - 設計規範文檔

#### 可選交付物

- [ ] **設計規範文檔** (Markdown/PDF)
- [ ] **組件使用指南** (Figma/PDF)
- [ ] **響應式設計指南** (Figma/PDF)
- [ ] **動效實現指南** (Figma/PDF)

### 💻 開發資源交付物

#### CSS 變量文件

```css
/* colors.css */
:root {
  /* Primary Colors */
  --color-primary-500: #1890ff;
  --color-primary-600: #096dd9;
  --color-primary-400: #40a9ff;
  --color-primary-50: #e6f7ff;

  /* Semantic Colors */
  --color-success-500: #52c41a;
  --color-warning-500: #faad14;
  --color-error-500: #f5222d;
  --color-info-500: #1890ff;

  /* Neutral Colors */
  --color-gray-900: #262626;
  --color-gray-600: #595959;
  --color-gray-400: #8c8c8c;
  --color-gray-200: #d9d9d9;
  --color-gray-50: #fafafa;
  --color-white: #ffffff;
}

/* Dark mode */
[data-theme="dark"] {
  --color-gray-900: #ffffff;
  --color-gray-600: #d9d9d9;
  --color-gray-400: #8c8c8c;
  --color-gray-200: #434343;
  --color-gray-50: #1f1f1f;
  --color-white: #141414;
}
```

#### 字體變量文件

```css
/* typography.css */
:root {
  /* Font Families */
  --font-family-primary: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  --font-family-monospace: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono",
    Consolas, "Courier New", monospace;

  /* Font Sizes */
  --font-size-h1: 32px;
  --font-size-h2: 24px;
  --font-size-h3: 20px;
  --font-size-h4: 16px;
  --font-size-body: 14px;
  --font-size-caption: 12px;

  /* Line Heights */
  --line-height-h1: 1.2;
  --line-height-h2: 1.3;
  --line-height-h3: 1.4;
  --line-height-h4: 1.5;
  --line-height-body: 1.5;
  --line-height-caption: 1.4;
}
```

#### 間距變量文件

```css
/* spacing.css */
:root {
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-xxl: 48px;
  --spacing-xxxl: 64px;
}
```

#### 陰影變量文件

```css
/* shadows.css */
:root {
  --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.06);
  --shadow-modal: 0 4px 16px rgba(0, 0, 0, 0.12);
  --shadow-popover: 0 8px 24px rgba(0, 0, 0, 0.18);
  --shadow-tooltip: 0 12px 32px rgba(0, 0, 0, 0.24);
}
```

### 📁 資源文件交付物

#### 圖標資源包

```
icons/
├── svg/
│   ├── icon-database-16.svg
│   ├── icon-database-20.svg
│   ├── icon-database-24.svg
│   └── icon-database-32.svg
├── png/
│   ├── icon-database-16.png
│   ├── icon-database-20.png
│   ├── icon-database-24.png
│   └── icon-database-32.png
└── README.md
```

#### 字體資源包

```
fonts/
├── woff2/
│   ├── font-primary-regular.woff2
│   ├── font-primary-medium.woff2
│   └── font-primary-semibold.woff2
├── woff/
│   ├── font-primary-regular.woff
│   ├── font-primary-medium.woff
│   └── font-primary-semibold.woff
└── README.md
```

---

## 6. 質量控制與審核

### ✅ 設計質量檢查

#### 設計系統檢查

- [ ] 所有組件使用統一的顏色變量
- [ ] 所有文字使用統一的字體樣式
- [ ] 所有間距符合 8px 網格系統
- [ ] 所有陰影使用統一的陰影層級
- [ ] 所有圓角使用統一的圓角值

#### 頁面設計檢查

- [ ] 所有頁面使用統一的佈局結構
- [ ] 所有頁面響應式行為正確
- [ ] 所有頁面組件狀態完整
- [ ] 所有頁面交互邏輯清晰
- [ ] 所有頁面無障礙設計考慮

#### 組件庫檢查

- [ ] 所有組件變體完整
- [ ] 所有組件狀態完整
- [ ] 所有組件響應式行為正確
- [ ] 所有組件使用變量
- [ ] 所有組件文檔完整

### 🔍 開發交接檢查

#### Dev Mode 檢查

- [ ] 所有組件標注完整
- [ ] 所有尺寸標注準確
- [ ] 所有顏色標注使用變量
- [ ] 所有字體標注完整
- [ ] 所有間距標注準確

#### 資源導出檢查

- [ ] 所有圖標導出完整
- [ ] 所有圖片導出完整
- [ ] 所有字體導出完整
- [ ] 所有資源命名規範
- [ ] 所有資源格式正確

### 📋 審核流程

#### 設計審核

1. **設計師自檢**：完成設計後進行自檢
2. **設計主管評審**：設計主管進行質量評審
3. **產品經理確認**：產品經理確認需求符合
4. **技術主管評估**：技術主管評估實現難度

#### 開發審核

1. **開發團隊評審**：開發團隊評審設計可行性
2. **設計師驗證**：設計師驗證實現效果
3. **用戶測試**：用戶測試驗證可用性
4. **最終確認**：所有相關人員最終確認

### 📊 質量指標

#### 設計質量指標

- **一致性**：95% 以上組件使用統一變量
- **完整性**：100% 組件狀態完整
- **響應式**：100% 頁面響應式適配
- **無障礙**：符合 WCAG 2.1 AA 標準

#### 交付質量指標

- **準時交付**：100% 按時交付
- **標注完整**：100% 組件標注完整
- **資源完整**：100% 資源導出完整
- **文檔完整**：100% 文檔說明完整

---

## 📋 實施檢查清單

### 文件設置檢查清單

- [ ] 創建 Figma 文件結構
- [ ] 設置文件權限
- [ ] 創建分頁結構
- [ ] 設置 Frame 命名規範
- [ ] 啟用 Dev Mode
- [ ] 設置標注規範
- [ ] 配置資源導出
- [ ] 建立版本控制流程

### 協作流程檢查清單

- [ ] 建立設計評審流程
- [ ] 建立開發交接流程
- [ ] 建立版本管理流程
- [ ] 建立質量控制流程
- [ ] 建立溝通協作機制
- [ ] 建立問題解決機制
- [ ] 建立持續改進機制

### 交付物檢查清單

- [ ] 設計系統文件完整
- [ ] 頁面設計文件完整
- [ ] 原型文件完整
- [ ] 開發交接文件完整
- [ ] CSS 變量文件完整
- [ ] 資源文件完整
- [ ] 文檔說明完整
- [ ] 使用指南完整

---

## 🚀 下一步行動

1. **立即執行**：按照本指南設置 Figma 協作環境
2. **團隊培訓**：對設計和開發團隊進行培訓
3. **流程實施**：實施協作流程和質量控制
4. **持續優化**：根據實際使用情況持續優化

---

**文檔版本**：v1.0  
**最後更新**：2025-01-26  
**負責人**：UI/UX 設計團隊  
**審核狀態**：待審核
