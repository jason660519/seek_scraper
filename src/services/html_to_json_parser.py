"""
ETL HTML 解析服務

實現 SEEK 爬蟲的 Step 2：HTML 解析轉 JSON/CSV 功能。
將 raw 資料夾中的 HTML 文件解析為結構化的 JSON/CSV 文件。
"""

import csv
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from ..models import JobPost, Company, Location, SalaryRange, JobRequirement


class HtmlToJsonParser:
    """
    HTML 轉 JSON 解析器
    
    負責將 SEEK 工作頁面的 HTML 解析為結構化的 JSON/CSV 數據，包括：
    - 工作標題
    - 公司名稱
    - 工作地點
    - 工作分類
    - 工作類型
    - 薪資範圍
    - 工作詳情
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化 HTML 解析器
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # SEEK 特定的選擇器映射
        self.selectors = {
            "title": [
                '[data-automation="job-detail-title"]',
                'h1[data-automation="job-detail-title"]',
                'h1[class*="title"]',
                'h1'
            ],
            "company": [
                '[data-automation="job-detail-company"]',
                '[data-automation="advertiser-name"]',
                '[class*="company"]',
                'a[href*="/company/"]'
            ],
            "location": [
                '[data-automation="job-detail-location"]',
                '[class*="location"]',
                'span:contains("Location:")',
                'div:contains("Location:")'
            ],
            "classifications": [
                '[data-automation="job-detail-classifications"]',
                '[class*="classification"]',
                'div:contains("Classification:")'
            ],
            "work_type": [
                '[data-automation="job-detail-work-type"]',
                '[class*="work-type"]',
                'span:contains("Work Type:")',
                'div:contains("Work Type:")'
            ],
            "salary": [
                '[data-automation="job-detail-salary"]',
                '[class*="salary"]',
                'span:contains("Salary:")',
                'div:contains("Salary:")'
            ],
            "job_details": [
                '[data-automation="jobAdDetails"]',
                '[class*="job-details"]',
                '[class*="job-description"]',
                'div:contains("Job Description")'
            ]
        }
        
        # 薪資解析正則表達式
        self.salary_patterns = [
            r'\$(\d+(?:,\d+)*)\s*-\s*\$(\d+(?:,\d+)*)',  # $50,000 - $70,000
            r'\$(\d+(?:,\d+)*)\+?',  # $50,000+ 或 $50,000
            r'(\d+(?:,\d)*)\s*k\s*-\s*(\d+(?:,\d)*)\s*k',  # 50k - 70k
            r'(\d+(?:,\d)*)\s*k\+?',  # 50k+
            r'\$(\d+(?:,\d)*)\s*PA',  # $50,000 PA
            r'\$(\d+(?:,\d)*)\s*per\s*annum',  # $50,000 per annum
            r'\$(\d+(?:,\d)*)\s*to\s*\$(\d+(?:,\d)*)'  # $50,000 to $70,000
        ]
        
        # 工作類型映射
        self.work_type_mapping = {
            "full time": "Full Time",
            "fulltime": "Full Time", 
            "full-time": "Full Time",
            "part time": "Part Time",
            "parttime": "Part Time",
            "part-time": "Part Time",
            "contract": "Contract",
            "temporary": "Temporary",
            "temp": "Temporary",
            "casual": "Casual",
            "permanent": "Permanent",
            "permanent full time": "Full Time",
            "permanent part time": "Part Time"
        }
    
    def parse_html_file(self, html_file_path: Path) -> Optional[Dict[str, Any]]:
        """
        解析單個 HTML 文件
        
        Args:
            html_file_path: HTML 文件路徑
            
        Returns:
            Optional[Dict[str, Any]]: 解析後的數據，失敗返回 None
        """
        try:
            self.logger.info(f"解析 HTML 文件: {html_file_path}")
            
            # 讀取 HTML 內容
            html_content = html_file_path.read_text(encoding='utf-8')
            
            # 解析 HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 提取數據
            job_data = self._extract_job_data(soup, html_file_path)
            
            if job_data:
                self.logger.info(f"成功解析 HTML 文件: {html_file_path}")
                return job_data
            else:
                self.logger.warning(f"無法從 HTML 文件提取有效數據: {html_file_path}")
                return None
                
        except Exception as e:
            self.logger.error(f"解析 HTML 文件失敗: {html_file_path} - {e}")
            return None
    
    def parse_job_folder(self, job_folder_path: Path) -> Optional[Dict[str, Any]]:
        """
        解析工作資料夾
        
        Args:
            job_folder_path: 工作資料夾路徑
            
        Returns:
            Optional[Dict[str, Any]]: 解析後的數據，失敗返回 None
        """
        try:
            self.logger.info(f"解析工作資料夾: {job_folder_path}")
            
            # 查找 HTML 文件
            html_files = list(job_folder_path.glob("*.html"))
            if not html_files:
                self.logger.warning(f"在工作資料夾中未找到 HTML 文件: {job_folder_path}")
                return None
            
            # 優先使用 index.html
            html_file = job_folder_path / "index.html"
            if not html_file.exists():
                html_file = html_files[0]
            
            # 解析 HTML
            job_data = self.parse_html_file(html_file)
            
            if job_data:
                # 添加資料夾資訊
                job_data["folder_info"] = {
                    "folder_name": job_folder_path.name,
                    "folder_path": str(job_folder_path),
                    "html_file": str(html_file),
                    "parsed_timestamp": datetime.now().isoformat()
                }
                
                # 從 metadata.json 加載額外資訊
                metadata_file = job_folder_path / "metadata.json"
                if metadata_file.exists():
                    try:
                        metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
                        job_data["metadata"] = metadata
                    except Exception as e:
                        self.logger.warning(f"讀取 metadata.json 失敗: {metadata_file} - {e}")
            
            return job_data
            
        except Exception as e:
            self.logger.error(f"解析工作資料夾失敗: {job_folder_path} - {e}")
            return None
    
    def parse_multiple_folders(self, folders_path: Path) -> List[Dict[str, Any]]:
        """
        解析多個工作資料夾
        
        Args:
            folders_path: 包含工作資料夾的目錄路徑
            
        Returns:
            List[Dict[str, Any]]: 解析後的工作數據列表
        """
        try:
            self.logger.info(f"解析多個工作資料夾: {folders_path}")
            
            # 獲取所有工作資料夾
            job_folders = [f for f in folders_path.iterdir() if f.is_dir()]
            self.logger.info(f"找到 {len(job_folders)} 個工作資料夾")
            
            parsed_jobs = []
            failed_folders = []
            
            for folder in job_folders:
                try:
                    job_data = self.parse_job_folder(folder)
                    if job_data:
                        parsed_jobs.append(job_data)
                        self.logger.info(f"成功解析資料夾: {folder.name}")
                    else:
                        failed_folders.append(folder.name)
                        self.logger.warning(f"解析失敗的資料夾: {folder.name}")
                        
                except Exception as e:
                    self.logger.error(f"解析資料夾失敗: {folder.name} - {e}")
                    failed_folders.append(folder.name)
                    continue
            
            self.logger.info(f"解析完成: 成功 {len(parsed_jobs)} 個，失敗 {len(failed_folders)} 個")
            
            if failed_folders:
                self.logger.warning(f"解析失敗的資料夾: {failed_folders}")
            
            return parsed_jobs
            
        except Exception as e:
            self.logger.error(f"解析多個資料夾失敗: {folders_path} - {e}")
            return []
    
    def _extract_job_data(self, soup: BeautifulSoup, html_file_path: Path) -> Dict[str, Any]:
        """
        從 BeautifulSoup 對象提取工作數據
        
        Args:
            soup: BeautifulSoup 對象
            html_file_path: HTML 文件路徑
            
        Returns:
            Dict[str, Any]: 提取的工作數據
        """
        try:
            job_data = {
                "seek_url": self._extract_url_from_html(soup, html_file_path),
                "job_detail_title": self._extract_title(soup),
                "job_detail_location": self._extract_location(soup),
                "job_detail_classifications": self._extract_classifications(soup),
                "job_detail_work_type": self._extract_work_type(soup),
                "job_detail_salary": self._extract_salary(soup),
                "jobAdDetails": self._extract_job_details(soup),
                "extraction_timestamp": datetime.now().isoformat(),
                "html_file": str(html_file_path)
            }
            
            # 清理數據
            job_data = self._clean_job_data(job_data)
            
            return job_data
            
        except Exception as e:
            self.logger.error(f"提取工作數據失敗: {e}")
            return {}
    
    def _extract_url_from_html(self, soup: BeautifulSoup, html_file_path: Path) -> str:
        """
        從 HTML 提取 URL
        
        Args:
            soup: BeautifulSoup 對象
            html_file_path: HTML 文件路徑
            
        Returns:
            str: 提取的 URL
        """
        try:
            # 從 metadata.json 提取 URL
            metadata_file = html_file_path.parent / "metadata.json"
            if metadata_file.exists():
                try:
                    metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
                    if "url" in metadata:
                        return metadata["url"]
                except Exception:
                    pass
            
            # 從 HTML 中的連結提取
            job_links = soup.find_all('a', href=True)
            for link in job_links:
                href = link['href']
                if 'seek.com.au' in href and '/job/' in href:
                    return href
            
            # 從文件夾名稱推斷
            folder_name = html_file_path.parent.name
            parts = folder_name.split('_')
            if len(parts) >= 2:
                company = parts[0]
                job_title = parts[1]
                # 構建可能的 URL
                return f"https://www.seek.com.au/job/{company}-{job_title}"
            
            return "Unknown"
            
        except Exception as e:
            self.logger.warning(f"提取 URL 失敗: {e}")
            return "Unknown"
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        提取工作標題
        
        Args:
            soup: BeautifulSoup 對象
            
        Returns:
            str: 工作標題
        """
        try:
            # 嘗試多個選擇器
            for selector in self.selectors["title"]:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text(strip=True)
                    if title:
                        return title
            
            # 後備方案：查找包含 "job" 的 h1 標籤
            h1_tags = soup.find_all('h1')
            for h1 in h1_tags:
                text = h1.get_text(strip=True)
                if text and len(text) > 5:  # 確保有內容
                    return text
            
            return "Unknown"
            
        except Exception as e:
            self.logger.warning(f"提取工作標題失敗: {e}")
            return "Unknown"
    
    def _extract_location(self, soup: BeautifulSoup) -> str:
        """
        提取工作地點
        
        Args:
            soup: BeautifulSoup 對象
            
        Returns:
            str: 工作地點
        """
        try:
            # 嘗試多個選擇器
            for selector in self.selectors["location"]:
                element = soup.select_one(selector)
                if element:
                    location = element.get_text(strip=True)
                    if location and len(location) > 2:
                        return location
            
            # 後備方案：查找包含地點信息的文本
            location_keywords = ["sydney", "melbourne", "brisbane", "perth", "adelaide", "canberra", "darwin", "hobart"]
            text_content = soup.get_text().lower()
            
            for keyword in location_keywords:
                if keyword in text_content:
                    return keyword.title()
            
            return "Unknown"
            
        except Exception as e:
            self.logger.warning(f"提取工作地點失敗: {e}")
            return "Unknown"
    
    def _extract_classifications(self, soup: BeautifulSoup) -> str:
        """
        提取工作分類
        
        Args:
            soup: BeautifulSoup 對象
            
        Returns:
            str: 工作分類
        """
        try:
            # 嘗試多個選擇器
            for selector in self.selectors["classifications"]:
                element = soup.select_one(selector)
                if element:
                    classifications = element.get_text(strip=True)
                    if classifications and len(classifications) > 2:
                        return classifications
            
            # 後備方案：查找包含分類信息的文本
            classification_keywords = ["classification", "category", "industry"]
            text_content = soup.get_text().lower()
            
            for keyword in classification_keywords:
                if keyword in text_content:
                    # 查找關鍵詞後的文本
                    lines = text_content.split('\n')
                    for line in lines:
                        if keyword in line and len(line.strip()) > 10:
                            return line.strip()
            
            return "Unknown"
            
        except Exception as e:
            self.logger.warning(f"提取工作分類失敗: {e}")
            return "Unknown"
    
    def _extract_work_type(self, soup: BeautifulSoup) -> str:
        """
        提取工作類型
        
        Args:
            soup: BeautifulSoup 對象
            
        Returns:
            str: 工作類型
        """
        try:
            # 嘗試多個選擇器
            for selector in self.selectors["work_type"]:
                element = soup.select_one(selector)
                if element:
                    work_type = element.get_text(strip=True)
                    if work_type and len(work_type) > 2:
                        return self._normalize_work_type(work_type)
            
            # 後備方案：從文本中提取工作類型
            text_content = soup.get_text().lower()
            
            for key, value in self.work_type_mapping.items():
                if key in text_content:
                    return value
            
            return "Unknown"
            
        except Exception as e:
            self.logger.warning(f"提取工作類型失敗: {e}")
            return "Unknown"
    
    def _extract_salary(self, soup: BeautifulSoup) -> str:
        """
        提取薪資信息
        
        Args:
            soup: BeautifulSoup 對象
            
        Returns:
            str: 薪資信息
        """
        try:
            # 嘗試多個選擇器
            for selector in self.selectors["salary"]:
                element = soup.select_one(selector)
                if element:
                    salary = element.get_text(strip=True)
                    if salary and len(salary) > 2:
                        return salary
            
            # 後備方案：使用正則表達式提取薪資
            text_content = soup.get_text()
            
            for pattern in self.salary_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    return matches[0] if isinstance(matches[0], str) else " - ".join(matches[0])
            
            return "Not specified"
            
        except Exception as e:
            self.logger.warning(f"提取薪資信息失敗: {e}")
            return "Not specified"
    
    def _extract_job_details(self, soup: BeautifulSoup) -> str:
        """
        提取工作詳情
        
        Args:
            soup: BeautifulSoup 對象
            
        Returns:
            str: 工作詳情
        """
        try:
            # 嘗試多個選擇器
            for selector in self.selectors["job_details"]:
                element = soup.select_one(selector)
                if element:
                    details = element.get_text(strip=True)
                    if details and len(details) > 10:
                        return details
            
            # 後備方案：查找主要的內容區域
            content_selectors = [
                'main',
                'article',
                '.content',
                '#content',
                '[role="main"]'
            ]
            
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    # 移除腳本和樣式
                    for script in element(["script", "style"]):
                        script.decompose()
                    
                    text = element.get_text(separator=' ', strip=True)
                    if text and len(text) > 50:  # 確保有足夠內容
                        return text
            
            # 最後手段：提取所有文本
            text_content = soup.get_text(separator=' ', strip=True)
            return text_content if len(text_content) > 50 else "No detailed description found"
            
        except Exception as e:
            self.logger.warning(f"提取工作詳情失敗: {e}")
            return "No detailed description found"
    
    def _normalize_work_type(self, work_type: str) -> str:
        """
        標準化工作類型
        
        Args:
            work_type: 原始工作類型
            
        Returns:
            str: 標準化後的工作類型
        """
        try:
            work_type_lower = work_type.lower().strip()
            
            for key, value in self.work_type_mapping.items():
                if key in work_type_lower:
                    return value
            
            # 如果沒有匹配，返回原始值（首字母大寫）
            return work_type.title()
            
        except Exception as e:
            self.logger.warning(f"標準化工作類型失敗: {e}")
            return work_type
    
    def _clean_job_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理工作數據
        
        Args:
            job_data: 原始工作數據
            
        Returns:
            Dict[str, Any]: 清理後的工作數據
        """
        try:
            # 清理每個字段
            for key, value in job_data.items():
                if isinstance(value, str):
                    # 移除多餘的空白字符
                    value = re.sub(r'\s+', ' ', value.strip())
                    
                    # 移除特殊字符（保留必要的標點符號）
                    value = re.sub(r'[^\w\s\-.,:;!?()"\'\/]', '', value)
                    
                    job_data[key] = value
            
            return job_data
            
        except Exception as e:
            self.logger.warning(f"清理工作數據失敗: {e}")
            return job_data
    
    def save_to_json(self, job_data: Dict[str, Any], output_path: Path) -> bool:
        """
        保存為 JSON 文件
        
        Args:
            job_data: 工作數據
            output_path: 輸出路徑
            
        Returns:
            bool: 是否成功保存
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"保存 JSON 文件成功: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存 JSON 文件失敗: {output_path} - {e}")
            return False
    
    def save_to_csv(self, job_data_list: List[Dict[str, Any]], output_path: Path) -> bool:
        """
        保存為 CSV 文件
        
        Args:
            job_data_list: 工作數據列表
            output_path: 輸出路徑
            
        Returns:
            bool: 是否成功保存
        """
        try:
            if not job_data_list:
                self.logger.warning("沒有數據可供保存")
                return False
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 定義 CSV 列順序
            fieldnames = [
                "seek_url",
                "job_detail_title", 
                "job_detail_location",
                "job_detail_classifications",
                "job_detail_work_type",
                "job_detail_salary",
                "jobAdDetails",
                "extraction_timestamp",
                "html_file"
            ]
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for job_data in job_data_list:
                    # 只寫入定義的字段
                    row_data = {field: job_data.get(field, '') for field in fieldnames}
                    writer.writerow(row_data)
            
            self.logger.info(f"保存 CSV 文件成功: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存 CSV 文件失敗: {output_path} - {e}")
            return False
    
    def convert_folder_to_json(self, input_folder: Path, output_folder: Path) -> bool:
        """
        將資料夾轉換為 JSON
        
        Args:
            input_folder: 輸入資料夾（包含 raw 數據）
            output_folder: 輸出資料夾
            
        Returns:
            bool: 是否成功轉換
        """
        try:
            self.logger.info(f"將資料夾轉換為 JSON: {input_folder} -> {output_folder}")
            
            # 解析所有工作資料夾
            job_data_list = self.parse_multiple_folders(input_folder)
            
            if not job_data_list:
                self.logger.warning("沒有找到可解析的工作數據")
                return False
            
            # 創建輸出文件夾
            output_folder.mkdir(parents=True, exist_ok=True)
            
            # 保存合併的 JSON 文件
            merged_json_path = output_folder / "all_jobs.json"
            self.save_to_json(job_data_list, merged_json_path)
            
            # 保存單獨的 JSON 文件
            for i, job_data in enumerate(job_data_list):
                # 生成文件名
                title = job_data.get("job_detail_title", "unknown").replace(" ", "_")
                company = job_data.get("job_detail_company", "unknown").replace(" ", "_")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                filename = f"{company}_{title}_{timestamp}.json"
                individual_path = output_folder / filename
                
                self.save_to_json(job_data, individual_path)
            
            self.logger.info(f"資料夾轉換完成: 成功轉換 {len(job_data_list)} 個工作")
            return True
            
        except Exception as e:
            self.logger.error(f"資料夾轉換失敗: {e}")
            return False
    
    def convert_folder_to_csv(self, input_folder: Path, output_folder: Path) -> bool:
        """
        將資料夾轉換為 CSV
        
        Args:
            input_folder: 輸入資料夾（包含 raw 數據）
            output_folder: 輸出資料夾
            
        Returns:
            bool: 是否成功轉換
        """
        try:
            self.logger.info(f"將資料夾轉換為 CSV: {input_folder} -> {output_folder}")
            
            # 解析所有工作資料夾
            job_data_list = self.parse_multiple_folders(input_folder)
            
            if not job_data_list:
                self.logger.warning("沒有找到可解析的工作數據")
                return False
            
            # 創建輸出文件夾
            output_folder.mkdir(parents=True, exist_ok=True)
            
            # 保存 CSV 文件
            csv_path = output_folder / "all_jobs.csv"
            self.save_to_csv(job_data_list, csv_path)
            
            self.logger.info(f"資料夾轉換完成: 成功轉換 {len(job_data_list)} 個工作")
            return True
            
        except Exception as e:
            self.logger.error(f"資料夾轉換失敗: {e}")
            return False