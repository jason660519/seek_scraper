/**
 * WebSocket 服務
 * @author TRAE
 * @description 管理 WebSocket 連接和實時通信
 */

import type { WebSocketMessage } from '../types';

/**
 * WebSocket 連接狀態枚舉
 */
export enum ConnectionStatus {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  ERROR = 'error'
}

/**
 * WebSocket 服務類
 */
class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000;
  private status: ConnectionStatus = ConnectionStatus.DISCONNECTED;
  private messageQueue: any[] = [];
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private listeners: Record<string, Function[]> = {};

  constructor(url: string) {
    this.url = url;
  }

  /**
   * 添加事件監聽器
   */
  on(event: string, listener: Function): void {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(listener);
  }

  /**
   * 移除事件監聽器
   */
  off(event: string, listener: Function): void {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(l => l !== listener);
    }
  }

  /**
   * 觸發事件
   */
  emit(event: string, ...args: any[]): void {
    if (this.listeners[event]) {
      this.listeners[event].forEach(listener => {
        try {
          listener(...args);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      });
    }
  }

  /**
   * 連接到 WebSocket 服務器
   */
  connect(): void {
    if (this.ws && this.status === ConnectionStatus.CONNECTED) {
      console.log('WebSocket already connected');
      return;
    }

    this.status = ConnectionStatus.CONNECTING;
    this.emit('statusChange', this.status);

    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);
    } catch (error) {
      this.handleConnectionError(error);
    }
  }

  /**
   * 斷開連接
   */
  disconnect(): void {
    this.reconnectAttempts = 0;
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.status = ConnectionStatus.DISCONNECTED;
    this.emit('statusChange', this.status);
  }

  /**
   * 發送消息
   */
  send(message: any): void {
    if (this.status === ConnectionStatus.CONNECTED && this.ws) {
      try {
        const messageStr = JSON.stringify(message);
        this.ws.send(messageStr);
      } catch (error) {
        console.error('Failed to send message:', error);
        this.messageQueue.push(message);
      }
    } else {
      // 如果未連接，將消息加入隊列
      this.messageQueue.push(message);
      console.log('Message queued, WebSocket not connected');
    }
  }

  /**
   * 獲取連接狀態
   */
  getStatus(): ConnectionStatus {
    return this.status;
  }

  /**
   * 處理連接打開
   */
  private handleOpen(): void {
    console.log('WebSocket connected');
    this.status = ConnectionStatus.CONNECTED;
    this.reconnectAttempts = 0;
    this.emit('statusChange', this.status);
    this.emit('connected');

    // 發送隊列中的消息
    this.processMessageQueue();
    
    // 開始心跳
    this.startHeartbeat();
  }

  /**
   * 處理接收消息
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data);
      
      // 處理不同類型的消息
      this.processMessage(data);
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }

  /**
   * 處理連接關閉
   */
  private handleClose(event: CloseEvent): void {
    console.log('WebSocket disconnected:', event.code, event.reason);
    this.status = ConnectionStatus.DISCONNECTED;
    this.emit('statusChange', this.status);
    this.emit('disconnected', event);

    // 停止心跳
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    // 嘗試重連
    this.attemptReconnect();
  }

  /**
   * 處理連接錯誤
   */
  private handleError(event: Event): void {
    console.error('WebSocket error:', event);
    this.status = ConnectionStatus.ERROR;
    this.emit('statusChange', this.status);
    this.emit('error', event);
  }

  /**
   * 處理連接錯誤
   */
  private handleConnectionError(error: any): void {
    console.error('WebSocket connection error:', error);
    this.status = ConnectionStatus.ERROR;
    this.emit('statusChange', this.status);
    this.emit('error', error);
    this.attemptReconnect();
  }

  /**
   * 嘗試重連
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnection attempts reached');
      this.emit('maxReconnectAttemptsReached');
      return;
    }

    this.reconnectAttempts++;
    console.log(`Attempting reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);

    this.reconnectTimeout = setTimeout(() => {
      this.connect();
    }, this.reconnectInterval);
  }

  /**
   * 處理消息
   */
  private processMessage(data: WebSocketMessage): void {
    switch (data.type) {
      case 'proxy_status_update':
        this.emit('proxyStatusUpdate', data.payload);
        break;
      case 'system_status_update':
        this.emit('systemStatusUpdate', data.payload);
        break;
      case 'task_update':
        this.emit('taskUpdate', data.payload);
        break;
      case 'error_notification':
        this.emit('errorNotification', data.payload);
        break;
      case 'pong':
        // 心跳響應
        break;
      default:
        this.emit('message', data);
    }
  }

  /**
   * 處理消息隊列
   */
  private processMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
  }

  /**
   * 開始心跳
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.status === ConnectionStatus.CONNECTED && this.ws) {
        this.send({ type: 'ping', timestamp: Date.now() });
      }
    }, 30000); // 30 秒心跳
  }
}

/**
 * 創建 WebSocket 服務實例
 */
export const createWebSocketService = (url: string): WebSocketService => {
  return new WebSocketService(url);
};

/**
 * 默認 WebSocket 服務實例
 */
export const wsService = createWebSocketService('ws://localhost:3000/ws');

export default WebSocketService;