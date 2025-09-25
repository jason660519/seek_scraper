"""Command line entry point for the SEEK job crawler."""

from __future__ import annotations

import argparse
import asyncio
from typing import List

from src.models.models import Job, JobSearchParams
from src.scrapers.seek_scraper import SeekScraper
from src.services.data_service import DataService
from src.utils.logger import setup_logging


async def run_crawler(args: argparse.Namespace) -> List[Job]:
	setup_logging()

	scraper = SeekScraper()
	data_service = DataService()

	try:
		params = JobSearchParams(
			keywords=args.keywords,
			location=args.location,
			per_page=args.page_size,
			page=args.page,
			posted_within_days=args.posted_within,
		)

		jobs = await scraper.scrape(params, include_details=args.include_details)

		if args.output_format in {"json", "both"}:
			path = data_service.save_jobs_to_json(jobs)
			print(f"Saved JSON to {path}")

		if args.output_format in {"csv", "both"}:
			path = data_service.save_jobs_to_csv(jobs)
			print(f"Saved CSV to {path}")

		return jobs
	finally:
		await scraper.close()


def build_argument_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="SEEK Job Crawler")
	parser.add_argument("keywords", help="Keywords to search for")
	parser.add_argument("--location", default=None, help="Location filter (e.g. Sydney)")
	parser.add_argument("--page-size", type=int, default=20, help="Number of results per page")
	parser.add_argument("--page", type=int, default=1, help="Page number (1-indexed)")
	parser.add_argument(
		"--posted-within",
		type=int,
		default=None,
		help="Limit results to jobs posted within the given days",
	)
	parser.add_argument(
		"--include-details",
		action="store_true",
		help="Fetch and merge job detail pages",
	)
	parser.add_argument(
		"--output-format",
		choices=["json", "csv", "both"],
		default="json",
		help="Output format for saved files",
	)
	return parser


def main() -> None:
	parser = build_argument_parser()
	args = parser.parse_args()
	asyncio.run(run_crawler(args))


if __name__ == "__main__":
	main()
