# Proxy Management Frontend - 開發指南

## 📋 目錄

- [項目概述](#項目概述)
- [技術棧](#技術棧)
- [項目結構](#項目結構)
- [開發環境設置](#開發環境設置)
- [開發規範](#開發規範)
- [組件開發](#組件開發)
- [狀態管理](#狀態管理)
- [API 集成](#api-集成)
- [測試](#測試)
- [部署](#部署)
- [故障排除](#故障排除)

## 🎯 項目概述

Proxy Management Frontend 是一個現代化的代理管理系統前端應用，提供直觀的用戶界面來管理代理服務器、監控系統狀態和配置系統參數。

### 主要功能

- **代理管理**: 添加、編輯、刪除、驗證代理服務器
- **實時監控**: WebSocket 實時數據更新
- **數據可視化**: 豐富的圖表和統計信息
- **文件操作**: 支持多格式導入導出
- **響應式設計**: 適配多種設備尺寸
- **國際化**: 支持多語言切換

## 🛠 技術棧

### 核心框架

- **React 18.2.0**: 現代化 UI 框架
- **TypeScript 5.0+**: 類型安全的 JavaScript
- **Vite 4.0+**: 快速構建工具

### UI 組件庫

- **Ant Design 5.0+**: 企業級 UI 組件庫
- **ECharts 5.0+**: 數據可視化圖表庫

### 狀態管理

- **Redux Toolkit 1.9+**: 現代化狀態管理
- **React Redux**: React 與 Redux 的橋接

### 路由與導航

- **React Router 6.0+**: 聲明式路由

### 實時通信

- **Socket.io Client 4.0+**: WebSocket 客戶端

### 開發工具

- **ESLint**: 代碼質量檢查
- **Prettier**: 代碼格式化
- **Jest**: 單元測試框架
- **React Testing Library**: React 組件測試

## 📁 項目結構

```
proxy-management-frontend/
├── public/                 # 靜態資源
├── src/
│   ├── components/         # 可重用組件
│   │   ├── common/        # 通用組件
│   │   ├── charts/        # 圖表組件
│   │   └── ui/            # UI 組件
│   ├── pages/             # 頁面組件
│   │   ├── Dashboard/     # 儀表板
│   │   ├── ProxyManagement/ # 代理管理
│   │   ├── SystemMonitor/ # 系統監控
│   │   └── Configuration/ # 配置中心
│   ├── hooks/             # 自定義 Hooks
│   ├── services/          # API 服務
│   ├── store/             # 狀態管理
│   ├── utils/             # 工具函數
│   ├── types/             # TypeScript 類型定義
│   ├── i18n/              # 國際化文件
│   └── layouts/           # 佈局組件
├── tests/                 # 測試文件
└── docs/                  # 文檔
```

## 🚀 開發環境設置

### 前置要求

- Node.js 16.0+
- npm 或 yarn
- Git

### 安裝步驟

1. **克隆項目**

```bash
git clone <repository-url>
cd proxy-management-frontend
```

2. **安裝依賴**

```bash
npm install
# 或
yarn install
```

3. **啟動開發服務器**

```bash
npm run dev
# 或
yarn dev
```

4. **訪問應用**
   打開瀏覽器訪問 `http://localhost:5173`

### 環境變量

創建 `.env.local` 文件：

```env
# API 基礎 URL
VITE_API_BASE_URL=http://localhost:3000/api

# WebSocket URL
VITE_WS_URL=ws://localhost:3000/ws

# 應用環境
VITE_APP_ENV=development
```

## 📝 開發規範

### 代碼風格

1. **命名規範**

   - 組件名使用 PascalCase: `UserProfile`
   - 函數名使用 camelCase: `handleSubmit`
   - 常量使用 UPPER_SNAKE_CASE: `API_BASE_URL`
   - 文件名使用 kebab-case: `user-profile.tsx`

2. **文件組織**

   - 每個組件一個文件
   - 相關文件放在同一目錄
   - 使用 index.ts 導出

3. **TypeScript 規範**
   - 所有組件必須有類型定義
   - 使用 interface 定義對象類型
   - 避免使用 any 類型

### Git 工作流

1. **分支策略**

   - `main`: 主分支，生產環境代碼
   - `develop`: 開發分支，集成測試
   - `feature/*`: 功能分支
   - `bugfix/*`: 修復分支

2. **提交規範**

   ```
   type(scope): description

   feat: 新功能
   fix: 修復問題
   docs: 文檔更新
   style: 代碼格式
   refactor: 重構
   test: 測試
   chore: 構建過程或輔助工具的變動
   ```

## 🧩 組件開發

### 組件結構

```typescript
/**
 * 組件名稱
 * @author 作者
 * @description 組件描述
 */

import React from "react";
import { ComponentProps } from "./types";

interface Props {
  // 屬性定義
}

const Component: React.FC<Props> = ({ ...props }) => {
  // 組件邏輯

  return <div>{/* JSX */}</div>;
};

export default Component;
```

### 組件最佳實踐

1. **單一職責**: 每個組件只負責一個功能
2. **可重用性**: 設計通用的組件接口
3. **可測試性**: 組件邏輯與 UI 分離
4. **性能優化**: 使用 React.memo 和 useMemo

### 響應式設計

使用 `useResponsive` Hook 實現響應式設計：

```typescript
import { useResponsive } from "../utils/responsive";

const Component: React.FC = () => {
  const { isMobile, getSpacing, getCardPadding } = useResponsive();

  return (
    <div style={{ padding: getCardPadding() }}>
      <Row gutter={getSpacing()}>
        <Col xs={24} md={12}>
          {/* 內容 */}
        </Col>
      </Row>
    </div>
  );
};
```

## 🔄 狀態管理

### Redux Store 結構

```typescript
interface RootState {
  auth: AuthState; // 認證狀態
  proxy: ProxyState; // 代理數據
  system: SystemState; // 系統狀態
  ui: UIState; // UI 狀態
}
```

### 使用 Redux Toolkit

```typescript
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// 異步操作
export const fetchProxies = createAsyncThunk(
  "proxy/fetchProxies",
  async (params: FetchParams) => {
    const response = await apiService.proxies.getList(params);
    return response;
  }
);

// Slice 定義
const proxySlice = createSlice({
  name: "proxy",
  initialState,
  reducers: {
    // 同步操作
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProxies.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchProxies.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      });
  },
});
```

## 🌐 API 集成

### API 服務結構

```typescript
class ApiService {
  // 認證相關
  auth = {
    login: async (credentials) => {
      /* ... */
    },
    logout: async () => {
      /* ... */
    },
  };

  // 代理管理
  proxies = {
    getList: async (params) => {
      /* ... */
    },
    create: async (proxy) => {
      /* ... */
    },
    update: async (id, proxy) => {
      /* ... */
    },
    delete: async (id) => {
      /* ... */
    },
  };
}
```

### 錯誤處理

```typescript
try {
  const data = await apiService.proxies.getList(params);
  // 處理成功響應
} catch (error) {
  if (error instanceof ApiError) {
    // 處理 API 錯誤
    message.error(error.message);
  } else {
    // 處理其他錯誤
    message.error("未知錯誤");
  }
}
```

## 🧪 測試

### 單元測試

```typescript
import { render, screen, fireEvent } from "@testing-library/react";
import Component from "./Component";

describe("Component", () => {
  it("renders correctly", () => {
    render(<Component />);
    expect(screen.getByText("Expected Text")).toBeInTheDocument();
  });

  it("handles user interaction", () => {
    render(<Component />);
    fireEvent.click(screen.getByRole("button"));
    expect(mockHandler).toHaveBeenCalled();
  });
});
```

### 測試命令

```bash
# 運行所有測試
npm run test

# 運行測試並生成覆蓋率報告
npm run test:coverage

# 監聽模式運行測試
npm run test:watch
```

## 🚀 部署

### 構建生產版本

```bash
npm run build
```

### 環境配置

- **開發環境**: `npm run dev`
- **測試環境**: `npm run build:test`
- **生產環境**: `npm run build:prod`

### Docker 部署

```dockerfile
FROM node:16-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🔧 故障排除

### 常見問題

1. **依賴安裝失敗**

   ```bash
   # 清除緩存
   npm cache clean --force
   # 刪除 node_modules 重新安裝
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **TypeScript 錯誤**

   - 檢查類型定義是否正確
   - 確保所有依賴都有類型定義
   - 使用 `// @ts-ignore` 臨時忽略錯誤

3. **構建失敗**
   - 檢查環境變量配置
   - 確保所有依賴都已安裝
   - 查看構建日誌中的具體錯誤

### 性能優化

1. **代碼分割**

   ```typescript
   const LazyComponent = React.lazy(() => import("./Component"));
   ```

2. **圖片優化**

   - 使用 WebP 格式
   - 實現懶加載
   - 壓縮圖片大小

3. **Bundle 分析**
   ```bash
   npm run build:analyze
   ```

## 📚 相關文檔

- [React 官方文檔](https://reactjs.org/docs)
- [Ant Design 組件庫](https://ant.design/components/overview-cn)
- [Redux Toolkit 文檔](https://redux-toolkit.js.org/)
- [ECharts 圖表庫](https://echarts.apache.org/zh/index.html)
- [TypeScript 手冊](https://www.typescriptlang.org/docs/)

## 🤝 貢獻指南

1. Fork 項目
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 許可證

本項目採用 MIT 許可證 - 查看 [LICENSE](LICENSE) 文件了解詳情。
