"""Fetcher for the public, unauthenticated Lever postings API."""

import requests

LEVER_BASE_URL = "https://api.lever.co/v0/postings/{company}"


def fetch_lever_jobs(company_slug: str) -> list[dict]:
    """Return the raw job list for one Lever board, or [] on failure."""
    url = LEVER_BASE_URL.format(company=company_slug)
    try:
        response = requests.get(url, params={"mode": "json"}, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"[lever] failed to fetch jobs for '{company_slug}': {exc}")
        return []
    return response.json()  # Lever returns a bare list, not an envelope object
