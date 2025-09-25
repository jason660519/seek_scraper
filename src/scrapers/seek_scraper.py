"""Concrete SEEK scraper implementation built atop :mod:`BaseScraper`."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Iterable, List, Optional, Sequence

import httpx

from src.models.models import Job, JobSearchParams
from src.parsers.job_parser import JobParser
from src.scrapers.base_scraper import BaseScraper
from src.utils.logger import get_logger


class SeekScraper(BaseScraper):
	"""High level interface for collecting job data from SEEK."""

	def __init__(
		self,
		*,
		parser: Optional[JobParser] = None,
		client: Optional[httpx.AsyncClient] = None,
	) -> None:
		super().__init__(client=client, logger_name="seek_scraper")
		self.parser = parser or JobParser()
		self.logger = get_logger("seek_scraper")

	async def search_jobs(self, params: JobSearchParams) -> List[Job]:
		"""Execute a SEEK search query and return structured job objects."""

		query_params = params.to_query_params()
		self.logger.debug("Searching SEEK", extra={"query": query_params})

		response = await self.request("GET", self.http_config.search_endpoint, params=query_params)
		payload = response.json()
		jobs = self.parser.parse_seek_results(payload, search_params=params)

		self.logger.info("Retrieved %s jobs for keywords '%s'", len(jobs), params.keywords)
		return jobs

	async def fetch_job_detail_html(self, job: Job) -> str:
		"""Fetch the HTML detail page for a given job."""

		endpoint = self.http_config.job_detail_endpoint.format(job_id=job.job_id)
		response = await self.request("GET", endpoint)
		return response.text

	async def enrich_jobs_with_details(self, jobs: Sequence[Job]) -> List[Job]:
		"""Fetch and merge detail information for each job in sequence."""

		tasks = [self.fetch_job_detail_html(job) for job in jobs]
		html_pages = await asyncio.gather(*tasks, return_exceptions=True)

		enriched: List[Job] = []
		for job, page in zip(jobs, html_pages):
			if isinstance(page, Exception):
				self.logger.error(
					"Failed to fetch job detail",
					exc_info=page,
					extra={"job_id": job.job_id},
				)
				enriched.append(job)
				continue

			enriched.append(self.parser.enrich_with_detail(job, page))

		return enriched

	async def scrape(
		self,
		params: JobSearchParams,
		*,
		include_details: bool = False,
	) -> List[Job]:
		"""Full scrape workflow for a single search configuration."""

		jobs = await self.search_jobs(params)
		if include_details and jobs:
			jobs = await self.enrich_jobs_with_details(jobs)
		return jobs


__all__ = ["SeekScraper"]
