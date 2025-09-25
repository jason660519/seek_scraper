import json
from pathlib import Path

from src.models.models import ExperienceLevel, JobSearchParams, JobType, SalaryPeriod
from src.parsers.seek_parser import SeekParser


def load_payload() -> dict:
    path = Path(__file__).parent / "data" / "sample_seek_search.json"
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def test_parse_job_search_results_creates_domain_models():
    payload = load_payload()
    parser = SeekParser()
    params = JobSearchParams(keywords="data engineer", location="Sydney")

    jobs = parser.parse_job_search_results(payload, search_params=params)

    assert len(jobs) == 2

    first = jobs[0]
    assert first.job_id == "123456"
    assert first.company.name == "ACME Co"
    assert first.location.city == "Sydney"
    assert first.salary and first.salary.max_salary == 150000
    assert first.salary.period == SalaryPeriod.ANNUALLY
    assert JobType.FULL_TIME in first.job_type
    assert first.metadata["search_params"]["keywords"] == "data engineer"

    second = jobs[1]
    assert second.job_id == "654321"
    assert second.company.name == "BetaTech"
    assert second.experience_level == ExperienceLevel.ENTRY
    assert JobType.PART_TIME in second.job_type
    assert second.salary and second.salary.min_salary == 65000


def test_parse_job_detail_enriches_existing_job():
    payload = load_payload()
    parser = SeekParser()
    job = parser.parse_job_search_results(payload)[0]

    html = """
    <div data-automation="jobAdDetails">
        <p>This role leads the data engineering practice.</p>
    </div>
    <ul data-automation="jobAdRequirements">
        <li>Extensive ETL experience</li>
        <li>Knowledge of cloud-native tooling</li>
    </ul>
    <ul data-automation="jobAdBenefits">
        <li>Hybrid working</li>
    </ul>
    """

    enriched = parser.parse_job_detail(html, base_job=job)

    assert "data engineering" in enriched.description
    assert enriched.requirements == [
        "Extensive ETL experience",
        "Knowledge of cloud-native tooling",
    ]
    assert enriched.benefits == ["Hybrid working"]
