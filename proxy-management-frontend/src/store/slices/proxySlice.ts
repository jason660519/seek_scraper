/**
 * 代理管理狀態切片
 * @author TRAE
 * @description 管理代理列表、篩選條件和操作狀態
 */

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { Proxy, PaginatedResponse } from '../../types';
import { ProxyStatus, ProxyProtocol } from '../../types';

/**
 * 代理狀態接口
 */
interface ProxyState {
  proxies: Proxy[];
  loading: boolean;
  error: string | null;
  total: number;
  currentPage: number;
  pageSize: number;
  filters: {
    status?: ProxyStatus;
    protocol?: ProxyProtocol;
    country?: string;
    anonymity?: string;
    search?: string;
  };
  selectedProxies: string[];
  editingProxy: Proxy | null;
  showEditModal: boolean;
}

const initialState: ProxyState = {
  proxies: [],
  loading: false,
  error: null,
  total: 0,
  currentPage: 1,
  pageSize: 10,
  filters: {},
  selectedProxies: [],
  editingProxy: null,
  showEditModal: false
};

/**
 * 獲取代理列表
 */
export const fetchProxies = createAsyncThunk(
  'proxy/fetchProxies',
  async (params: { page?: number; pageSize?: number; filters?: any }) => {
    // 模擬 API 調用
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // 模擬數據
    const mockProxies: Proxy[] = [
      {
        id: '1',
        host: '192.168.1.100',
        port: 8080,
        protocol: ProxyProtocol.HTTP,
        status: ProxyStatus.VALID,
        country: 'US',
        city: 'New York',
        anonymity: 'High',
        responseTime: 1.2,
        lastChecked: new Date(),
        createdAt: new Date(),
        updatedAt: new Date()
      },
      {
        id: '2',
        host: '203.0.113.45',
        port: 3128,
        protocol: ProxyProtocol.SOCKS5,
        status: ProxyStatus.VALID,
        country: 'GB',
        city: 'London',
        anonymity: 'High',
        responseTime: 0.8,
        lastChecked: new Date(),
        createdAt: new Date(),
        updatedAt: new Date()
      },
      {
        id: '3',
        host: '198.51.100.25',
        port: 8080,
        protocol: ProxyProtocol.HTTP,
        status: ProxyStatus.INVALID,
        country: 'CA',
        city: 'Toronto',
        anonymity: 'Medium',
        responseTime: 2.5,
        lastChecked: new Date(),
        createdAt: new Date(),
        updatedAt: new Date()
      }
    ];
    
    return {
      items: mockProxies,
      total: mockProxies.length,
      page: params.page || 1,
      pageSize: params.pageSize || 10,
      totalPages: Math.ceil(mockProxies.length / (params.pageSize || 10))
    } as PaginatedResponse<Proxy>;
  }
);

/**
 * 驗證代理
 */
export const validateProxies = createAsyncThunk(
  'proxy/validateProxies',
  async (proxyIds: string[]) => {
    // 模擬 API 調用
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    return proxyIds.map(id => ({
      id,
      status: Math.random() > 0.3 ? ProxyStatus.VALID : ProxyStatus.INVALID,
      lastChecked: new Date()
    }));
  }
);

/**
 * 刪除代理
 */
export const deleteProxies = createAsyncThunk(
  'proxy/deleteProxies',
  async (proxyIds: string[]) => {
    // 模擬 API 調用
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return proxyIds;
  }
);

/**
 * 代理切片
 */
