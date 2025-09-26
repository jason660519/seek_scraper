/**
 * 系統監控狀態切片
 * @author TRAE
 * @description 管理系統狀態、任務隊列和實時監控數據
 */

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { SystemStatus, TaskQueue, ErrorLog, OperationLog, ChartData } from '../../types';

/**
 * 系統狀態接口
 */
interface SystemState {
  status: SystemStatus | null;
  taskQueue: TaskQueue[];
  errorLogs: ErrorLog[];
  operationLogs: OperationLog[];
  loading: boolean;
  error: string | null;
  theme: 'light' | 'dark';
  systemMetrics: {
    cpuUsage: ChartData[];
    memoryUsage: ChartData[];
    networkTraffic: ChartData[];
  };
}

const initialState: SystemState = {
  status: null,
  taskQueue: [],
  errorLogs: [],
  operationLogs: [],
  loading: false,
  error: null,
  theme: 'light',
  systemMetrics: {
    cpuUsage: [],
    memoryUsage: [],
    networkTraffic: []
  }
};

/**
 * 獲取系統狀態
 */
export const fetchSystemStatus = createAsyncThunk(
  'system/fetchStatus',
  async () => {
    // 模擬 API 調用
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return {
      cpuUsage: 45.2,
      memoryUsage: 68.5,
      diskUsage: 32.1,
      networkSpeed: 1024.5,
      activeTasks: 5,
      queueSize: 12,
      errorRate: 0.8,
      uptime: 9240 // 2h 34m in seconds
    } as SystemStatus;
  }
);

/**
 * 獲取任務隊列
 */
export const fetchTaskQueue = createAsyncThunk(
  'system/fetchTaskQueue',
  async () => {
    // 模擬 API 調用
    await new Promise(resolve => setTimeout(resolve, 600));
    
    return [
      {
        waiting: 2,
        running: 1,
        completed: 156,
        failed: 3,
        total: 162
      },
      {
        waiting: 0,
        running: 0,
        completed: 89,
        failed: 1,
        total: 90
      }
    ] as TaskQueue[];
  }
);

/**
 * 獲取系統指標
 */
export const fetchSystemMetrics = createAsyncThunk(
  'system/fetchMetrics',
  async (metric: 'cpu' | 'memory' | 'network') => {
    // 模擬 API 調用
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // 生成模擬數據
    const xAxis: string[] = [];
    const seriesData: number[] = [];
    const now = Date.now();
    
    for (let i = 29; i >= 0; i--) {
      const time = new Date(now - i * 60000); // 每分鐘一個數據點
      let value: number;
      
      switch (metric) {
        case 'cpu':
          value = 30 + Math.random() * 40; // 30-70%
          break;
        case 'memory':
          value = 50 + Math.random() * 30; // 50-80%
          break;
        case 'network':
          value = 100 + Math.random() * 200; // 100-300 KB/s
          break;
        default:
          value = 0;
      }
      
      xAxis.push(time.toISOString());
      seriesData.push(Math.round(value * 100) / 100);
    }
    
    return { 
      metric, 
      data: {
        xAxis,
        series: [{
          name: metric,
          data: seriesData,
          type: 'line'
        }]
      }
    };
  }
);

/**
 * 獲取錯誤日誌
 */
export const fetchErrorLogs = createAsyncThunk(
  'system/fetchErrorLogs',
  async () => {
    // 模擬 API 調用
    await new Promise(resolve => setTimeout(resolve, 400));
    
    return [
      {
        id: 'error-1',
        timestamp: new Date(Date.now() - 600000),
        level: 'error',
        message: 'Connection timeout to proxy server',
        stack: 'Failed to connect to proxy 192.168.1.100:8080',
        context: { component: 'ProxyValidator' }
      },
      {
        id: 'error-2',
        timestamp: new Date(Date.now() - 1200000),
        level: 'warn',
        message: 'High memory usage detected',
        stack: 'Memory usage: 85.3%',
        context: { component: 'SystemMonitor' }
      },
      {
        id: 'error-3',
        timestamp: new Date(Date.now() - 1800000),
        level: 'info',
        message: 'Proxy validation completed',
        stack: 'Validated 156 proxies, 142 valid',
        context: { component: 'ProxyValidator' }
      }
    ] as ErrorLog[];
  }
);

/**
 * 獲取操作日誌
 */
