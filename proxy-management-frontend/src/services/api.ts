/**
 * API 服務
 * @author TRAE
 * @description 管理所有 API 請求和響應處理
 */

import axios from 'axios';
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import type { ApiResponse, Proxy, ProxyStatistics, SystemStatus, SystemConfig, User } from '../types';

/**
 * API 錯誤類
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * API 服務類
 */
class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  /**
   * 設置請求和響應攔截器
   */
  private setupInterceptors(): void {
    // 請求攔截器
    this.client.interceptors.request.use(
      (config) => {
        // 添加認證 token
        const auth = localStorage.getItem('auth');
        if (auth) {
          try {
            const authData = JSON.parse(auth);
            config.headers.Authorization = `Bearer ${authData.token}`;
          } catch (error) {
            console.error('Failed to parse auth data:', error);
          }
        }
        
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 響應攔截器
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error: AxiosError) => {
        if (error.response) {
          // 服務器響應錯誤
          const errorMessage = typeof error.response.data === 'object' && error.response.data !== null 
            ? (error.response.data as any).message || 'Request failed'
            : 'Request failed';
          const apiError = new ApiError(
            errorMessage,
            error.response.status,
            error.response.data
          );
          
          // 處理特定錯誤碼
          if (error.response.status === 401) {
            // 未授權，清除本地認證信息
            localStorage.removeItem('auth');
            window.location.href = '/login';
          }
          
          return Promise.reject(apiError);
        } else if (error.request) {
          // 請求發送失敗
          return Promise.reject(new ApiError('Network error', 0));
        } else {
          // 其他錯誤
          return Promise.reject(new ApiError(error.message));
        }
      }
    );
  }

  /**
   * GET 請求
   */
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<ApiResponse<T>>(url, config);
    if (response.data.data === undefined) {
      throw new ApiError('No data in response', response.status || 0, response.data);
    }
    return response.data.data;
  }

  /**
   * POST 請求
   */
  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<ApiResponse<T>>(url, data, config);
    if (response.data.data === undefined) {
      throw new ApiError('No data in response', response.status || 0, response.data);
    }
    return response.data.data;
  }

  /**
   * PUT 請求
   */
  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<ApiResponse<T>>(url, data, config);
    if (response.data.data === undefined) {
      throw new ApiError('No data in response', response.status || 0, response.data);
    }
    return response.data.data;
  }

  /**
   * DELETE 請求
   */
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<ApiResponse<T>>(url, config);
    if (response.data.data === undefined) {
      throw new ApiError('No data in response', response.status || 0, response.data);
    }
    return response.data.data;
  }

  /**
   * 認證相關 API
   */
  auth = {
    /**
     * 登入
     */
    login: async (username: string, password: string): Promise<User> => {
      return this.post<User>('/auth/login', { username, password });
    },

    /**
     * 登出
     */
    logout: async (): Promise<void> => {
      return this.post('/auth/logout');
    },

    /**
     * 獲取用戶信息
     */
    getUser: async (): Promise<User> => {
      return this.get<User>('/auth/user');
    }
  };

  /**
   * 代理管理相關 API
   */
  proxies = {
    /**
     * 獲取代理列表
     */
    getList: async (params: {
      page?: number;
      pageSize?: number;
      status?: string;
      protocol?: string;
      country?: string;
      search?: string;
    } = {}): Promise<{ data: Proxy[]; total: number }> => {
      return this.get('/proxies', { params });
    },

    /**
     * 獲取代理詳情
     */
    getById: async (id: string): Promise<Proxy> => {
      return this.get(`/proxies/${id}`);
    },

    /**
     * 創建代理
     */
    create: async (proxy: Partial<Proxy>): Promise<Proxy> => {
      return this.post('/proxies', proxy);
    },

    /**
     * 更新代理
     */
    update: async (id: string, proxy: Partial<Proxy>): Promise<Proxy> => {
      return this.put(`/proxies/${id}`, proxy);
    },

    /**
     * 刪除代理
     */
    delete: async (id: string): Promise<void> => {
      return this.delete(`/proxies/${id}`);
    },

    /**
     * 批量刪除代理
     */
    deleteMany: async (ids: string[]): Promise<void> => {
      return this.post('/proxies/batch-delete', { ids });
    },

    /**
     * 驗證代理
     */
    validate: async (ids: string[]): Promise<void> => {
      return this.post('/proxies/validate', { ids });
    },

    /**
     * 批量驗證代理
     */
    validateAll: async (): Promise<void> => {
      return this.post('/proxies/validate-all');
    },

    /**
     * 導出代理
     */
    export: async (format: 'csv' | 'json' | 'txt', filters?: any): Promise<Blob> => {
      const response = await this.client.post('/proxies/export', { format, filters }, {
        responseType: 'blob'
      });
      return response.data;
    },

    /**
     * 導入代理
     */
    import: async (file: File): Promise<void> => {
      const formData = new FormData();
      formData.append('file', file);
      
      return this.post('/proxies/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    }
  };

  /**
   * 統計數據相關 API
   */
  statistics = {
    /**
     * 獲取代理統計數據
     */
    getProxyStats: async (): Promise<ProxyStatistics> => {
      return this.get('/statistics/proxy');
    },

    /**
     * 獲取代理趨勢數據
     */
    getProxyTrends: async (days: number = 7): Promise<any> => {
      return this.get('/statistics/proxy-trends', { params: { days } });
    },

    /**
     * 獲取地理分布數據
     */
    getGeoDistribution: async (): Promise<any> => {
      return this.get('/statistics/geo-distribution');
    },

    /**
     * 獲取系統使用統計
     */
    getSystemStats: async (): Promise<any> => {
      return this.get('/statistics/system');
    }
  };

  /**
   * 系統管理相關 API
   */
  system = {
    /**
     * 獲取系統狀態
     */
    getStatus: async (): Promise<SystemStatus> => {
      return this.get('/system/status');
    },

    /**
     * 獲取系統配置
     */
    getConfig: async (): Promise<SystemConfig> => {
      return this.get('/system/config');
    },

    /**
     * 更新系統配置
     */
    updateConfig: async (config: Partial<SystemConfig>): Promise<SystemConfig> => {
      return this.put('/system/config', config);
    },

    /**
     * 重啟系統
     */
    restart: async (): Promise<void> => {
      return this.post('/system/restart');
    },

    /**
     * 獲取任務隊列
     */
    getTaskQueue: async (): Promise<any[]> => {
      return this.get('/system/tasks');
    },

    /**
     * 取消任務
     */
    cancelTask: async (taskId: string): Promise<void> => {
      return this.post(`/system/tasks/${taskId}/cancel`);
    },

    /**
     * 獲取系統日誌
     */
    getLogs: async (type: 'error' | 'operation', limit: number = 100): Promise<any[]> => {
      return this.get(`/system/logs/${type}`, { params: { limit } });
    }
  };
}

// 創建 API 服務實例
export const apiService = new ApiService();

export default apiService;