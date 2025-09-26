"""
資料模型模組

定義爬蟲系統中使用的所有資料結構和模型。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class JobType(Enum):
    """職位類型枚舉"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    CASUAL = "casual"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"


class ExperienceLevel(Enum):
    """經驗等級枚舉"""
    ENTRY_LEVEL = "entry_level"
    MID_LEVEL = "mid_level"
    SENIOR_LEVEL = "senior_level"
    EXECUTIVE = "executive"


@dataclass
class SalaryRange:
    """薪資範圍"""
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: str = "AUD"
    period: str = "annum"  # annum, hour, day, week, month
    
    @property
    def is_range(self) -> bool:
        """檢查是否為薪資範圍"""
        return self.min_salary is not None and self.max_salary is not None
    
    @property
    def display_text(self) -> str:
        """生成顯示文字"""
        if self.min_salary and self.max_salary:
            return f"${self.min_salary:,.0f} - ${self.max_salary:,.0f} {self.currency} per {self.period}"
        elif self.min_salary:
            return f"${self.min_salary:,.0f}+ {self.currency} per {self.period}"
        elif self.max_salary:
            return f"Up to ${self.max_salary:,.0f} {self.currency} per {self.period}"
        else:
            return "薪資未公開"


@dataclass
class Company:
    """公司資訊"""
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None


@dataclass
class Location:
    """地點資訊"""
    city: str
    state: Optional[str] = None
    country: str = "Australia"
    postal_code: Optional[str] = None
    suburb: Optional[str] = None
    
    @property
    def full_address(self) -> str:
        """完整地址"""
        parts = [self.suburb, self.city, self.state, self.country]
        return ", ".join(filter(None, parts))


@dataclass
class JobRequirement:
    """職位要求"""
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    education_level: Optional[str] = None
    experience_years: Optional[int] = None
    certifications: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)


@dataclass
class JobPost:
    """職位發布資訊"""
    # 基本資訊
    title: str
    company: Company
    location: Location
    job_type: JobType
    
    # 詳細資訊
    description: str
    requirements: JobRequirement
    responsibilities: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    
    # 薪資資訊
    salary: Optional[SalaryRange] = None
    
    # 分類資訊
    category: Optional[str] = None
    subcategory: Optional[str] = None
    industry: Optional[str] = None
    experience_level: Optional[ExperienceLevel] = None
    
    # 時間資訊
    posted_date: Optional[datetime] = None
    closing_date: Optional[datetime] = None
    
    # 來源資訊
    source_url: str = ""
    source_id: str = ""
    
    # 元數據
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 爬蟲相關
    crawled_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    def __post_init__(self):
        """後處理：確保必要欄位存在"""
        if not self.crawled_at:
            self.crawled_at = datetime.now()
    
    @property
    def job_summary(self) -> str:
        """職位摘要"""
        return f"{self.title} at {self.company.name} in {self.location.city}"
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典（用於 JSON 序列化）"""
        return {
            'title': self.title,
            'company': {
                'name': self.company.name,
                'website': self.company.website,
                'industry': self.company.industry,
                'company_size': self.company.company_size,
                'description': self.company.description,
                'logo_url': self.company.logo_url
            },
            'location': {
                'city': self.location.city,
                'state': self.location.state,
                'country': self.location.country,
                'postal_code': self.location.postal_code,
                'suburb': self.location.suburb
            },
            'job_type': self.job_type.value if self.job_type else None,
            'description': self.description,
            'requirements': {
                'required_skills': self.requirements.required_skills,
                'preferred_skills': self.requirements.preferred_skills,
                'education_level': self.requirements.education_level,
                'experience_years': self.requirements.experience_years,
                'certifications': self.requirements.certifications,
                'languages': self.requirements.languages
            },
            'responsibilities': self.responsibilities,
            'benefits': self.benefits,
            'salary': {
                'min_salary': self.salary.min_salary if self.salary else None,
                'max_salary': self.salary.max_salary if self.salary else None,
                'currency': self.salary.currency if self.salary else None,
                'period': self.salary.period if self.salary else None
            } if self.salary else None,
            'category': self.category,
            'subcategory': self.subcategory,
            'industry': self.industry,
            'experience_level': self.experience_level.value if self.experience_level else None,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'closing_date': self.closing_date.isoformat() if self.closing_date else None,
            'source_url': self.source_url,
            'source_id': self.source_id,
            'metadata': self.metadata,
            'crawled_at': self.crawled_at.isoformat(),
            'is_active': self.is_active
        }


@dataclass
class SearchCriteria:
    """搜尋條件"""
    keyword: str
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    category: Optional[str] = None
    posted_within_days: Optional[int] = None  # 最近 N 天內發布
    
    def to_seek_params(self) -> Dict[str, Any]:
        """轉換為 SEEK 搜尋參數"""
        params = {
            'keywords': self.keyword
        }
        
        if self.location:
            params['where'] = self.location
            
        if self.job_type:
            # SEEK 使用的工作類型代碼
            job_type_map = {
                JobType.FULL_TIME: 'full-time',
                JobType.PART_TIME: 'part-time',
                JobType.CONTRACT: 'contract-temp',
                JobType.CASUAL: 'casual',
                JobType.TEMPORARY: 'contract-temp',
                JobType.INTERNSHIP: 'graduate'
            }
            params['worktype'] = job_type_map.get(self.job_type)
            
        if self.salary_min or self.salary_max:
            # SEEK 薪資範圍參數（需要根據實際情況調整）
            salary_ranges = [
                (0, 50000, '0-50k'),
                (50000, 70000, '50k-70k'),
                (70000, 90000, '70k-90k'),
                (90000, 110000, '90k-110k'),
                (110000, 130000, '110k-130k'),
                (130000, 150000, '130k-150k'),
                (150000, float('inf'), '150k+')
            ]
            
            for min_sal, max_sal, seek_range in salary_ranges:
                if (self.salary_min is None or self.salary_min >= min_sal) and \
                   (self.salary_max is None or self.salary_max <= max_sal):
                    params['salaryrange'] = seek_range
                    break
        
        return params