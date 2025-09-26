/**
 * 主應用組件
 * @author TRAE
 * @description 應用的根組件，配置路由和全局狀態
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import { Provider } from 'react-redux';
import { store } from './store';
import MainLayout from './layouts/MainLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ProxyManagement from './pages/ProxyManagement';
import SystemMonitor from './pages/SystemMonitor';
import Configuration from './pages/Configuration';
import { useAppSelector } from './hooks/redux';
import { selectTheme } from './store/slices/systemSlice';
import './i18n';
import './App.css';

/**
 * 受保護的路由組件
 * @description 檢查用戶是否已登錄，未登錄則重定向到登錄頁面
 */
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAppSelector((state) => state.auth);
  
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

/**
 * 應用內容組件
 * @description 包含路由配置和主佈局
 */
const AppContent: React.FC = () => {
  const appTheme = useAppSelector(selectTheme);

  return (
    <ConfigProvider
      theme={{
        algorithm: appTheme === 'dark' ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 8,
          wireframe: false,
        },
      }}
    >
      <Router>
        <Routes>
          {/* 登錄頁面 */}
          <Route path="/login" element={<Login />} />
          
          {/* 受保護的路由 */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="proxies" element={<ProxyManagement />} />
            <Route path="system" element={<SystemMonitor />} />
            <Route path="configuration" element={<Configuration />} />
          </Route>
          
          {/* 404 頁面 */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </ConfigProvider>
  );
};

/**
 * 主應用組件
 */
function App() {
  return (
    <Provider store={store}>
      <AppContent />
    </Provider>
  );
}

export default App;
