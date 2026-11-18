"""Fetcher for the public, unauthenticated Greenhouse job board API."""

import requests

GREENHOUSE_BASE_URL = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"


def fetch_greenhouse_jobs(company_slug: str) -> list[dict]:
    """Return the raw job list for one Greenhouse board, or [] on failure."""
    url = GREENHOUSE_BASE_URL.format(company=company_slug)
    try:
        response = requests.get(url, params={"content": "true"}, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"[greenhouse] failed to fetch jobs for '{company_slug}': {exc}")
        return []
    return response.json().get("jobs", [])
