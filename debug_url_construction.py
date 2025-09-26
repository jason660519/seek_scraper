#!/usr/bin/env python3
"""
調試 URL 構建過程
"""

import sys
from pathlib import Path

# 添加 src 到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.models import SearchCriteria

def debug_url_construction():
    """調試 URL 構建過程"""
    
    # 模擬 test_diverse_with_runner.py 中的邏輯
    test_searches = [
        {
            "keywords": ["ai", "machine learning", "data scientist"],
            "location": "Sydney NSW 2000"
        },
        {
            "keywords": ["data scientist", "machine learning"],
            "location": "Melbourne VIC 3000"
        }
    ]
    
    print("調試 URL 構建過程:")
    print("=" * 60)
    
    for i, search in enumerate(test_searches):
        print(f"\n測試案例 {i+1}:")
        print(f"關鍵詞: {search['keywords']}")
        print(f"位置: {search['location']}")
        
        # 模擬 run_integrated_seek_etl.py 的邏輯
        keywords = search['keywords']
        location = search['location']
        
        # 處理關鍵詞格式
        if isinstance(keywords, list):
            keyword_str = '-'.join(keywords).lower()
        else:
            keyword_str = str(keywords).lower().replace(' ', '-')
        
        print(f"處理後的關鍵詞: '{keyword_str}'")
        
        # 處理位置格式
        if location:
            location = str(location).replace(' ', '-')
            if not location.startswith('in-'):
                location = f'in-{location}'
        
        print(f"處理後的位置: '{location}'")
        
        # 構建 URL
        base_url = "https://www.seek.com.au"
        search_url = f"{base_url}/{keyword_str}-jobs"
        if location:
            search_url += f"/{location}"
        
        print(f"最終 URL: {search_url}")
        
        # 與已知的工作 URL 比較
        working_urls = [
            "https://www.seek.com.au/machine-learning-jobs/in-Sydney-NSW-2000",
            "https://www.seek.com.au/data-scientist-jobs/in-Melbourne-VIC-3000"
        ]
        
        print(f"工作 URL 示例: {working_urls[i] if i < len(working_urls) else 'N/A'}")
        print(f"匹配工作格式: {search_url == working_urls[i] if i < len(working_urls) else 'N/A'}")

if __name__ == "__main__":
    debug_url_construction()