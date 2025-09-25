import json
from pathlib import Path

import pytest
import httpx

from src.models.models import JobSearchParams
from src.scrapers.seek_scraper import SeekScraper


@pytest.fixture()
def sample_payload() -> dict:
    path = Path(__file__).parent / "data" / "sample_seek_search.json"
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.mark.asyncio
async def test_seek_scraper_search_jobs_returns_parsed_jobs(sample_payload):
    params = JobSearchParams(keywords="data", location="Sydney")

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/search"):
            return httpx.Response(200, json=sample_payload)
        raise AssertionError(f"Unexpected URL {request.url}")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="https://www.seek.com.au") as client:
        scraper = SeekScraper(client=client)
        jobs = await scraper.search_jobs(params)

    assert len(jobs) == 2
    assert jobs[0].title == "Senior Data Engineer"


@pytest.mark.asyncio
async def test_seek_scraper_enriches_with_detail_html(sample_payload):
    params = JobSearchParams(keywords="data", location="Sydney")

    detail_html = """
    <div data-automation="jobAdDetails">Detailed description</div>
    <ul data-automation="jobAdBenefits"><li>Free coffee</li></ul>
    """

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/search"):
            return httpx.Response(200, json=sample_payload)
        if request.url.path.startswith("/job/"):
            return httpx.Response(200, text=detail_html)
        raise AssertionError(f"Unexpected URL {request.url}")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="https://www.seek.com.au") as client:
        scraper = SeekScraper(client=client)
        jobs = await scraper.scrape(params, include_details=True)

    assert jobs[0].description == "Detailed description"
    assert jobs[0].benefits == ["Free coffee"]
