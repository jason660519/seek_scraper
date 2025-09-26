/**
 * 用戶相關類型定義
 */

// 用戶接口
export interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  lastLogin?: Date;
  createdAt?: Date;
}