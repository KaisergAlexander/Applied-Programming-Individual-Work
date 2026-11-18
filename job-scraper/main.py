"""Runs all Step 1 fetchers, normalizes results, and writes one output file
per collection run (see step1-data-collection-context.md, section 4).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from config import (
    ADZUNA_COUNTRIES,
    ADZUNA_KEYWORDS,
    ADZUNA_MAX_PAGES,
    ADZUNA_RESULTS_PER_PAGE,
    GREENHOUSE_COMPANIES,
    LEVER_COMPANIES,
)
from fetchers.adzuna_fetcher import fetch_adzuna_jobs
from fetchers.greenhouse_fetcher import fetch_greenhouse_jobs
from fetchers.lever_fetcher import fetch_lever_jobs
from normalizer import normalize_adzuna, normalize_greenhouse, normalize_lever

DATA_DIR = Path(__file__).parent / "data"


def collect_greenhouse_jobs() -> list[dict]:
    jobs = []
    for entry in GREENHOUSE_COMPANIES:
        raw_jobs = fetch_greenhouse_jobs(entry["slug"])
        jobs.extend(normalize_greenhouse(raw, entry["slug"], entry["name"]) for raw in raw_jobs)
    return jobs


def collect_lever_jobs() -> list[dict]:
    jobs = []
    for entry in LEVER_COMPANIES:
        raw_jobs = fetch_lever_jobs(entry["slug"])
        jobs.extend(normalize_lever(raw, entry["slug"], entry["name"]) for raw in raw_jobs)
    return jobs


def collect_adzuna_jobs() -> list[dict]:
    jobs = []
    for country in ADZUNA_COUNTRIES:
        for page in range(1, ADZUNA_MAX_PAGES + 1):
            raw_jobs = fetch_adzuna_jobs(country, ADZUNA_KEYWORDS, ADZUNA_RESULTS_PER_PAGE, page)
            jobs.extend(normalize_adzuna(raw) for raw in raw_jobs)
    return jobs


def main() -> None:
    load_dotenv()
    DATA_DIR.mkdir(exist_ok=True)

    jobs = [
        *collect_greenhouse_jobs(),
        *collect_lever_jobs(),
        *collect_adzuna_jobs(),
    ]

    output = {
        "schema_version": "1.0",
        "collected_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": ["greenhouse", "lever", "adzuna"],
        "job_count": len(jobs),
        "jobs": jobs,
    }

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = DATA_DIR / f"jobs_{timestamp}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Collected {len(jobs)} jobs -> {output_path}")


if __name__ == "__main__":
    main()
