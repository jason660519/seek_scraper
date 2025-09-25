#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEEK爬蟲數據模型模組

定義爬蟲系統中使用的所有數據模型，使用Pydantic進行數據驗證和序列化。
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    """職位狀態枚舉"""
    ACTIVE = "active"
    EXPIRED = "expired"
    FILLED = "filled"
    DRAFT = "draft"

class JobType(str, Enum):
    """工作類型枚舉"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    CASUAL = "casual"
    INTERNSHIP = "internship"

class ExperienceLevel(str, Enum):
    """經驗等級枚舉"""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    EXECUTIVE = "executive"

class SalaryPeriod(str, Enum):
    """薪資週期枚舉"""
    HOURLY = "hourly"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUALLY = "annually"

class ProxyStatus(str, Enum):
    """代理狀態枚舉"""
    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"
    TESTING = "testing"

class AnonymityLevel(str, Enum):
    """匿名級別枚舉"""
    ELITE = "elite"
    ANONYMOUS = "anonymous"
    TRANSPARENT = "transparent"

class Company(BaseModel):
    """公司信息模型"""
    name: str = Field(..., description="公司名稱")
    company_id: Optional[str] = Field(None, description="公司ID")
    industry: Optional[str] = Field(None, description="行業分類")
    size: Optional[str] = Field(None, description="公司規模")
    website: Optional[HttpUrl] = Field(None, description="公司網站")
    logo_url: Optional[HttpUrl] = Field(None, description="公司Logo URL")
    description: Optional[str] = Field(None, description="公司描述")
    location: Optional[str] = Field(None, description="公司位置")

class Location(BaseModel):
    """位置信息模型"""
    city: str = Field(..., description="城市")
    state: Optional[str] = Field(None, description="州/省")
    country: str = Field("Australia", description="國家")
    postal_code: Optional[str] = Field(None, description="郵政編碼")
    suburb: Optional[str] = Field(None, description="郊區")
    is_remote: bool = Field(False, description="是否遠程工作")

class Salary(BaseModel):
    """薪資信息模型"""
    min_salary: Optional[float] = Field(None, description="最低薪資")
    max_salary: Optional[float] = Field(None, description="最高薪資")
    currency: str = Field("AUD", description="貨幣類型")
    period: SalaryPeriod = Field(SalaryPeriod.ANNUALLY, description="薪資週期")
    is_negotiable: bool = Field(False, description="是否可協商")

class Job(BaseModel):
    """職位信息模型"""
    job_id: str = Field(..., description="職位ID")
    title: str = Field(..., description="職位標題")
    company: Company = Field(..., description="公司信息")
    location: Location = Field(..., description="工作地點")
    salary: Optional[Salary] = Field(None, description="薪資信息")
    job_type: List[JobType] = Field(default_factory=list, description="工作類型")
    experience_level: Optional[ExperienceLevel] = Field(None, description="經驗等級")
    description: str = Field(..., description="職位描述")
    requirements: List[str] = Field(default_factory=list, description="職位要求")
    benefits: List[str] = Field(default_factory=list, description="福利待遇")
    posted_date: datetime = Field(..., description="發布日期")
    expiry_date: Optional[datetime] = Field(None, description="過期日期")
    application_url: HttpUrl = Field(..., description="申請鏈接")
    job_status: JobStatus = Field(JobStatus.ACTIVE, description="職位狀態")
    source: str = Field("seek", description="數據源")
    tags: List[str] = Field(default_factory=list, description="標籤")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="額外元數據")
    scraped_at: datetime = Field(default_factory=datetime.now, description="爬取時間")

class Proxy(BaseModel):
    """代理服務器模型"""
    id: Optional[int] = Field(None, description="代理ID")
    ip: str = Field(..., description="IP地址")
    port: int = Field(..., ge=1, le=65535, description="端口")
    protocol: str = Field("http", description="協議類型")
    username: Optional[str] = Field(None, description="用戶名")
    password: Optional[str] = Field(None, description="密碼")
    country: Optional[str] = Field(None, description="國家")
    city: Optional[str] = Field(None, description="城市")
    status: ProxyStatus = Field(ProxyStatus.UNKNOWN, description="代理狀態")
    score: int = Field(0, ge=0, le=100, description="評分")
    response_time: Optional[float] = Field(None, description="響應時間(秒)")
    anonymity_level: Optional[AnonymityLevel] = Field(None, description="匿名級別")
    last_tested: Optional[datetime] = Field(None, description="最後測試時間")
    created_at: datetime = Field(default_factory=datetime.now, description="創建時間")


class JobSearchParams(BaseModel):
    """SEEK 搜尋參數配置模型"""

    keywords: str = Field(..., min_length=1, description="搜尋關鍵字")
    location: Optional[str] = Field(None, description="搜尋地點")
    page: int = Field(1, ge=1, description="頁碼 (從 1 開始)")
    per_page: int = Field(20, ge=1, le=100, description="每頁結果數")
    sort_mode: str = Field("listed", description="排序模式，例如 listed、salary")
    salary_min: Optional[int] = Field(None, ge=0, description="最低薪資篩選")
    salary_max: Optional[int] = Field(None, ge=0, description="最高薪資篩選")
    work_types: List[JobType] = Field(default_factory=list, description="工作型態過濾")
    remote_only: bool = Field(False, description="是否僅遠端工作")
    posted_within_days: Optional[int] = Field(None, ge=1, le=31, description="發布天數內")

    def to_query_params(self) -> Dict[str, Any]:
        """轉換為提供給 SEEK API 的查詢參數"""

        params: Dict[str, Any] = {
            "keywords": self.keywords,
            "page": self.page - 1,  # SEEK 的 API 以 0 為起點
            "seekSelectFields": "roleTitle,listingDate,jobAdType,subClassification,"
            "workType,location,advertiser,bulletPoints,salary,teaser,"
            "solMetadata,jobId,jobUrl",
            "siteKey": "AU-Main",
            "sourcesystem": "houston",
            "sortmode": self.sort_mode,
            "pageSize": self.per_page,
        }

        if self.location:
            params["where"] = self.location
        if self.salary_min is not None:
            params["salaryrange"] = f"{self.salary_min}-"
        if self.salary_min is not None and self.salary_max is not None:
            params["salaryrange"] = f"{self.salary_min}-{self.salary_max}"
        elif self.salary_max is not None:
            params["salaryrange"] = f"-{self.salary_max}"

        if self.work_types:
            params["worktype"] = ",".join(work_type.value for work_type in self.work_types)

        if self.remote_only:
            params["isremotejob"] = "true"

        if self.posted_within_days is not None:
            params["daterange"] = str(self.posted_within_days)

        return params


__all__ = [
    "Company",
    "Location",
    "Salary",
    "Job",
    "Proxy",
    "JobStatus",
    "JobType",
    "ExperienceLevel",
    "SalaryPeriod",
    "ProxyStatus",
    "AnonymityLevel",
    "JobSearchParams",
]