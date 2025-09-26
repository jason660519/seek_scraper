/**
 * 系統相關類型定義
 */

// 系統狀態接口
export interface SystemStatus {
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  networkSpeed: number;
  activeTasks: number;
  queueSize: number;
  errorRate: number;
  uptime: number;
}

// 任務隊列接口
export interface TaskQueue {
  waiting: number;
  running: number;
  completed: number;
  failed: number;
  total: number;
}

// 配置接口
export interface SystemConfig {
  scheduler: {
    fetchInterval: number;
    validateInterval: number;
    cleanupInterval: number;
    retryAttempts: number;
  };
  sources: {
    enabled: boolean;
    apiKeys: Record<string, string>;
    rateLimits: Record<string, number>;
    timeouts: Record<string, number>;
  };
  notifications: {
    webhookUrl?: string;
    emailConfig?: {
      host: string;
      port: number;
      secure: boolean;
      auth: {
        user: string;
        pass: string;
      };
    };
    triggers: string[];
  };
  export: {
    defaultFormat: string;
    namingRule: string;
    autoExport: boolean;
    retentionDays: number;
  };
}

// 錯誤日誌接口
export interface ErrorLog {
  id: string;
  level: 'error' | 'warn' | 'info';
  message: string;
  stack?: string;
  timestamp: Date;
  context?: Record<string, any>;
}

// 操作日誌接口
export interface OperationLog {
  id: string;
  userId: string;
  action: string;
  target: string;
  details?: Record<string, any>;
  timestamp: Date;
  ip?: string;
}