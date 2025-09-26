"""
HTML 解析器模組

負責解析從網站爬取的 HTML 內容，提取結構化的職位資訊。
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from bs4 import BeautifulSoup, Tag
from src.models import JobPost, Company, Location, SalaryRange, JobRequirement, JobType, ExperienceLevel


class JobParser:
    """
    職位資訊解析器
    
    負責從 HTML 頁面中提取結構化的職位資訊。
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化解析器
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def parse_job_listing(self, html_content: str) -> List[JobPost]:
        """
        解析職位列表頁面
        
        Args:
            html_content: HTML 內容
            
        Returns:
            List[JobPost]: 解析出的職位列表
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        jobs = []
        
        # 尋找職位卡片
        job_cards = self._find_job_cards(soup)
        self.logger.info(f"找到 {len(job_cards)} 個職位卡片")
        
        for card in job_cards:
            try:
                job = self._parse_job_card(card)
                if job:
                    jobs.append(job)
            except Exception as e:
                self.logger.warning(f"解析職位卡片失敗: {e}")
                continue
        
        return jobs
    
    def _find_job_cards(self, soup: BeautifulSoup) -> List[Tag]:
        """
        尋找頁面中的職位卡片
        
        Args:
            soup: BeautifulSoup 物件
            
        Returns:
            List[Tag]: 職位卡片元素列表
        """
        job_cards = []
        
        # 方法 1: 使用 data-automation 屬性
        cards = soup.find_all('article', {'data-automation': 'jobListing'})
        job_cards.extend(cards)
        
        # 方法 2: 使用特定的 class
        cards = soup.find_all('div', class_=lambda x: x and 'job' in x.lower() and 'listing' in x.lower())
        job_cards.extend(cards)
        
        # 方法 3: 使用特定的結構
        cards = soup.find_all('div', {'data-testid': lambda x: x and 'job' in x})
        job_cards.extend(cards)
        
        # 去重
        unique_cards = []
        seen_ids = set()
        
        for card in job_cards:
            card_id = str(card.get('id', '')) or str(hash(str(card)))
            if card_id not in seen_ids:
                unique_cards.append(card)
                seen_ids.add(card_id)
        
        return unique_cards
    
    def _parse_job_card(self, card: Tag) -> Optional[JobPost]:
        """
        解析單個職位卡片
        
        Args:
            card: 職位卡片 HTML 元素
            
        Returns:
            Optional[JobPost]: 解析出的職位資訊，失敗返回 None
        """
        try:
            # 提取基本資訊
            title = self._extract_job_title(card)
            if not title:
                self.logger.warning("無法提取職位標題")
                return None
            
            company = self._extract_company(card)
            location = self._extract_location(card)
            salary = self._extract_salary(card)
            job_type = self._extract_job_type(card)
            
            # 提取描述和其他資訊
            description = self._extract_description(card)
            requirements = self._extract_requirements(card)
            posted_date = self._extract_posted_date(card)
            source_url = self._extract_job_url(card)
            
            # 創建職位物件
            job = JobPost(
                title=title,
                company=company,
                location=location,
                job_type=job_type,
                description=description,
                requirements=requirements,
                salary=salary,
                posted_date=posted_date,
                source_url=source_url,
                source_id=self._generate_source_id(source_url)
            )
            
            self.logger.info(f"成功解析職位: {job.job_summary}")
            return job
            
        except Exception as e:
            self.logger.error(f"解析職位卡片時發生錯誤: {e}")
            return None
    
    def _extract_job_title(self, card: Tag) -> Optional[str]:
        """提取職位標題"""
        # 方法 1: data-automation
        title_elem = card.find(['h1', 'h2', 'h3', 'a'], {'data-automation': 'jobTitle'})
        if title_elem:
            return title_elem.get_text(strip=True)
        
        # 方法 2: 尋找包含 'job' 的連結
        title_links = card.find_all('a', href=lambda x: x and '/job/' in x)
        for link in title_links:
            text = link.get_text(strip=True)
            if text and len(text) > 5:  # 過濾掉太短的文本
                return text
        
        # 方法 3: 尋找標題元素
        for tag in ['h1', 'h2', 'h3', 'h4']:
            title_elem = card.find(tag)
            if title_elem:
                text = title_elem.get_text(strip=True)
                if text and len(text) > 5:
                    return text
        
        return None
    
    def _extract_company(self, card: Tag) -> Company:
        """提取公司資訊"""
        company_name = "Unknown Company"
        
        # 方法 1: data-automation
        company_elem = card.find(['span', 'div', 'a'], {'data-automation': 'jobCompany'})
        if company_elem:
            company_name = company_elem.get_text(strip=True)
        
        # 方法 2: 尋找公司相關的 class
        if company_name == "Unknown Company":
            company_elem = card.find(class_=lambda x: x and 'company' in x.lower())
            if company_elem:
                company_name = company_elem.get_text(strip=True)
        
        return Company(name=company_name)
    
    def _extract_location(self, card: Tag) -> Location:
        """提取地點資訊"""
        location_text = "Unknown Location"
        
        # 方法 1: data-automation
        location_elem = card.find(['span', 'div'], {'data-automation': 'jobLocation'})
        if location_elem:
            location_text = location_elem.get_text(strip=True)
        
        # 方法 2: 尋找地點相關的 class
        if location_text == "Unknown Location":
            location_elem = card.find(class_=lambda x: x and 'location' in x.lower())
            if location_elem:
                location_text = location_elem.get_text(strip=True)
        
        # 解析地點文本
        city, state = self._parse_location_text(location_text)
        
        return Location(city=city, state=state, country="Australia")
    
    def _parse_location_text(self, location_text: str) -> tuple[str, Optional[str]]:
        """解析地點文本"""
        # 簡單的解析邏輯，可以根據需要改進
        parts = [part.strip() for part in location_text.split(',')]
        
        if len(parts) >= 2:
            city = parts[0]
            state = parts[1]
        else:
            city = location_text
            state = None
        
        return city, state
    
    def _extract_salary(self, card: Tag) -> Optional[SalaryRange]:
        """提取薪資資訊"""
        # 方法 1: data-automation
        salary_elem = card.find(['span', 'div'], {'data-automation': 'jobSalary'})
        if not salary_elem:
            # 方法 2: 尋找薪資相關的 class
            salary_elem = card.find(class_=lambda x: x and 'salary' in x.lower())
        
        if not salary_elem:
            return None
        
        salary_text = salary_elem.get_text(strip=True)
        return self._parse_salary_text(salary_text)
    
    def _parse_salary_text(self, salary_text: str) -> Optional[SalaryRange]:
        """解析薪資文本"""
        if not salary_text or 'not' in salary_text.lower():
            return None
        
        # 正則表達式匹配薪資範圍
        patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $X - $Y
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\+',  # $X+
            r'up\s+to\s+\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # up to $X
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $X
        ]
        
        for pattern in patterns:
            match = re.search(pattern, salary_text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 2:  # 範圍
                    min_salary = float(groups[0].replace(',', ''))
                    max_salary = float(groups[1].replace(',', ''))
                    return SalaryRange(min_salary=min_salary, max_salary=max_salary)
                elif len(groups) == 1:  # 單一值
                    salary = float(groups[0].replace(',', ''))
                    return SalaryRange(min_salary=salary, max_salary=salary)
        
        return None
    
    def _extract_job_type(self, card: Tag) -> Optional[JobType]:
        """提取工作類型"""
        # 方法 1: data-automation
        type_elem = card.find(['span', 'div'], {'data-automation': 'jobType'})
        if not type_elem:
            # 方法 2: 尋找工作類型相關的 class
            type_elem = card.find(class_=lambda x: x and 'worktype' in x.lower())
        
        if not type_elem:
            return None
        
        type_text = type_elem.get_text(strip=True).lower()
        
        # 映射到枚舉
        if 'full' in type_text:
            return JobType.FULL_TIME
        elif 'part' in type_text:
            return JobType.PART_TIME
        elif 'contract' in type_text:
            return JobType.CONTRACT
        elif 'casual' in type_text:
            return JobType.CASUAL
        elif 'temporary' in type_text:
            return JobType.TEMPORARY
        elif 'intern' in type_text or 'graduate' in type_text:
            return JobType.INTERNSHIP
        
        return None
    
    def _extract_description(self, card: Tag) -> str:
        """提取職位描述"""
        # 方法 1: 尋找包含描述的 div
        desc_elem = card.find('div', {'data-automation': 'jobDescription'})
        if desc_elem:
            return desc_elem.get_text(strip=True)
        
        # 方法 2: 尋找長文本的 div
        divs = card.find_all('div')
        for div in divs:
            text = div.get_text(strip=True)
            if len(text) > 100:  # 假設描述應該比較長
                return text
        
        return ""
    
    def _extract_requirements(self, card: Tag) -> JobRequirement:
        """提取職位要求"""
        # 這是一個簡化的實現，實際上需要更複雜的解析
        requirements = JobRequirement()
        
        # 尋找技能相關的文本
        text = card.get_text(strip=True).lower()
        
        # 簡單的關鍵詞匹配
        common_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue',
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes',
            'machine learning', 'deep learning', 'ai', 'data science',
            'agile', 'scrum', 'git', 'ci/cd'
        ]
        
        for skill in common_skills:
            if skill in text:
                requirements.required_skills.append(skill)
        
        return requirements
    
    def _extract_posted_date(self, card: Tag) -> Optional[datetime]:
        """提取發布日期"""
        # 方法 1: data-automation
        date_elem = card.find(['span', 'div'], {'data-automation': 'jobListingDate'})
        if not date_elem:
            # 方法 2: 尋找日期相關的 class
            date_elem = card.find(class_=lambda x: x and 'date' in x.lower())
        
        if not date_elem:
            return None
        
        date_text = date_elem.get_text(strip=True)
        return self._parse_date_text(date_text)
    
    def _parse_date_text(self, date_text: str) -> Optional[datetime]:
        """解析日期文本"""
        if not date_text:
            return None
        
        date_text = date_text.lower()
        now = datetime.now()
        
        # 相對日期
        if 'just' in date_text or 'now' in date_text:
            return now
        elif 'hour' in date_text or 'hr' in date_text:
            hours = self._extract_number(date_text) or 1
            return now - timedelta(hours=hours)
        elif 'day' in date_text:
            days = self._extract_number(date_text) or 1
            return now - timedelta(days=days)
        elif 'week' in date_text:
            weeks = self._extract_number(date_text) or 1
            return now - timedelta(weeks=weeks)
        elif 'month' in date_text:
            months = self._extract_number(date_text) or 1
            return now - timedelta(days=months * 30)  # 近似
        
        return now  # 預設值
    
    def _extract_number(self, text: str) -> Optional[int]:
        """從文本中提取數字"""
        match = re.search(r'\d+', text)
        return int(match.group()) if match else None
    
    def _extract_job_url(self, card: Tag) -> str:
        """提取職位 URL"""
        # 方法 1: 尋找包含 '/job/' 的連結
        job_links = card.find_all('a', href=lambda x: x and '/job/' in x)
        for link in job_links:
            href = link.get('href', '')
            if href.startswith('/'):
                return f"https://www.seek.com.au{href}"
            elif href.startswith('http'):
                return href
        
        return ""
    
    def _generate_source_id(self, url: str) -> str:
        """生成來源 ID"""
        if not url:
            return ""
        
        # 從 URL 中提取 ID
        match = re.search(r'/job/(\d+)', url)
        return match.group(1) if match else url