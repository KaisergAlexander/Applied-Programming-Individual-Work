"""Fetcher for the Adzuna Job Search API (requires an app id/key)."""

import os

import requests

ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"


def fetch_adzuna_jobs(
    country: str,
    keywords: list[str],
    results_per_page: int = 20,
    page: int = 1,
) -> list[dict]:
    """Return raw Adzuna results for a keyword/location search, or [] on failure."""
    app_id = os.environ.get("ADZUNA_APP_ID")
    app_key = os.environ.get("ADZUNA_API_KEY")
    if not app_id or not app_key:
        print("[adzuna] ADZUNA_APP_ID / ADZUNA_API_KEY not set, skipping Adzuna fetch")
        return []

    url = ADZUNA_BASE_URL.format(country=country, page=page)
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": " ".join(keywords),
        "results_per_page": results_per_page,
        "content-type": "application/json",
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"[adzuna] failed to fetch jobs for country='{country}': {exc}")
        return []
    return response.json().get("results", [])
