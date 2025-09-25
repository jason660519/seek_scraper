#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單連接測試
"""

import socket
import urllib.request
import urllib.error

def test_connection():
    """測試服務器連接"""
    try:
        # 測試端口是否開放
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        
        if result == 0:
            print("✅ 端口 5000 已開放")
            
            # 測試HTTP請求
            try:
                response = urllib.request.urlopen('http://localhost:5000/')
                print(f"✅ 主頁面訪問成功，狀態碼: {response.getcode()}")
                
                # 測試API端點
                try:
                    api_response = urllib.request.urlopen('http://localhost:5000/api/status')
                    print(f"✅ API端點訪問成功，狀態碼: {api_response.getcode()}")
                except urllib.error.HTTPError as e:
                    print(f"❌ API端點錯誤: {e.code} - {e.reason}")
                except Exception as e:
                    print(f"❌ API端點錯誤: {str(e)}")
                    
            except Exception as e:
                print(f"❌ 主頁面訪問錯誤: {str(e)}")
                
        else:
            print("❌ 端口 5000 未開放或服務器未運行")
            
    except Exception as e:
        print(f"❌ 連接測試失敗: {str(e)}")

if __name__ == '__main__':
    print("🔍 測試服務器連接...")
    test_connection()