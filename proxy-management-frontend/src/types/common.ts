/**
 * 通用類型定義
 */

// API響應接口
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp: number;
}

// 分頁響應接口
export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// 圖表數據接口
export interface ChartData {
  xAxis: string[];
  series: Array<{
    name: string;
    data: number[];
    type?: string;
    color?: string;
  }>;
}

// 地理分佈數據接口
export interface GeoDistribution {
  country: string;
  count: number;
  code: string;
}

// 主題配置接口
export interface ThemeConfig {
  primaryColor: string;
  layout: 'side' | 'top' | 'mix';
  theme: 'light' | 'dark' | 'auto';
  language: 'zh-TW' | 'zh-CN' | 'en';
  compact: boolean;
}

// WebSocket消息接口
export interface WebSocketMessage {
  type: string;
  payload: any;
  timestamp: number;
}