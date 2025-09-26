# Proxy Management Frontend - 性能優化指南

## 📋 目錄

- [性能監控](#性能監控)
- [代碼優化](#代碼優化)
- [資源優化](#資源優化)
- [網絡優化](#網絡優化)
- [渲染優化](#渲染優化)
- [內存優化](#內存優化)
- [最佳實踐](#最佳實踐)

## 📊 性能監控

### 性能指標

1. **Core Web Vitals**

   - LCP (Largest Contentful Paint): < 2.5s
   - FID (First Input Delay): < 100ms
   - CLS (Cumulative Layout Shift): < 0.1

2. **應用性能指標**
   - 首屏加載時間: < 3s
   - 路由切換時間: < 500ms
   - 組件渲染時間: < 100ms

### 性能監控工具

```typescript
// 性能監控 Hook
import { useEffect } from "react";

export const usePerformanceMonitor = () => {
  useEffect(() => {
    // 監控頁面加載時間
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === "navigation") {
          console.log(
            "Page load time:",
            entry.loadEventEnd - entry.loadEventStart
          );
        }
      }
    });

    observer.observe({ entryTypes: ["navigation"] });

    return () => observer.disconnect();
  }, []);
};
```

## 🚀 代碼優化

### 1. 組件優化

#### React.memo 使用

```typescript
import React, { memo } from "react";

interface Props {
  data: any[];
  onItemClick: (id: string) => void;
}

const ExpensiveComponent = memo<Props>(
  ({ data, onItemClick }) => {
    return (
      <div>
        {data.map((item) => (
          <div key={item.id} onClick={() => onItemClick(item.id)}>
            {item.name}
          </div>
        ))}
      </div>
    );
  },
  (prevProps, nextProps) => {
    // 自定義比較函數
    return prevProps.data.length === nextProps.data.length;
  }
);
```

#### useMemo 和 useCallback

```typescript
import React, { useMemo, useCallback } from "react";

const OptimizedComponent = ({ data, filter }) => {
  // 緩存計算結果
  const filteredData = useMemo(() => {
    return data.filter((item) => item.status === filter);
  }, [data, filter]);

  // 緩存回調函數
  const handleClick = useCallback((id: string) => {
    // 處理點擊事件
  }, []);

  return (
    <div>
      {filteredData.map((item) => (
        <div key={item.id} onClick={() => handleClick(item.id)}>
          {item.name}
        </div>
      ))}
    </div>
  );
};
```

### 2. 狀態管理優化

#### 選擇器優化

```typescript
import { createSelector } from "@reduxjs/toolkit";

// 使用 createSelector 避免不必要的重新計算
const selectFilteredProxies = createSelector(
  [
    (state: RootState) => state.proxy.data,
    (state: RootState) => state.proxy.filter,
  ],
  (proxies, filter) => {
    return proxies.filter((proxy) => proxy.status === filter);
  }
);

// 在組件中使用
const filteredProxies = useAppSelector(selectFilteredProxies);
```

#### 狀態正規化

```typescript
interface ProxyState {
  entities: Record<string, Proxy>;
  ids: string[];
  loading: boolean;
  error: string | null;
}

// 使用正規化狀態結構提高查詢效率
const selectProxyById = (state: RootState, id: string) =>
  state.proxy.entities[id];
```

### 3. 異步操作優化

#### 請求去重

```typescript
class RequestDeduplicator {
  private pendingRequests = new Map<string, Promise<any>>();

  async request<T>(key: string, requestFn: () => Promise<T>): Promise<T> {
    if (this.pendingRequests.has(key)) {
      return this.pendingRequests.get(key)!;
    }

    const promise = requestFn().finally(() => {
      this.pendingRequests.delete(key);
    });

    this.pendingRequests.set(key, promise);
    return promise;
  }
}

const deduplicator = new RequestDeduplicator();

// 使用去重器
const fetchProxy = (id: string) =>
  deduplicator.request(`proxy-${id}`, () => apiService.proxies.getById(id));
```

#### 請求緩存

```typescript
class RequestCache {
  private cache = new Map<string, { data: any; timestamp: number }>();
  private ttl = 5 * 60 * 1000; // 5分鐘

  get(key: string) {
    const item = this.cache.get(key);
    if (item && Date.now() - item.timestamp < this.ttl) {
      return item.data;
    }
    this.cache.delete(key);
    return null;
  }

  set(key: string, data: any) {
    this.cache.set(key, { data, timestamp: Date.now() });
  }
}
```

## 📦 資源優化

### 1. 代碼分割

#### 路由級分割

```typescript
import { lazy, Suspense } from "react";
import { Loading } from "../components/Loading";

const Dashboard = lazy(() => import("../pages/Dashboard"));
const ProxyManagement = lazy(() => import("../pages/ProxyManagement"));
const SystemMonitor = lazy(() => import("../pages/SystemMonitor"));

const App = () => (
  <Suspense fallback={<Loading />}>
    <Routes>
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/proxies" element={<ProxyManagement />} />
      <Route path="/monitor" element={<SystemMonitor />} />
    </Routes>
  </Suspense>
);
```

#### 組件級分割

```typescript
const HeavyChart = lazy(() => import("../components/HeavyChart"));

const Dashboard = () => (
  <div>
    <Suspense fallback={<div>Loading chart...</div>}>
      <HeavyChart />
    </Suspense>
  </div>
);
```

### 2. 圖片優化

#### 圖片懶加載

```typescript
import { useState, useRef, useEffect } from "react";

const LazyImage = ({ src, alt, ...props }) => {
  const [loaded, setLoaded] = useState(false);
  const [inView, setInView] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <img
      ref={imgRef}
      src={inView ? src : undefined}
      alt={alt}
      onLoad={() => setLoaded(true)}
      style={{ opacity: loaded ? 1 : 0 }}
      {...props}
    />
  );
};
```

#### 圖片壓縮

```typescript
// 使用 WebP 格式
const getOptimizedImageUrl = (url: string) => {
  const supportsWebP =
    document
      .createElement("canvas")
      .toDataURL("image/webp")
      .indexOf("data:image/webp") === 0;

  return supportsWebP ? url.replace(/\.(jpg|png)$/, ".webp") : url;
};
```

### 3. 字體優化

```css
/* 字體預加載 */
@font-face {
  font-family: "CustomFont";
  src: url("./fonts/custom-font.woff2") format("woff2");
  font-display: swap; /* 優化字體加載 */
}

/* 字體子集化 */
@font-face {
  font-family: "CustomFont";
  src: url("./fonts/custom-font-subset.woff2") format("woff2");
  unicode-range: U+4E00-9FFF; /* 中文字符範圍 */
}
```

## 🌐 網絡優化

### 1. HTTP/2 優化

```typescript
// 資源提示
const ResourceHints = () => (
  <>
    <link rel="preconnect" href="https://api.example.com" />
    <link rel="dns-prefetch" href="https://cdn.example.com" />
    <link
      rel="preload"
      href="/fonts/main.woff2"
      as="font"
      type="font/woff2"
      crossOrigin="anonymous"
    />
  </>
);
```

### 2. 請求優化

#### 請求合併

```typescript
class RequestBatcher {
  private batch: Array<{ key: string; request: () => Promise<any> }> = [];
  private timeout: NodeJS.Timeout | null = null;

  add<T>(key: string, request: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.batch.push({
        key,
        request: async () => {
          try {
            const result = await request();
            resolve(result);
            return result;
          } catch (error) {
            reject(error);
            throw error;
          }
        },
      });

      if (this.timeout) {
        clearTimeout(this.timeout);
      }

      this.timeout = setTimeout(() => {
        this.flush();
      }, 100); // 100ms 內合併請求
    });
  }

  private async flush() {
    const batch = this.batch.splice(0);
    // 執行批量請求
    await Promise.all(batch.map((item) => item.request()));
  }
}
```

#### 請求優先級

```typescript
// 關鍵資源優先加載
const loadCriticalResources = async () => {
  const criticalPromises = [
    import("./components/Header"),
    import("./components/Navigation"),
    import("./styles/critical.css"),
  ];

  await Promise.all(criticalPromises);
};

// 非關鍵資源延遲加載
const loadNonCriticalResources = () => {
  setTimeout(() => {
    import("./components/Footer");
    import("./components/Sidebar");
  }, 1000);
};
```

## 🎨 渲染優化

### 1. 虛擬滾動

```typescript
import { FixedSizeList as List } from "react-window";

const VirtualizedList = ({ items }) => (
  <List height={600} itemCount={items.length} itemSize={50} itemData={items}>
    {({ index, style, data }) => <div style={style}>{data[index].name}</div>}
  </List>
);
```

### 2. 防抖和節流

```typescript
import { useCallback, useRef } from "react";

// 防抖 Hook
export const useDebounce = (callback: Function, delay: number) => {
  const timeoutRef = useRef<NodeJS.Timeout>();

  return useCallback(
    (...args: any[]) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(() => {
        callback(...args);
      }, delay);
    },
    [callback, delay]
  );
};

// 節流 Hook
export const useThrottle = (callback: Function, delay: number) => {
  const lastCallRef = useRef<number>(0);

  return useCallback(
    (...args: any[]) => {
      const now = Date.now();
      if (now - lastCallRef.current >= delay) {
        lastCallRef.current = now;
        callback(...args);
      }
    },
    [callback, delay]
  );
};
```

### 3. 動畫優化

```css
/* 使用 transform 和 opacity 進行動畫 */
.optimized-animation {
  transform: translateX(0);
  opacity: 1;
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.optimized-animation:hover {
  transform: translateX(10px);
  opacity: 0.8;
}

/* 使用 will-change 提示瀏覽器 */
.will-animate {
  will-change: transform, opacity;
}
```

## 💾 內存優化

### 1. 內存洩漏防護

```typescript
import { useEffect, useRef } from "react";

export const useCleanup = () => {
  const cleanupRef = useRef<(() => void)[]>([]);

  const addCleanup = (cleanup: () => void) => {
    cleanupRef.current.push(cleanup);
  };

  useEffect(() => {
    return () => {
      cleanupRef.current.forEach((cleanup) => cleanup());
    };
  }, []);

  return addCleanup;
};

// 使用示例
const Component = () => {
  const addCleanup = useCleanup();

  useEffect(() => {
    const timer = setInterval(() => {
      // 定時器邏輯
    }, 1000);

    addCleanup(() => clearInterval(timer));
  }, [addCleanup]);
};
```

### 2. 對象池模式

```typescript
class ObjectPool<T> {
  private pool: T[] = [];
  private createFn: () => T;

  constructor(createFn: () => T, initialSize: number = 10) {
    this.createFn = createFn;
    for (let i = 0; i < initialSize; i++) {
      this.pool.push(createFn());
    }
  }

  get(): T {
    return this.pool.pop() || this.createFn();
  }

  release(obj: T) {
    this.pool.push(obj);
  }
}

// 使用對象池
const proxyPool = new ObjectPool(() => ({}), 100);
const proxy = proxyPool.get();
// 使用完畢後歸還
proxyPool.release(proxy);
```

## 🏆 最佳實踐

### 1. 性能預算

```json
{
  "budget": {
    "bundle": {
      "javascript": "500kb",
      "css": "100kb",
      "images": "1mb"
    },
    "performance": {
      "first-contentful-paint": "1.5s",
      "largest-contentful-paint": "2.5s",
      "first-input-delay": "100ms"
    }
  }
}
```

### 2. 性能監控

```typescript
// 性能監控服務
class PerformanceMonitor {
  private metrics: Map<string, number> = new Map();

  startTiming(name: string) {
    this.metrics.set(name, performance.now());
  }

  endTiming(name: string) {
    const startTime = this.metrics.get(name);
    if (startTime) {
      const duration = performance.now() - startTime;
      console.log(`${name}: ${duration}ms`);
      this.metrics.delete(name);
      return duration;
    }
  }

  measureWebVitals() {
    // 測量 Core Web Vitals
    new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === "largest-contentful-paint") {
          console.log("LCP:", entry.startTime);
        }
      }
    }).observe({ entryTypes: ["largest-contentful-paint"] });
  }
}
```

### 3. 性能測試

```typescript
// 性能測試工具
export const performanceTest = async (
  testName: string,
  testFn: () => Promise<void>
) => {
  const start = performance.now();
  await testFn();
  const end = performance.now();

  console.log(`${testName}: ${end - start}ms`);

  if (end - start > 1000) {
    console.warn(`${testName} took too long: ${end - start}ms`);
  }
};

// 使用示例
await performanceTest("Component Render", async () => {
  render(<ExpensiveComponent data={largeDataset} />);
});
```

### 4. 持續優化

1. **定期性能審計**

   - 使用 Lighthouse 進行性能審計
   - 監控 Core Web Vitals
   - 分析 Bundle 大小

2. **用戶體驗監控**

   - 收集真實用戶性能數據
   - 監控錯誤率和崩潰率
   - 分析用戶行為模式

3. **優化迭代**
   - 設定性能目標
   - 定期回顧和調整
   - 持續改進優化策略

通過遵循這些性能優化指南，可以顯著提升 Proxy Management Frontend 的應用性能和用戶體驗。
