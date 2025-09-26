/**
 * 認證狀態切片
 * @author TRAE
 * @description 管理用戶登入狀態和認證信息
 */

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

/**
 * 認證狀態接口
 */
interface AuthState {
  isAuthenticated: boolean;
  user: {
    username: string;
    token: string;
    expiresIn: number;
  } | null;
  loading: boolean;
  error: string | null;
}

/**
 * 登入參數接口
 */
interface LoginCredentials {
  username: string;
  password: string;
}

/**
 * 登入響應接口
 */
interface LoginResponse {
  username: string;
  token: string;
  expiresIn: number;
}

const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  loading: false,
  error: null
};

/**
 * 異步登入 thunk
 */
export const loginAsync = createAsyncThunk(
  'auth/login',
  async (credentials: LoginCredentials) => {
    // 模擬 API 調用
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    if (credentials.username === 'admin' && credentials.password === 'admin123') {
      return {
        username: credentials.username,
        token: 'mock-jwt-token-' + Date.now(),
        expiresIn: 3600
      };
    } else {
      throw new Error('Invalid credentials');
    }
  }
);

/**
 * 認證切片
 */
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    /**
     * 登入成功
     */
    login: (state, action: PayloadAction<LoginResponse>) => {
      state.isAuthenticated = true;
      state.user = action.payload;
      state.error = null;
      // 保存到 localStorage
      localStorage.setItem('auth', JSON.stringify(action.payload));
    },
    
    /**
     * 登出
     */
    logout: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.error = null;
      // 清除 localStorage
      localStorage.removeItem('auth');
    },
    
    /**
     * 從 localStorage 恢復認證狀態
     */
    restoreAuth: (state) => {
      const authData = localStorage.getItem('auth');
      if (authData) {
        try {
          const user = JSON.parse(authData);
          state.isAuthenticated = true;
          state.user = user;
        } catch (error) {
          localStorage.removeItem('auth');
        }
      }
    },
    
    /**
     * 清除錯誤
     */
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginAsync.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginAsync.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload;
        localStorage.setItem('auth', JSON.stringify(action.payload));
      })
      .addCase(loginAsync.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Login failed';
      });
  }
});

// 導出 actions
export const { login, logout, restoreAuth, clearError } = authSlice.actions;

// 導出 selectors
export const selectAuth = (state: { auth: AuthState }) => state.auth;
export const selectIsAuthenticated = (state: { auth: AuthState }) => state.auth.isAuthenticated;
export const selectCurrentUser = (state: { auth: AuthState }) => state.auth.user;
export const selectAuthLoading = (state: { auth: AuthState }) => state.auth.loading;
export const selectAuthError = (state: { auth: AuthState }) => state.auth.error;

export default authSlice.reducer;