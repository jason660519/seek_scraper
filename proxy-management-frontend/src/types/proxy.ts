/**
 * 代理相關類型定義
 */

// 代理狀態枚舉
export enum ProxyStatus {
  VALID = 'valid',
  INVALID = 'invalid',
  TEMPORARILY_INVALID = 'temporarily_invalid',
  UNTESTED = 'untested'
}

// 代理協議枚舉
export enum ProxyProtocol {
  HTTP = 'http',
  HTTPS = 'https',
  SOCKS4 = 'socks4',
  SOCKS5 = 'socks5'
}

// 代理接口
export interface Proxy {
  id: string;
  host: string;
  port: number;
  protocol: ProxyProtocol;
  status: ProxyStatus;
  country?: string;
  city?: string;
  responseTime?: number;
  anonymity?: string;
  lastChecked?: Date;
  createdAt?: Date;
  updatedAt?: Date;
}

// 代理統計接口
export interface ProxyStatistics {
  total: number;
  valid: number;
  invalid: number;
  temporarilyInvalid: number;
  untested: number;
  byProtocol: Record<ProxyProtocol, number>;
  byCountry: Record<string, number>;
}