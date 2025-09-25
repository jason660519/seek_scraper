"""High level job parsing utilities that orchestrate provider-specific parsers."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from src.models.models import Job, JobSearchParams
from src.parsers.seek_parser import SeekParser


class JobParser:
	"""Facade that routes payloads to the appropriate provider parser."""

	def __init__(self, *, seek_parser: Optional[SeekParser] = None) -> None:
		self.seek_parser = seek_parser or SeekParser()

	def parse_seek_results(
		self, payload: Dict[str, Any], *, search_params: Optional[JobSearchParams] = None
	) -> List[Job]:
		"""Parse SEEK search results payload."""

		return self.seek_parser.parse_job_search_results(payload, search_params=search_params)

	def enrich_with_detail(self, job: Job, html: str) -> Job:
		"""Enrich a job with detail HTML content."""

		return self.seek_parser.parse_job_detail(html, base_job=job)


__all__ = ["JobParser"]
