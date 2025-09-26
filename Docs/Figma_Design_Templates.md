# 🎨 Figma 設計模板與頁面規範

**版本**：v1.0  
**更新日期**：2025-01-26  
**適用專案**：SEEK Job Crawler 代理管理系統  
**目標**：提供具體的頁面設計模板和組件規範

---

## 📋 目錄

1. [登入頁面設計模板](#1-登入頁面設計模板)
2. [主控制台設計模板](#2-主控制台設計模板)
3. [代理管理頁面設計模板](#3-代理管理頁面設計模板)
4. [系統監控頁面設計模板](#4-系統監控頁面設計模板)
5. [配置中心頁面設計模板](#5-配置中心頁面設計模板)
6. [響應式適配規範](#6-響應式適配規範)

---

## 1. 登入頁面設計模板

### 🖥️ Desktop 版本 (1440x1024)

#### 佈局結構

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                    Logo + 標題                          │
│                                                         │
│                ┌─────────────────┐                      │
│                │                 │                      │
│                │   Login Form    │                      │
│                │                 │                      │
│                │  - 用戶名輸入    │                      │
│                │  - 密碼輸入      │                      │
│                │  - 驗證碼輸入    │                      │
│                │  - 登入按鈕      │                      │
│                │  - 記住登入      │                      │
│                │                 │                      │
│                └─────────────────┘                      │
│                                                         │
│                  語言切換器                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### 設計規範

- **背景**：漸變背景 `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- **卡片**：白色背景，圓角 12px，陰影 Level 2
- **尺寸**：登入卡片 400x500px
- **間距**：卡片內間距 32px
- **對齊**：垂直水平居中

#### 組件配置

```css
LoginCard {
  width: 400px;
  height: 500px;
  background: White;
  border-radius: 12px;
  shadow: Level 2;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

Logo {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
}

Title {
  font: H2/Section Title;
  color: Gray/900;
  text-align: center;
  margin-bottom: 8px;
}

Subtitle {
  font: Body/Regular;
  color: Gray/600;
  text-align: center;
  margin-bottom: 32px;
}

InputField {
  width: 100%;
  height: 40px;
  border: 1px solid Gray/200;
  border-radius: 8px;
  padding: 0 12px;
  font: Body/Regular;
}

LoginButton {
  width: 100%;
  height: 40px;
  background: Primary/500;
  color: White;
  border-radius: 8px;
  font: H4/Form Title;
  border: none;
}

LanguageSelector {
  position: absolute;
  top: 24px;
  right: 24px;
  width: 120px;
}
```

### 📱 Mobile 版本 (375x812)

#### 佈局調整

- **卡片寬度**：320px（左右各留 27.5px 邊距）
- **卡片高度**：自適應內容
- **間距**：減少為 16px
- **字體**：H2 改為 H3，Body 保持不變

#### 響應式行為

- **語言切換器**：移至卡片內部
- **按鈕高度**：增加至 48px（觸控友好）
- **輸入框高度**：增加至 48px

---

## 2. 主控制台設計模板

### 🖥️ Desktop 版本 (1440x1024)

#### 佈局結構

```
┌─────────────────────────────────────────────────────────┐
│ HeaderBar (64px)                                        │
│ ┌─────┬─────────────────────────┬─────────┬─────────┐   │
│ │Logo │     Quick Search        │ Notify  │ User    │   │
│ └─────┴─────────────────────────┴─────────┴─────────┘   │
├─────────────┬───────────────────────────────────────────┤
│             │                                           │
│ SideMenu    │              ContentArea                  │
│ (240px)     │                                           │
│ ┌─────────┐ │ ┌─────────┬─────────┬─────────┬─────────┐ │
│ │Dashboard│ │ │StatCard1│StatCard2│StatCard3│StatCard4│ │
│ │Proxies  │ │ └─────────┴─────────┴─────────┴─────────┘ │
│ │Monitor  │ │                                           │
│ │Config   │ │ ┌─────────────────────────────────────────┐ │
│ │Logs     │ │ │            Chart Grid                   │ │
│ └─────────┘ │ │                                         │ │
│             │ │  ┌─────────┐ ┌─────────┐ ┌─────────┐   │ │
│             │ │  │Chart 1  │ │Chart 2  │ │Chart 3  │   │ │
│             │ │  └─────────┘ └─────────┘ └─────────┘   │ │
│             │ └─────────────────────────────────────────┘ │
│             │                                           │
│             │ ┌─────────────────────────────────────────┐ │
│             │ │            Recent Activity              │ │
│             │ └─────────────────────────────────────────┘ │
└─────────────┴───────────────────────────────────────────┘
```

#### 設計規範

- **HeaderBar**：高度 64px，背景 White，陰影 Level 1
- **SideMenu**：寬度 240px，背景 Gray/50
- **ContentArea**：剩餘空間，背景 White
- **間距**：內容區域間距 24px

#### 組件配置

```css
HeaderBar {
  height: 64px;
  background: White;
  border-bottom: 1px solid Gray/200;
  display: flex;
  align-items: center;
  padding: 0 24px;
  shadow: Level 1;
}

Logo {
  width: 32px;
  height: 32px;
  margin-right: 16px;
}

QuickSearch {
  flex: 1;
  max-width: 400px;
  height: 32px;
  border: 1px solid Gray/200;
  border-radius: 6px;
  padding: 0 12px;
  margin: 0 24px;
}

SideMenu {
  width: 240px;
  background: Gray/50;
  border-right: 1px solid Gray/200;
  padding: 24px 0;
}

MenuItem {
  height: 40px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  font: Body/Regular;
  color: Gray/900;
}

MenuItem:hover {
  background: Primary/50;
  color: Primary/500;
}

MenuItem.active {
  background: Primary/50;
  color: Primary/500;
  border-right: 3px solid Primary/500;
}

StatCard {
  width: 240px;
  height: 120px;
  background: White;
  border-radius: 8px;
  padding: 20px;
  shadow: Level 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

StatCardTitle {
  font: Caption/Helper;
  color: Gray/600;
}

StatCardValue {
  font: H1/Page Title;
  color: Gray/900;
}

StatCardChange {
  font: Caption/Helper;
  color: Success/500;
}

ChartCard {
  background: White;
  border-radius: 8px;
  padding: 20px;
  shadow: Level 1;
  min-height: 300px;
}

ChartTitle {
  font: H3/Card Title;
  color: Gray/900;
  margin-bottom: 16px;
}
```

### 📱 Mobile 版本 (375x812)

#### 佈局調整

- **HeaderBar**：保持 64px 高度
- **SideMenu**：變為抽屜式，寬度 280px
- **ContentArea**：全寬顯示
- **StatCard**：改為 2x2 網格佈局
- **ChartCard**：垂直堆疊，全寬顯示

#### 響應式行為

- **側邊菜單**：點擊漢堡菜單彈出抽屜
- **統計卡片**：每行 2 個，高度調整為 100px
- **圖表卡片**：垂直堆疊，高度調整為 250px

---

## 3. 代理管理頁面設計模板

### 🖥️ Desktop 版本 (1440x1024)

#### 佈局結構

```
┌─────────────────────────────────────────────────────────┐
│ HeaderBar (64px)                                        │
├─────────────┬───────────────────────────────────────────┤
│             │ FilterPanel (240px)                       │
│ SideMenu    │ ┌─────────────────────────────────────────┐ │
│ (240px)     │ │ Protocol: [HTTP▼] [SOCKS4▼] [SOCKS5▼]  │ │
│             │ │ Status:   [Valid▼] [Invalid▼]         │ │
│             │ │ Country:  [All▼]                       │ │
│             │ │ Response: [0-100ms▼]                   │ │
│             │ │ Search:   [________] [🔍]              │ │
│             │ └─────────────────────────────────────────┘ │
│             │                                           │
│             │ ActionBar (48px)                          │
│             │ ┌─────────────────────────────────────────┐ │
│             │ │ [✓] Select All  [Validate] [Delete]     │ │
│             │ │ [Export▼] [Import] [Refresh]            │ │
│             │ └─────────────────────────────────────────┘ │
│             │                                           │
│             │ ProxyTable                                │
│             │ ┌─────────────────────────────────────────┐ │
│             │ │ ☐ IP Address    │ Port │ Protocol │ ... │ │
│             │ │ ☐ 192.168.1.1   │ 8080 │ HTTP     │ ... │ │
│             │ │ ☐ 192.168.1.2   │ 3128 │ SOCKS5   │ ... │ │
│             │ │ ☐ 192.168.1.3   │ 1080 │ SOCKS4   │ ... │ │
│             │ └─────────────────────────────────────────┘ │
│             │                                           │
│             │ Pagination                                │
│             │ ┌─────────────────────────────────────────┐ │
│             │ │ ← Previous  1 2 3 4 5 ... 100  Next → │ │
│             │ │ Show: [20▼] per page                    │ │
│             │ └─────────────────────────────────────────┘ │
└─────────────┴───────────────────────────────────────────┘
```

#### 設計規範

- **FilterPanel**：寬度 240px，背景 Gray/50
- **ActionBar**：高度 48px，背景 White
- **ProxyTable**：剩餘空間，背景 White
- **間距**：各區域間距 16px

#### 組件配置

```css
FilterPanel {
  width: 240px;
  background: Gray/50;
  border-right: 1px solid Gray/200;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

FilterGroup {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

FilterLabel {
  font: Caption/Helper;
  color: Gray/600;
  margin-bottom: 4px;
}

FilterSelect {
  width: 100%;
  height: 32px;
  border: 1px solid Gray/200;
  border-radius: 6px;
  padding: 0 8px;
  font: Body/Regular;
}

SearchInput {
  width: 100%;
  height: 32px;
  border: 1px solid Gray/200;
  border-radius: 6px;
  padding: 0 8px 0 32px;
  font: Body/Regular;
}

ActionBar {
  height: 48px;
  background: White;
  border-bottom: 1px solid Gray/200;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

ActionButton {
  height: 32px;
  padding: 0 12px;
  border: 1px solid Gray/200;
  border-radius: 6px;
  font: Body/Regular;
  background: White;
}

ActionButton.primary {
  background: Primary/500;
  color: White;
  border-color: Primary/500;
}

ProxyTable {
  flex: 1;
  background: White;
  overflow: auto;
}

TableHeader {
  height: 48px;
  background: Gray/50;
  border-bottom: 1px solid Gray/200;
  display: flex;
  align-items: center;
  padding: 0 20px;
  font: H4/Form Title;
  color: Gray/900;
}

TableRow {
  height: 56px;
  border-bottom: 1px solid Gray/200;
  display: flex;
  align-items: center;
  padding: 0 20px;
  font: Body/Regular;
}

TableRow:hover {
  background: Gray/50;
}

StatusBadge {
  padding: 4px 8px;
  border-radius: 4px;
  font: Caption/Helper;
  font-weight: 500;
}

StatusBadge.valid {
  background: Success/50;
  color: Success/500;
}

StatusBadge.invalid {
  background: Error/50;
  color: Error/500;
}

StatusBadge.temporary {
  background: Warning/50;
  color: Warning/500;
}

StatusBadge.untested {
  background: Gray/100;
  color: Gray/600;
}
```

### 📱 Mobile 版本 (375x812)

#### 佈局調整

- **FilterPanel**：變為底部抽屜
- **ActionBar**：簡化為主要操作
- **ProxyTable**：改為卡片式佈局
- **每行顯示**：1 個代理卡片

#### 響應式行為

- **篩選面板**：點擊篩選按鈕彈出底部抽屜
- **代理卡片**：垂直堆疊，每張卡片顯示完整信息
- **操作按鈕**：改為圖標按鈕，節省空間

---

## 4. 系統監控頁面設計模板

### 🖥️ Desktop 版本 (1440x1024)

#### 佈局結構

```
┌─────────────────────────────────────────────────────────┐
│ HeaderBar (64px)                                        │
├─────────────┬───────────────────────────────────────────┤
│             │ RealTimeMetrics                           │
│ SideMenu    │ ┌─────────┬─────────┬─────────┬─────────┐ │
│ (240px)     │ │   CPU   │ Memory  │  Disk   │ Network │ │
│             │ │  85%    │  72%    │  45%    │  1.2GB  │ │
│             │ └─────────┴─────────┴─────────┴─────────┘ │
│             │                                           │
│             │ TaskQueueStatus                           │
│             │ ┌─────────────────────────────────────────┐ │
│             │ │ Waiting: 15  │ Running: 8  │ Failed: 2 │ │
│             │ │ Success Rate: 85%                       │ │
│             │ └─────────────────────────────────────────┘ │
│             │                                           │
│             │ ChartsGrid                                │
│             │ ┌─────────────┬─────────────┬─────────────┐ │
│             │ │ Error Rate  │ Response    │ Throughput  │ │
│             │ │ Chart       │ Time Chart  │ Chart       │ │
│             │ └─────────────┴─────────────┴─────────────┘ │
│             │                                           │
│             │ PerformanceMetrics                        │
│             │ ┌─────────────────────────────────────────┐ │
│             │ │ Avg Response: 120ms │ Success: 98.5%   │ │
│             │ │ Proxy Speed: 2.3s   │ Validation: 45/s │ │
│             │ └─────────────────────────────────────────┘ │
└─────────────┴───────────────────────────────────────────┘
```

#### 設計規範

- **實時指標**：圓環圖 + 數值顯示
- **任務隊列**：進度條 + 狀態統計
- **圖表網格**：3x1 佈局，高度 300px
- **性能指標**：2x2 網格，高度 120px

#### 組件配置

```css
MetricCard {
  width: 200px;
  height: 160px;
  background: White;
  border-radius: 8px;
  padding: 20px;
  shadow: Level 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

MetricTitle {
  font: Caption/Helper;
  color: Gray/600;
  text-align: center;
}

MetricValue {
  font: H1/Page Title;
  color: Gray/900;
  text-align: center;
}

MetricChart {
  width: 80px;
  height: 80px;
}

TaskQueueCard {
  background: White;
  border-radius: 8px;
  padding: 20px;
  shadow: Level 1;
  margin-bottom: 20px;
}

TaskQueueTitle {
  font: H3/Card Title;
  color: Gray/900;
  margin-bottom: 16px;
}

TaskQueueStats {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

TaskStat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

TaskStatLabel {
  font: Caption/Helper;
  color: Gray/600;
}

TaskStatValue {
  font: H2/Section Title;
  color: Gray/900;
}

ProgressBar {
  width: 100%;
  height: 8px;
  background: Gray/200;
  border-radius: 4px;
  overflow: hidden;
}

ProgressFill {
  height: 100%;
  background: Success/500;
  transition: width 0.3s ease;
}

ChartsGrid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

ChartCard {
  background: White;
  border-radius: 8px;
  padding: 20px;
  shadow: Level 1;
  min-height: 300px;
}

ChartTitle {
  font: H3/Card Title;
  color: Gray/900;
  margin-bottom: 16px;
}

PerformanceGrid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

PerformanceCard {
  background: White;
  border-radius: 8px;
  padding: 20px;
  shadow: Level 1;
  height: 120px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

PerformanceLabel {
  font: Caption/Helper;
  color: Gray/600;
}

PerformanceValue {
  font: H2/Section Title;
  color: Gray/900;
}
```

### 📱 Mobile 版本 (375x812)

#### 佈局調整

- **實時指標**：2x2 網格佈局
- **任務隊列**：垂直堆疊
- **圖表網格**：垂直堆疊，高度調整為 250px
- **性能指標**：垂直堆疊

#### 響應式行為

- **指標卡片**：寬度調整為 160px
- **圖表卡片**：高度調整為 250px
- **性能卡片**：高度調整為 100px

---

## 5. 配置中心頁面設計模板

### 🖥️ Desktop 版本 (1440x1024)

#### 佈局結構

```
┌─────────────────────────────────────────────────────────┐
│ HeaderBar (64px)                                        │
├─────────────┬───────────────────────────────────────────┤
│             │ TabContainer                              │
│ SideMenu    │ ┌─────────────────────────────────────────┐ │
│ (240px)     │ │ [Scheduler] [Source] [Notification] [Export] │ │
│             │ └─────────────────────────────────────────┘ │
│             │                                           │
│             │ ConfigContent                             │
│             │ ┌─────────────────────────────────────────┐ │
│             │ │ SchedulerConfig                        │ │
│             │ │ ┌─────────┬─────────┬─────────┬─────────┐ │
│             │ │ │ Interval│ Timeout │ Retry   │ Cleanup │ │
│             │ │ │ 30s     │ 10s     │ 3x      │ 1h      │ │
│             │ │ └─────────┴─────────┴─────────┴─────────┘ │
│             │ │                                           │
│             │ │ AdvancedSettings                         │
│             │ │ ┌─────────────────────────────────────────┐ │
│             │ │ │ Concurrency: [10▼]                      │ │
│             │ │ │ Batch Size: [100▼]                      │ │
│             │ │ │ Error Threshold: [5%▼]                  │ │
│             │ │ └─────────────────────────────────────────┘ │
│             │ └─────────────────────────────────────────┘ │
│             │                                           │
│             │ ActionBar                                 │
│             │ ┌─────────────────────────────────────────┐ │
│             │ │ [Save] [Reset] [Test] [Export Config]   │ │
│             │ └─────────────────────────────────────────┘ │
└─────────────┴───────────────────────────────────────────┘
```

#### 設計規範

- **標籤容器**：高度 48px，背景 White
- **配置內容**：剩餘空間，背景 White
- **操作欄**：高度 64px，背景 Gray/50

#### 組件配置

```css
TabContainer {
  height: 48px;
  background: White;
  border-bottom: 1px solid Gray/200;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

TabButton {
  height: 32px;
  padding: 0 16px;
  border: none;
  background: transparent;
  font: Body/Regular;
  color: Gray/600;
  border-radius: 6px;
  margin-right: 8px;
}

TabButton.active {
  background: Primary/50;
  color: Primary/500;
}

ConfigContent {
  flex: 1;
  background: White;
  padding: 24px;
  overflow: auto;
}

ConfigSection {
  margin-bottom: 32px;
}

ConfigSectionTitle {
  font: H3/Card Title;
  color: Gray/900;
  margin-bottom: 16px;
}

ConfigGrid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

ConfigItem {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

ConfigLabel {
  font: Caption/Helper;
  color: Gray/600;
}

ConfigInput {
  height: 32px;
  border: 1px solid Gray/200;
  border-radius: 6px;
  padding: 0 8px;
  font: Body/Regular;
}

ConfigSelect {
  height: 32px;
  border: 1px solid Gray/200;
  border-radius: 6px;
  padding: 0 8px;
  font: Body/Regular;
}

AdvancedSettings {
  background: Gray/50;
  border-radius: 8px;
  padding: 20px;
  margin-top: 24px;
}

AdvancedGrid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
}

ActionBar {
  height: 64px;
  background: Gray/50;
  border-top: 1px solid Gray/200;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

ActionButton {
  height: 36px;
  padding: 0 16px;
  border: 1px solid Gray/200;
  border-radius: 6px;
  font: Body/Regular;
  background: White;
}

ActionButton.primary {
  background: Primary/500;
  color: White;
  border-color: Primary/500;
}

ActionButton.danger {
  background: Error/500;
  color: White;
  border-color: Error/500;
}
```

### 📱 Mobile 版本 (375x812)

#### 佈局調整

- **標籤容器**：改為滾動式標籤
- **配置網格**：改為 1x1 佈局
- **高級設置**：垂直堆疊
- **操作欄**：按鈕改為圖標

#### 響應式行為

- **配置項目**：每行 1 個，高度調整為 48px
- **操作按鈕**：改為圖標按鈕，節省空間
- **標籤切換**：支援左右滑動

---

## 6. 響應式適配規範

### 📱 斷點設定

| 設備類型 | 斷點範圍       | 主要特徵 | 佈局調整 |
| -------- | -------------- | -------- | -------- |
| Mobile   | < 768px        | 單欄佈局 | 垂直堆疊 |
| Tablet   | 768px - 1024px | 雙欄佈局 | 部分並排 |
| Desktop  | > 1024px       | 多欄佈局 | 完全並排 |

### 🔄 響應式組件行為

#### 導航菜單

- **Desktop**：側邊菜單固定顯示 (240px)
- **Tablet**：側邊菜單可折疊 (80px)
- **Mobile**：側邊菜單變為抽屜式

#### 表格組件

- **Desktop**：完整表格顯示
- **Tablet**：隱藏次要欄位
- **Mobile**：卡片式佈局

#### 圖表組件

- **Desktop**：多圖表並排 (3x1)
- **Tablet**：圖表堆疊 (2x1)
- **Mobile**：單圖表全寬 (1x1)

#### 表單組件

- **Desktop**：多欄佈局 (2-4 欄)
- **Tablet**：雙欄佈局 (2 欄)
- **Mobile**：單欄佈局 (1 欄)

### 📐 間距響應式調整

| 組件     | Desktop | Tablet | Mobile |
| -------- | ------- | ------ | ------ |
| 頁面邊距 | 48px    | 24px   | 16px   |
| 卡片間距 | 24px    | 16px   | 12px   |
| 表單間距 | 16px    | 12px   | 8px    |
| 按鈕間距 | 12px    | 8px    | 8px    |

---

## 📋 實施檢查清單

### 設計模板檢查清單

- [ ] 登入頁面設計完成
- [ ] 主控制台設計完成
- [ ] 代理管理頁面設計完成
- [ ] 系統監控頁面設計完成
- [ ] 配置中心頁面設計完成
- [ ] 響應式適配完成
- [ ] 組件庫建立完成
- [ ] 設計規範文檔完成

### 質量檢查清單

- [ ] 所有頁面使用統一的設計系統
- [ ] 響應式行為正確實現
- [ ] 組件狀態完整
- [ ] 顏色和字體使用變量
- [ ] 間距符合 8px 網格系統
- [ ] 陰影和圓角一致
- [ ] 交互狀態完整
- [ ] 無障礙設計考慮

---

**文檔版本**：v1.0  
**最後更新**：2025-01-26  
**負責人**：UI/UX 設計團隊  
**審核狀態**：待審核
