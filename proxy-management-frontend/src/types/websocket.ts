/**
 * WebSocket相關類型定義
 */

// WebSocket消息接口
export interface WebSocketMessage {
  type: string;
  payload: any;
  timestamp: number;
}