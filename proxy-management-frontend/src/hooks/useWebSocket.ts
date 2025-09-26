/**
 * WebSocket Hook
 * @author TRAE
 * @description 管理WebSocket連接和實時數據更新
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { message } from 'antd';
import { wsService, ConnectionStatus } from '../services/websocket';
import { useAppDispatch } from './redux';
import {
  updateSystemStatus,
  addOperationLog
} from '../store/slices/systemSlice';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  maxReconnectAttempts?: number;
}

/**
 * WebSocket Hook
 */
export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const {
    autoConnect = true,
    maxReconnectAttempts = 5
  } = options;

  const dispatch = useAppDispatch();
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>(ConnectionStatus.DISCONNECTED);
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // 連接WebSocket
  const connect = useCallback(() => {
    try {
      wsService.connect();
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      message.error('WebSocket連接失敗');
    }
  }, []);

  // 斷開WebSocket
  const disconnect = useCallback(() => {
    wsService.disconnect();
    setReconnectAttempts(0);
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  // 發送消息
  const sendMessage = useCallback((message: any) => {
    wsService.send(message);
  }, []);

  // 處理代理狀態更新
  const handleProxyStatusUpdate = useCallback((data: any) => {
    console.log('Proxy status update:', data);
    // TODO: 實現代理狀態更新邏輯
  }, []);

  // 處理新增代理
  const handleProxyAdded = useCallback((data: any) => {
    console.log('Proxy added:', data);
    // TODO: 實現新增代理邏輯
  }, []);

  // 處理刪除代理
  const handleProxyDeleted = useCallback((data: any) => {
    console.log('Proxy deleted:', data);
    // TODO: 實現刪除代理邏輯
  }, []);

  // 處理系統狀態更新
  const handleSystemStatusUpdate = useCallback((data: any) => {
    dispatch(updateSystemStatus(data));
  }, [dispatch]);

  // 處理系統日誌
  const handleSystemLog = useCallback((data: any) => {
    dispatch(addOperationLog({
      id: `log-${Date.now()}`,
      timestamp: new Date(),
      userId: 'system',
      action: 'system_log',
      target: 'system',
      details: data
    }));
  }, [dispatch]);

  // 處理錯誤通知
  const handleErrorNotification = useCallback((data: any) => {
    message.error(data.message || '系統錯誤');
  }, []);

  // 處理任務更新
  const handleTaskUpdate = useCallback((data: any) => {
    console.log('Task update:', data);
    // 可以在這裡處理任務更新邏輯
  }, []);

  // 處理連接狀態變化
  const handleStatusChange = useCallback((status: ConnectionStatus) => {
    setConnectionStatus(status);
    setIsConnected(status === ConnectionStatus.CONNECTED);
    
    if (status === ConnectionStatus.CONNECTED) {
      setReconnectAttempts(0);
      message.success('WebSocket連接成功');
    } else if (status === ConnectionStatus.DISCONNECTED) {
      message.warning('WebSocket連接已斷開');
    } else if (status === ConnectionStatus.ERROR) {
      message.error('WebSocket連接錯誤');
    }
  }, []);

  // 處理最大重連嘗試次數達到
  const handleMaxReconnectAttemptsReached = useCallback(() => {
    message.error('WebSocket重連失敗，請檢查網絡連接');
    setReconnectAttempts(maxReconnectAttempts);
  }, [maxReconnectAttempts]);

  // 設置事件監聽器
  useEffect(() => {
    // 連接狀態變化
    wsService.on('statusChange', handleStatusChange);
    
    // 代理相關事件
    wsService.on('proxyStatusUpdate', handleProxyStatusUpdate);
    wsService.on('proxyAdded', handleProxyAdded);
    wsService.on('proxyDeleted', handleProxyDeleted);
    
    // 系統相關事件
    wsService.on('systemStatusUpdate', handleSystemStatusUpdate);
    wsService.on('systemLog', handleSystemLog);
    wsService.on('errorNotification', handleErrorNotification);
    
    // 任務相關事件
    wsService.on('taskUpdate', handleTaskUpdate);
    
    // 重連相關事件
    wsService.on('maxReconnectAttemptsReached', handleMaxReconnectAttemptsReached);

    return () => {
      // 清理事件監聽器
      wsService.off('statusChange', handleStatusChange);
      wsService.off('proxyStatusUpdate', handleProxyStatusUpdate);
      wsService.off('proxyAdded', handleProxyAdded);
      wsService.off('proxyDeleted', handleProxyDeleted);
      wsService.off('systemStatusUpdate', handleSystemStatusUpdate);
      wsService.off('systemLog', handleSystemLog);
      wsService.off('errorNotification', handleErrorNotification);
      wsService.off('taskUpdate', handleTaskUpdate);
      wsService.off('maxReconnectAttemptsReached', handleMaxReconnectAttemptsReached);
    };
  }, [
    handleStatusChange,
    handleProxyStatusUpdate,
    handleProxyAdded,
    handleProxyDeleted,
    handleSystemStatusUpdate,
    handleSystemLog,
    handleErrorNotification,
    handleTaskUpdate,
    handleMaxReconnectAttemptsReached
  ]);

  // 自動連接
  useEffect(() => {
    if (autoConnect && !isConnected) {
      connect();
    }
  }, [autoConnect, isConnected, connect]);

  // 組件卸載時斷開連接
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  // 手動重連
  const reconnect = useCallback(() => {
    if (reconnectAttempts < maxReconnectAttempts) {
      setReconnectAttempts(prev => prev + 1);
      connect();
    } else {
      message.error('已達到最大重連次數');
    }
  }, [reconnectAttempts, maxReconnectAttempts, connect]);

  return {
    connectionStatus,
    isConnected,
    reconnectAttempts,
    maxReconnectAttempts,
    connect,
    disconnect,
    reconnect,
    sendMessage
  };
};

export default useWebSocket;
