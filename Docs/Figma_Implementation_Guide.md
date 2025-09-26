# 🛠️ Figma 設計系統實施指南

**版本**：v1.0  
**更新日期**：2025-01-26  
**適用專案**：SEEK Job Crawler 代理管理系統  
**目標**：提供詳細的 Figma 操作步驟，確保設計規範的正確實施

---

## 📋 目錄

1. [Figma 文件結構設置](#1-figma-文件結構設置)
2. [色彩系統實施](#2-色彩系統實施)
3. [字體系統實施](#3-字體系統實施)
4. [圖標系統實施](#4-圖標系統實施)
5. [組件庫建立](#5-組件庫建立)
6. [響應式設計設置](#6-響應式設計設置)
7. [Dev Mode 配置](#7-dev-mode-配置)

---

## 1. Figma 文件結構設置

### 📁 創建主文件結構

#### 步驟 1：創建 Figma 文件

1. 打開 Figma
2. 點擊 "New file"
3. 命名為 "SEEK Job Crawler Design System"
4. 設置為 Team 文件（如果使用 Figma Team）

#### 步驟 2：創建頁面結構

在左側面板創建以下頁面：

```
📄 01 - Design System
📄 02 - Layout Templates
📄 03 - Component Library
📄 04 - Page Designs
📄 05 - Prototypes
📄 06 - Development Handoff
```

#### 步驟 3：設置文件屬性

1. 點擊右上角 "Share" 按鈕
2. 設置權限為 "Anyone with the link can view"
3. 啟用 "Dev Mode" 權限
4. 添加團隊成員

---

## 2. 色彩系統實施

### 🎨 創建顏色變量 (Color Variables)

#### 步驟 1：進入 Design System 頁面

1. 切換到 "01 - Design System" 頁面
2. 創建 Frame 命名為 "Color System"

#### 步驟 2：創建主色調變量

1. 創建矩形，設置顏色為 `#1890ff`
2. 選中矩形，右側面板點擊 "Variables"
3. 點擊 "+" 創建變量
4. 設置變量名稱為 "Primary/500"
5. 設置模式為 "Light mode"
6. 重複創建以下變量：

| 變量名稱    | 色值    | 模式  |
| ----------- | ------- | ----- |
| Primary/500 | #1890ff | Light |
| Primary/600 | #096dd9 | Light |
| Primary/400 | #40a9ff | Light |
| Primary/50  | #e6f7ff | Light |

#### 步驟 3：創建語義色變量

重複上述步驟創建語義色：

| 變量名稱    | 色值    | 模式  |
| ----------- | ------- | ----- |
| Success/500 | #52c41a | Light |
| Warning/500 | #faad14 | Light |
| Error/500   | #f5222d | Light |
| Info/500    | #1890ff | Light |

#### 步驟 4：創建中性色變量

創建中性色變量：

| 變量名稱 | 色值    | 模式  |
| -------- | ------- | ----- |
| Gray/900 | #262626 | Light |
| Gray/600 | #595959 | Light |
| Gray/400 | #8c8c8c | Light |
| Gray/200 | #d9d9d9 | Light |
| Gray/50  | #fafafa | Light |
| White    | #ffffff | Light |

#### 步驟 5：創建 Dark Mode 變量

1. 在 Variables 面板點擊 "Modes"
2. 添加 "Dark mode"
3. 為每個變量設置 Dark mode 值：

| 變量名稱             | Light 值 | Dark 值 |
| -------------------- | -------- | ------- |
| Text/Primary         | #262626  | #ffffff |
| Text/Secondary       | #595959  | #d9d9d9 |
| Text/Tertiary        | #8c8c8c  | #8c8c8c |
| Border/Default       | #d9d9d9  | #434343 |
| Background/Primary   | #ffffff  | #141414 |
| Background/Secondary | #fafafa  | #1f1f1f |

#### 步驟 6：創建代理狀態色變量

創建代理專用狀態色：

| 變量名稱        | 色值    | 用途     |
| --------------- | ------- | -------- |
| Proxy/Valid     | #52c41a | 有效代理 |
| Proxy/Temporary | #faad14 | 暫時無效 |
| Proxy/Invalid   | #f5222d | 永久無效 |
| Proxy/Untested  | #d9d9d9 | 未測試   |

---

## 3. 字體系統實施

### 📝 創建文字樣式 (Text Styles)

#### 步驟 1：創建字體樣式框架

1. 在 "01 - Design System" 頁面創建 Frame 命名為 "Typography"
2. 創建文字框展示字體層級

#### 步驟 2：創建字體樣式

1. 創建文字框，輸入 "H1 - Page Title"
2. 設置字體屬性：
   - Font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto
   - Size: 32px
   - Weight: 600
   - Line Height: 1.2
3. 右側面板點擊 "Text" 樣式
4. 點擊 "+" 創建樣式
5. 命名為 "H1/Page Title"
6. 重複創建以下樣式：

| 樣式名稱         | 大小 | 字重 | 行高 | 用途       |
| ---------------- | ---- | ---- | ---- | ---------- |
| H1/Page Title    | 32px | 600  | 1.2  | 頁面主標題 |
| H2/Section Title | 24px | 600  | 1.3  | 區塊標題   |
| H3/Card Title    | 20px | 500  | 1.4  | 卡片標題   |
| H4/Form Title    | 16px | 500  | 1.5  | 表單標題   |
| Body/Regular     | 14px | 400  | 1.5  | 主要內容   |
| Caption/Helper   | 12px | 400  | 1.4  | 輔助說明   |
| Code/Monospace   | 13px | 400  | 1.4  | 代碼顯示   |

#### 步驟 3：創建字體變量

1. 在 Variables 面板創建字體變量
2. 創建以下變量：

| 變量名稱              | 值                                                    | 用途         |
| --------------------- | ----------------------------------------------------- | ------------ |
| Font/Family/Primary   | -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto | 主要字體     |
| Font/Family/Monospace | 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono'     | 等寬字體     |
| Font/Size/H1          | 32px                                                  | H1 字體大小  |
| Font/Size/H2          | 24px                                                  | H2 字體大小  |
| Font/Size/H3          | 20px                                                  | H3 字體大小  |
| Font/Size/H4          | 16px                                                  | H4 字體大小  |
| Font/Size/Body        | 14px                                                  | 正文字體大小 |
| Font/Size/Caption     | 12px                                                  | 說明字體大小 |

---

## 4. 圖標系統實施

### 🔧 創建圖標組件

#### 步驟 1：創建圖標框架

1. 在 "01 - Design System" 頁面創建 Frame 命名為 "Iconography"
2. 創建 24x24 的 Frame 作為圖標容器

#### 步驟 2：導入 Ant Design 圖標

1. 安裝 Figma 插件 "Ant Design Icons"
2. 在插件中搜索需要的圖標
3. 拖拽到 Fig 件框架中

#### 步驟 3：創建圖標組件

1. 選中圖標，右鍵 "Create Component"
2. 命名為 "Icon/[圖標名稱]"
3. 設置組件屬性：
   - Size: 24x24 (默認)
   - Color: 使用顏色變量
   - Style: Outlined (線性)

#### 步驟 4：創建圖標變體

為每個圖標創建不同尺寸的變體：

| 組件名稱         | 尺寸  | 用途     |
| ---------------- | ----- | -------- |
| Icon/Database/16 | 16x16 | 小圖標   |
| Icon/Database/20 | 20x20 | 中等圖標 |
| Icon/Database/24 | 24x24 | 標準圖標 |
| Icon/Database/32 | 32x32 | 大圖標   |

#### 步驟 5：創建圖標庫

創建以下常用圖標組件：

| 圖標名稱         | 用途     | 組件名稱      |
| ---------------- | -------- | ------------- |
| DatabaseOutlined | 代理管理 | Icon/Database |
| MonitorOutlined  | 系統監控 | Icon/Monitor  |
| SettingOutlined  | 配置中心 | Icon/Setting  |
| BarChartOutlined | 數據分析 | Icon/Chart    |
| UserOutlined     | 用戶管理 | Icon/User     |
| SearchOutlined   | 搜索功能 | Icon/Search   |
| FilterOutlined   | 篩選功能 | Icon/Filter   |
| DownloadOutlined | 導出功能 | Icon/Download |
| UploadOutlined   | 導入功能 | Icon/Upload   |
| ReloadOutlined   | 刷新數據 | Icon/Reload   |

---

## 5. 組件庫建立

### 🧩 創建基礎組件

#### 步驟 1：創建組件庫頁面

1. 切換到 "03 - Component Library" 頁面
2. 創建 Frame 命名為 "Basic Components"

#### 步驟 2：創建按鈕組件

1. 創建矩形，設置尺寸 80x32
2. 設置填充色為 Primary/500 變量
3. 添加文字 "Button"
4. 設置圓角 8px
5. 右鍵 "Create Component"
6. 命名為 "Button/Primary"

#### 步驟 3：創建按鈕變體

創建按鈕的不同狀態變體：

| 變體名稱                | 填充色      | 用途     |
| ----------------------- | ----------- | -------- |
| Button/Primary/Default  | Primary/500 | 默認狀態 |
| Button/Primary/Hover    | Primary/600 | 懸停狀態 |
| Button/Primary/Pressed  | Primary/700 | 點擊狀態 |
| Button/Primary/Disabled | Gray/200    | 禁用狀態 |

#### 步驟 4：創建輸入框組件

1. 創建矩形，設置尺寸 200x32
2. 設置邊框色為 Gray/200
3. 添加佔位符文字 "Placeholder"
4. 創建組件 "Input/Text"

#### 步驟 5：創建卡片組件

1. 創建矩形，設置尺寸 300x200
2. 設置填充色為 White
3. 設置陰影為 Level 1
4. 添加內容區域
5. 創建組件 "Card/Basic"

#### 步驟 6：創建表格組件

1. 創建表格結構
2. 設置表頭樣式
3. 設置數據行樣式
4. 創建組件 "Table/Basic"

### 🏢 創建業務組件

#### 步驟 1：創建業務組件框架

1. 在 "03 - Component Library" 頁面創建 Frame 命名為 "Business Components"

#### 步驟 2：創建代理卡片組件

1. 創建卡片容器
2. 添加代理信息區域
3. 添加狀態指示器
4. 添加操作按鈕
5. 創建組件 "ProxyCard"

#### 步驟 3：創建狀態徽章組件

1. 創建圓角矩形
2. 設置不同狀態顏色
3. 添加狀態文字
4. 創建組件 "StatusBadge"

#### 步驟 4：創建圖表卡片組件

1. 創建卡片容器
2. 添加圖表佔位符
3. 添加標題和數據
4. 創建組件 "ChartCard"

---

## 6. 響應式設計設置

### 📱 創建響應式框架

#### 步驟 1：創建響應式頁面

1. 切換到 "02 - Layout Templates" 頁面
2. 創建三個 Frame：
   - Desktop Layout (1440x1024)
   - Tablet Layout (768x1024)
   - Mobile Layout (375x812)

#### 步驟 2：設置 Auto Layout

1. 選中 Frame
2. 右側面板設置 Auto Layout
3. 設置方向為 Vertical
4. 設置間距為 24px

#### 步驟 3：創建響應式組件

1. 創建響應式組件
2. 設置不同尺寸的變體
3. 使用 Constraints 設置響應行為

#### 步驟 4：設置斷點

1. 在 Figma 中設置斷點
2. 創建不同斷點的設計
3. 設置組件的響應行為

---

## 7. Dev Mode 配置

### 🔧 設置 Dev Mode

#### 步驟 1：啟用 Dev Mode

1. 點擊右上角 "Dev Mode" 按鈕
2. 切換到開發模式視圖

#### 步驟 2：設置標注

1. 選中組件
2. 在右側面板設置標注
3. 添加尺寸、顏色、字體信息

#### 步驟 3：創建規格文檔

1. 在 "06 - Development Handoff" 頁面
2. 創建規格文檔
3. 添加開發說明

#### 步驟 4：導出資源

1. 選中需要導出的資源
2. 右鍵 "Export"
3. 選擇導出格式
4. 設置導出設置

---

## 📋 檢查清單

### 設計系統檢查清單

- [ ] 創建 Figma 文件結構
- [ ] 設置顏色變量（Light/Dark mode）
- [ ] 創建字體樣式
- [ ] 建立圖標組件庫
- [ ] 創建基礎組件
- [ ] 創建業務組件
- [ ] 設置響應式設計
- [ ] 配置 Dev Mode
- [ ] 創建開發交接文檔
- [ ] 測試組件功能

### 質量檢查清單

- [ ] 所有組件使用變量
- [ ] 響應式行為正確
- [ ] 組件狀態完整
- [ ] 標注信息準確
- [ ] 導出資源完整
- [ ] 文檔說明清晰

---

## 🚀 下一步行動

1. **立即執行**：按照本指南創建 Figma 設計系統
2. **團隊協作**：邀請開發團隊參與評審
3. **迭代優化**：根據反饋持續改進設計系統
4. **文檔維護**：定期更新設計規範文檔

---

**文檔版本**：v1.0  
**最後更新**：2025-01-26  
**負責人**：UI/UX 設計團隊  
**審核狀態**：待審核
