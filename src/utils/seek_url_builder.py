"""
Seek URL構建器
根據Seek網站的URL規律構建搜索URL
"""

from typing import Optional
from urllib.parse import urlencode


class SeekURLBuilder:
    """Seek網站URL構建器"""
    
    BASE_URL = "https://www.seek.com.au"
    
    @staticmethod
    def build_search_url(
        keyword: str, 
        location: Optional[str] = None, 
        page: int = 1
    ) -> str:
        """
        構建Seek搜索URL
        
        Args:
            keyword: 搜索關鍵詞（如：software-engineer）
            location: 地點（如：melbourne-vic，可選）
            page: 頁碼（默認1）
            
        Returns:
            完整的Seek搜索URL
        """
        # 處理關鍵詞：小寫，空格替換為連字符
        keyword_processed = keyword.lower().replace(' ', '-')
        
        # 構建基礎URL
        if location:
            # 處理地點：小寫，空格替換為連字符
            location_processed = location.lower().replace(' ', '-')
            url = f"{SeekURLBuilder.BASE_URL}/{keyword_processed}-jobs/in-{location_processed}"
        else:
            url = f"{SeekURLBuilder.BASE_URL}/{keyword_processed}-jobs"
        
        # 添加分頁參數
        if page > 1:
            url += f"?page={page}"
            
        return url
    
    @staticmethod
    def build_job_detail_url(job_id: str) -> str:
        """
        構建Seek職位詳情頁URL
        
        Args:
            job_id: 職位ID
            
        Returns:
            完整的Seek職位詳情URL
        """
        return f"{SeekURLBuilder.BASE_URL}/job/{job_id}"
    
    @staticmethod
    def process_text_for_url(text: str) -> str:
        """
        將文本處理為URL友好的格式
        
        Args:
            text: 原始文本
            
        Returns:
            處理後的文本（小寫，空格替換為連字符）
        """
        return text.lower().strip().replace(' ', '-')