export const fetchOperationLogs = createAsyncThunk(
  'system/fetchOperationLogs',
  async () => {
    // 模擬 API 調用
    await new Promise(resolve => setTimeout(resolve, 400));
    
    return [
      {
        id: 'op-1',
        timestamp: new Date(Date.now() - 300000),
        userId: 'admin',
        action: 'proxy_validation',
        target: 'proxy-123',
        details: {
          result: 'success',
          message: 'Validated proxy 192.168.1.100:8080'
        }
      },
      {
        id: 'op-2',
        timestamp: new Date(Date.now() - 600000),
        userId: 'admin',
        action: 'proxy_deletion',
        target: 'proxy-456',
        details: {
          result: 'success',
          message: 'Deleted invalid proxy'
        }
      },
      {
        id: 'op-3',
        timestamp: new Date(Date.now() - 900000),
        userId: 'admin',
        action: 'config_update',
        target: 'system',
        details: {
          result: 'success',
          message: 'Updated proxy validation timeout'
        }
      }
    ] as OperationLog[];
  }
);

/**
 * 系統監控切片
 */
const systemSlice = createSlice({
  name: 'system',
  initialState,
  reducers: {
    /**
     * 更新系統狀態
     */
    updateSystemStatus: (state, action: PayloadAction<SystemStatus>) => {
      state.status = action.payload;
    },
    
    /**
     * 更新任務隊列
     */
    updateTaskQueue: (state, action: PayloadAction<TaskQueue[]>) => {
      state.taskQueue = action.payload;
    },
    
    /**
     * 添加錯誤日誌
     */
    addErrorLog: (state, action: PayloadAction<ErrorLog>) => {
      state.errorLogs.unshift(action.payload);
      // 保持最多 100 條記錄
      if (state.errorLogs.length > 100) {
        state.errorLogs = state.errorLogs.slice(0, 100);
      }
    },
    
    /**
     * 添加操作日誌
     */
    addOperationLog: (state, action: PayloadAction<OperationLog>) => {
      state.operationLogs.unshift(action.payload);
      // 保持最多 100 條記錄
      if (state.operationLogs.length > 100) {
        state.operationLogs = state.operationLogs.slice(0, 100);
      }
    },
    
    /**
     * 清除錯誤
     */
    clearError: (state) => {
      state.error = null;
    },
    
    /**
     * 切換主題
     */
    toggleTheme: (state) => {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
    },
    
    /**
     * 設置主題
     */
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      // 獲取系統狀態
      .addCase(fetchSystemStatus.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSystemStatus.fulfilled, (state, action) => {
        state.loading = false;
        state.status = action.payload;
      })
      .addCase(fetchSystemStatus.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch system status';
      })
      
      // 獲取任務隊列
      .addCase(fetchTaskQueue.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchTaskQueue.fulfilled, (state, action) => {
        state.loading = false;
        state.taskQueue = action.payload;
      })
      .addCase(fetchTaskQueue.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch task queue';
      })
      
      // 獲取系統指標
      .addCase(fetchSystemMetrics.fulfilled, (state, action) => {
        const { metric, data } = action.payload;
        switch (metric) {
          case 'cpu':
            state.systemMetrics.cpuUsage = [data as ChartData];
            break;
          case 'memory':
            state.systemMetrics.memoryUsage = [data as ChartData];
            break;
          case 'network':
            state.systemMetrics.networkTraffic = [data as ChartData];
            break;
        }
      })
      
      // 獲取錯誤日誌
      .addCase(fetchErrorLogs.fulfilled, (state, action) => {
        state.errorLogs = action.payload;
      })
      
      // 獲取操作日誌
      .addCase(fetchOperationLogs.fulfilled, (state, action) => {
        state.operationLogs = action.payload;
      });
  }
});

// 導出 actions
export const { 
  updateSystemStatus, 
  updateTaskQueue, 
  addErrorLog, 
  addOperationLog, 
  clearError,
  toggleTheme,
  setTheme
} = systemSlice.actions;

// 導出 selectors
export const selectSystemStatus = (state: { system: SystemState }) => state.system.status;
export const selectTaskQueue = (state: { system: SystemState }) => state.system.taskQueue;
export const selectErrorLogs = (state: { system: SystemState }) => state.system.errorLogs;
export const selectOperationLogs = (state: { system: SystemState }) => state.system.operationLogs;
export const selectSystemLoading = (state: { system: SystemState }) => state.system.loading;
export const selectSystemError = (state: { system: SystemState }) => state.system.error;
export const selectSystemMetrics = (state: { system: SystemState }) => state.system.systemMetrics;
export const selectTheme = (state: { system: SystemState }) => state.system.theme;

export default systemSlice.reducer;