const proxySlice = createSlice({
  name: 'proxy',
  initialState,
  reducers: {
    /**
     * 設置篩選條件
     */
    setFilters: (state, action: PayloadAction<ProxyState['filters']>) => {
      state.filters = { ...state.filters, ...action.payload };
      state.currentPage = 1;
    },
    
    /**
     * 清除篩選條件
     */
    clearFilters: (state) => {
      state.filters = {};
      state.currentPage = 1;
    },
    
    /**
     * 設置當前頁面
     */
    setCurrentPage: (state, action: PayloadAction<number>) => {
      state.currentPage = action.payload;
    },
    
    /**
     * 設置頁面大小
     */
    setPageSize: (state, action: PayloadAction<number>) => {
      state.pageSize = action.payload;
      state.currentPage = 1;
    },
    
    /**
     * 選擇代理
     */
    selectProxies: (state, action: PayloadAction<string[]>) => {
      state.selectedProxies = action.payload;
    },
    
    /**
     * 切換代理選擇
     */
    toggleProxySelection: (state, action: PayloadAction<string>) => {
      const id = action.payload;
      const index = state.selectedProxies.indexOf(id);
      if (index > -1) {
        state.selectedProxies.splice(index, 1);
      } else {
        state.selectedProxies.push(id);
      }
    },
    
    /**
     * 全選/取消全選
     */
    toggleSelectAll: (state) => {
      if (state.selectedProxies.length === state.proxies.length) {
        state.selectedProxies = [];
      } else {
        state.selectedProxies = state.proxies.map(proxy => proxy.id);
      }
    },
    
    /**
     * 打開編輯模態框
     */
    openEditModal: (state, action: PayloadAction<Proxy | null>) => {
      state.editingProxy = action.payload;
      state.showEditModal = true;
    },
    
    /**
     * 關閉編輯模態框
     */
    closeEditModal: (state) => {
      state.editingProxy = null;
      state.showEditModal = false;
    },
    
    /**
     * 更新代理
     */
    updateProxy: (state, action: PayloadAction<Proxy>) => {
      const index = state.proxies.findIndex(p => p.id === action.payload.id);
      if (index !== -1) {
        state.proxies[index] = action.payload;
      }
    },
    
    /**
     * 添加代理
     */
    addProxy: (state, action: PayloadAction<Proxy>) => {
      state.proxies.unshift(action.payload);
      state.total++;
    }
  },
  extraReducers: (builder) => {
    builder
      // 獲取代理列表
      .addCase(fetchProxies.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProxies.fulfilled, (state, action) => {
        state.loading = false;
        state.proxies = action.payload.items;
        state.total = action.payload.total;
        state.currentPage = action.payload.page;
        state.pageSize = action.payload.pageSize;
      })
      .addCase(fetchProxies.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch proxies';
      })
      
      // 驗證代理
      .addCase(validateProxies.pending, (state) => {
        state.loading = true;
      })
      .addCase(validateProxies.fulfilled, (state, action) => {
        state.loading = false;
        action.payload.forEach(update => {
          const proxy = state.proxies.find(p => p.id === update.id);
          if (proxy) {
            proxy.status = update.status;
            proxy.lastChecked = update.lastChecked;
          }
        });
        state.selectedProxies = [];
      })
      .addCase(validateProxies.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Validation failed';
      })
      
      // 刪除代理
      .addCase(deleteProxies.pending, (state) => {
        state.loading = true;
      })
      .addCase(deleteProxies.fulfilled, (state, action) => {
        state.loading = false;
        state.proxies = state.proxies.filter(p => !action.payload.includes(p.id));
        state.total = state.proxies.length;
        state.selectedProxies = [];
      })
      .addCase(deleteProxies.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Deletion failed';
      });
  }
});

// 導出 actions
export const {
  setFilters,
  clearFilters,
  setCurrentPage,
  setPageSize,
  selectProxies,
  toggleProxySelection,
  toggleSelectAll,
  openEditModal,
  closeEditModal,
  updateProxy,
  addProxy
} = proxySlice.actions;

// 導出 selectors
export const selectProxyLoading = (state: { proxy: ProxyState }) => state.proxy.loading;
export const selectProxyError = (state: { proxy: ProxyState }) => state.proxy.error;
export const selectProxyTotal = (state: { proxy: ProxyState }) => state.proxy.total;
export const selectCurrentPage = (state: { proxy: ProxyState }) => state.proxy.currentPage;
export const selectPageSize = (state: { proxy: ProxyState }) => state.proxy.pageSize;
export const selectFilters = (state: { proxy: ProxyState }) => state.proxy.filters;
export const selectSelectedProxies = (state: { proxy: ProxyState }) => state.proxy.selectedProxies;
export const selectEditingProxy = (state: { proxy: ProxyState }) => state.proxy.editingProxy;
export const selectShowEditModal = (state: { proxy: ProxyState }) => state.proxy.showEditModal;

export default proxySlice.reducer;