/**
 * Redux Store 配置
 * @author TRAE
 * @description 配置 Redux Toolkit store，包含認證和代理狀態管理
 */

import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import proxyReducer from './slices/proxySlice';
import systemReducer from './slices/systemSlice';

/**
 * 創建 Redux store
 * @description 配置應用程序的狀態管理
 */
export const store = configureStore({
  reducer: {
    auth: authReducer,
    proxy: proxyReducer,
    system: systemReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
  devTools: (import.meta as any).env?.MODE !== 'production'
});

// 導出類型
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;