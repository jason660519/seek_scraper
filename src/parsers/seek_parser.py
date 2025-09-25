"""Parsers dedicated to translating SEEK payloads into domain models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from src.models.models import (
	Company,
	ExperienceLevel,
	Job,
	JobSearchParams,
	JobType,
	Location,
	Salary,
	SalaryPeriod,
)
from src.utils.logger import get_logger


class SeekParser:
	"""Parse SEEK responses into strongly-typed data models."""

	_JOB_TYPE_MAPPING = {
		"full time": JobType.FULL_TIME,
		"full-time": JobType.FULL_TIME,
		"part time": JobType.PART_TIME,
		"part-time": JobType.PART_TIME,
		"contract": JobType.CONTRACT,
		"temp": JobType.CONTRACT,
		"casual": JobType.CASUAL,
		"vacation": JobType.CASUAL,
		"internship": JobType.INTERNSHIP,
		"graduate": JobType.INTERNSHIP,
	}

	_SALARY_PERIOD_MAPPING = {
		"year": SalaryPeriod.ANNUALLY,
		"annual": SalaryPeriod.ANNUALLY,
		"annum": SalaryPeriod.ANNUALLY,
		"month": SalaryPeriod.MONTHLY,
		"week": SalaryPeriod.WEEKLY,
		"day": SalaryPeriod.DAILY if hasattr(SalaryPeriod, "DAILY") else SalaryPeriod.WEEKLY,  # type: ignore[attr-defined]
		"hour": SalaryPeriod.HOURLY,
	}

	_EXPERIENCE_MAPPING = {
		"entry": ExperienceLevel.ENTRY,
		"junior": ExperienceLevel.JUNIOR,
		"mid": ExperienceLevel.MID,
		"senior": ExperienceLevel.SENIOR,
		"lead": ExperienceLevel.SENIOR,
		"executive": ExperienceLevel.EXECUTIVE,
	}

	def __init__(self) -> None:
		self.logger = get_logger("parser")

	def parse_job_search_results(
		self,
		payload: Dict[str, Any],
		*,
		search_params: Optional[JobSearchParams] = None,
	) -> List[Job]:
		"""Convert a SEEK search payload into a list of :class:`Job` objects."""

		jobs: List[Job] = []

		raw_jobs = self._extract_job_items(payload)
		for item in raw_jobs:
			try:
				job = self._parse_job_item(item, search_params)
				jobs.append(job)
			except Exception as exc:  # pragma: no cover - logging only
				self.logger.error("Failed to parse job item", exc_info=exc, extra={"item": item})

		return jobs

	def parse_job_detail(self, html: str, *, base_job: Optional[Job] = None) -> Job:
		"""Parse a SEEK job detail HTML page into a :class:`Job` object."""

		soup = BeautifulSoup(html, "lxml")
		detail_section = soup.select_one("[data-automation='jobAdDetails']")

		description = detail_section.get_text("\n", strip=True) if detail_section else (base_job.description if base_job else "")

		requirements = [
			li.get_text(strip=True)
			for li in soup.select("[data-automation='jobAdRequirements'] li")
			if li.get_text(strip=True)
		]

		benefits = [
			li.get_text(strip=True)
			for li in soup.select("[data-automation='jobAdBenefits'] li")
			if li.get_text(strip=True)
		]

		if base_job:
			base_job.description = description or base_job.description
			if requirements:
				base_job.requirements = requirements
			if benefits:
				base_job.benefits = benefits
			return base_job

		raise ValueError("Base job must be provided when parsing job detail HTML")

	def _extract_job_items(self, payload: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
		data = payload.get("data") or payload.get("results") or payload

		possible_paths = [
			data.get("results"),
			data.get("jobs"),
			data.get("searchResults", {}).get("jobs") if isinstance(data.get("searchResults"), dict) else None,
		]

		for maybe in possible_paths:
			if isinstance(maybe, list):
				return maybe

		return []

	def _parse_job_item(
		self, item: Dict[str, Any], search_params: Optional[JobSearchParams]
	) -> Job:
		job_id = str(item.get("id") or item.get("jobId") or item.get("listingId"))
		if not job_id:
			raise ValueError("Missing job identifier")

		title = item.get("title") or item.get("roleTitle") or "Untitled role"

		advertiser = item.get("company") or item.get("advertiser") or {}
		company_name = (
			advertiser.get("name")
			or advertiser.get("displayName")
			or advertiser.get("description")
			or "Unknown company"
		)

		company = Company(
			name=company_name,
			company_id=str(advertiser.get("id") or advertiser.get("companyId") or ""),
			industry=item.get("classification", {}).get("description"),
		)

		location_data = item.get("location") or {}
		location_display = location_data.get("display") or location_data.get("label") or "Sydney NSW"
		city, state = self._split_location(location_display)
		location = Location(city=city, state=state, country=location_data.get("country") or "Australia")

		salary = self._parse_salary(item.get("salary") or {})

		work_type_raw = item.get("workType")
		job_types = self._parse_job_types(work_type_raw)

		experience = self._parse_experience(item.get("seniority") or item.get("experienceLevel"))

		posted = self._parse_datetime(
			item.get("listingDate")
			or item.get("listedAt")
			or item.get("postedAt")
			or datetime.utcnow().isoformat()
		)
		expiry = self._parse_optional_datetime(item.get("expiryDate") or item.get("closingDate"))

		url = item.get("jobUrl") or item.get("applyUrl") or f"https://www.seek.com.au/job/{job_id}"

		tags = item.get("tags") or []
		if isinstance(tags, dict):
			tags = list(tags.values())

		description = item.get("teaser") or item.get("summary") or item.get("shortDescription") or ""
		requirements = [
			req.strip()
			for req in item.get("bulletPoints") or []
			if isinstance(req, str) and req.strip()
		]

		metadata = {
			"search_params": search_params.model_dump() if search_params else {},
			"raw": item,
		}

		return Job(
			job_id=job_id,
			title=title,
			company=company,
			location=location,
			salary=salary,
			job_type=job_types,
			experience_level=experience,
			description=description,
			requirements=requirements,
			benefits=[],
			posted_date=posted,
			expiry_date=expiry,
			application_url=url,
			tags=tags,
			metadata=metadata,
		)

	def _parse_salary(self, salary_data: Dict[str, Any]) -> Optional[Salary]:
		if not salary_data:
			return None

		minimum = salary_data.get("minimum") or salary_data.get("salaryMin")
		maximum = salary_data.get("maximum") or salary_data.get("salaryMax")
		currency = salary_data.get("currency") or salary_data.get("currencyCode") or "AUD"
		raw_period = str(salary_data.get("interval") or salary_data.get("period") or "year").lower()
		period = self._SALARY_PERIOD_MAPPING.get(raw_period, SalaryPeriod.ANNUALLY)

		return Salary(
			min_salary=float(minimum) if minimum is not None else None,
			max_salary=float(maximum) if maximum is not None else None,
			currency=currency,
			period=period,
			is_negotiable=bool(salary_data.get("isNegotiable", False)),
		)

	def _parse_job_types(self, work_type: Any) -> List[JobType]:
		if not work_type:
			return []

		if isinstance(work_type, str):
			work_type_iterable = [work_type]
		elif isinstance(work_type, list):
			work_type_iterable = work_type
		else:
			work_type_iterable = []

		mapped: List[JobType] = []
		for work in work_type_iterable:
			key = str(work).strip().lower()
			if key in self._JOB_TYPE_MAPPING:
				mapped.append(self._JOB_TYPE_MAPPING[key])

		return mapped

	def _parse_experience(self, value: Any) -> Optional[ExperienceLevel]:
		if not value:
			return None
		return self._EXPERIENCE_MAPPING.get(str(value).strip().lower())

	def _parse_datetime(self, value: str) -> datetime:
		return date_parser.isoparse(value)

	def _parse_optional_datetime(self, value: Optional[str]) -> Optional[datetime]:
		if not value:
			return None
		return date_parser.isoparse(value)

	def _split_location(self, value: str) -> tuple[str, Optional[str]]:
		parts = [part.strip() for part in value.split(",") if part.strip()]
		if len(parts) >= 2:
			return parts[0], parts[1]
		if " " in value:
			tokens = value.split(" ")
			return tokens[0], tokens[-1]
		return value, None


__all__ = ["SeekParser"]
