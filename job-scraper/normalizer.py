"""Maps raw Greenhouse/Lever/Adzuna job payloads to the unified schema
defined in step1-data-collection-context.md, section 4.
"""

import re
from datetime import datetime, timezone

COUNTRY_NAME_TO_CODE = {
    "germany": "DE",
    "deutschland": "DE",
    "portugal": "PT",
    "austria": "AT",
    "switzerland": "CH",
    "netherlands": "NL",
    "france": "FR",
    "spain": "ES",
    "italy": "IT",
    "united kingdom": "GB",
    "uk": "GB",
    "united states": "US",
    "usa": "US",
    "denmark": "DK",
    "belgium": "BE",
    "poland": "PL",
    "ireland": "IE",
}

SKILL_KEYWORDS = [
    "Python", "SQL", "R", "VBA", "Excel", "PowerPoint", "Tableau", "Power BI",
    "Financial Modeling", "Financial Modelling", "Valuation", "DCF",
    "Bloomberg Terminal", "M&A", "Due Diligence", "Forecasting", "Budgeting",
    "Data Analysis", "Machine Learning",
]

BENEFIT_KEYWORDS = [
    "Meal allowance", "Public transport ticket", "Health insurance",
    "Remote work", "Flexible hours", "Gym membership",
    "Relocation assistance", "Visa sponsorship", "Learning budget",
    "Stock options", "Pension", "Company car", "Childcare",
]

LANGUAGE_KEYWORDS = ["English", "German", "Portuguese", "French", "Spanish", "Italian", "Dutch"]

WORKPLACE_TYPE_MAP = {"remote": "Remote", "hybrid": "Hybrid", "on-site": "On-site", "onsite": "On-site"}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_job_id(source: str, company_slug: str, source_job_id) -> str:
    slug = company_slug or "unknown"
    return f"{source}_{slug}_{source_job_id}"


def slugify(value: str) -> str:
    if not value:
        return "unknown"
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unknown"


def strip_html(html: str) -> str:
    if not html:
        return ""
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()


def parse_location(raw: str | None) -> dict:
    if not raw:
        return {"city": None, "country": None, "raw": raw}
    raw = raw.strip()
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if not parts:
        return {"city": None, "country": None, "raw": raw}

    last = parts[-1]
    country_code = COUNTRY_NAME_TO_CODE.get(last.lower())
    if country_code is None and len(last) == 2 and last.isalpha():
        country_code = last.upper()

    if country_code is not None:
        city = parts[0] if len(parts) > 1 else None
    else:
        city = parts[0]
    return {"city": city, "country": country_code, "raw": raw}


def extract_work_mode(text_blob: str) -> str | None:
    if not text_blob:
        return None
    lowered = text_blob.lower()
    if "hybrid" in lowered:
        return "Hybrid"
    if "remote" in lowered:
        return "Remote"
    if "on-site" in lowered or "onsite" in lowered or "on site" in lowered:
        return "On-site"
    return None


def _match_keywords(text_blob: str, keywords: list[str]) -> list[str]:
    if not text_blob:
        return []
    return [kw for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", text_blob, re.IGNORECASE)]


def extract_skills(text_blob: str) -> list[str]:
    return _match_keywords(text_blob, SKILL_KEYWORDS)


def extract_benefits(text_blob: str) -> list[str]:
    return _match_keywords(text_blob, BENEFIT_KEYWORDS)


def extract_experience_years(text_blob: str) -> dict | None:
    if not text_blob:
        return None
    match = re.search(r"(\d+)\s*(?:\+|to|-)\s*(\d+)?\s*years?", text_blob, re.IGNORECASE)
    if match:
        return {"min": int(match.group(1)), "max": int(match.group(2)) if match.group(2) else None}
    match = re.search(r"at least\s*(\d+)\s*years?", text_blob, re.IGNORECASE)
    if match:
        return {"min": int(match.group(1)), "max": None}
    return None


def extract_languages(text_blob: str) -> list[str]:
    if not text_blob:
        return []
    found = []
    for lang in LANGUAGE_KEYWORDS:
        level_match = re.search(rf"\b{lang}\b\s*\(?([ABC][12])\)?", text_blob, re.IGNORECASE)
        if level_match:
            found.append(f"{lang} ({level_match.group(1).upper()})")
        elif re.search(rf"\b{lang}\b", text_blob, re.IGNORECASE):
            found.append(lang)
    return found


def normalize_greenhouse(raw_job: dict, company_slug: str, company_name: str) -> dict:
    description = strip_html(raw_job.get("content", ""))
    location_raw = (raw_job.get("location") or {}).get("name")
    departments = raw_job.get("departments") or []

    return {
        "id": build_job_id("greenhouse", company_slug, raw_job.get("id")),
        "source": "greenhouse",
        "source_job_id": str(raw_job.get("id")),
        "date_scraped": now_iso(),

        "company": company_name,
        "job_title": raw_job.get("title"),
        "department": departments[0].get("name") if departments else None,
        "industry": None,  # requires separate company enrichment — see context doc section 5

        "location": parse_location(location_raw),
        "work_mode": extract_work_mode(f"{location_raw or ''} {description}"),

        "employment_type": None,  # Greenhouse board API has no structured field for this
        "duration": None,
        "date_posted": raw_job.get("updated_at"),  # closest available field; no original-post-date field exists
        "application_deadline": None,
        "desired_start_date": None,

        "salary": {"min": None, "max": None, "currency": None, "period": None, "raw": None},
        "required_experience_years": extract_experience_years(description),
        "education_requirement": None,
        "language_requirements": extract_languages(description),
        "visa_sponsorship": None,

        "required_skills": extract_skills(description),
        "benefits": extract_benefits(description),
        "description": description,

        # Greenhouse board API responses don't expose recruiter contact details.
        "contact_name": None,
        "contact_email": None,

        "job_url": raw_job.get("absolute_url"),
        "apply_url": raw_job.get("absolute_url"),
        "status": "open",
    }


def normalize_lever(raw_job: dict, company_slug: str, company_name: str) -> dict:
    categories = raw_job.get("categories") or {}
    description_plain = raw_job.get("descriptionPlain") or raw_job.get("description") or ""
    lists = raw_job.get("lists") or []
    extra_text = " ".join(strip_html(item.get("content", "")) for item in lists)
    full_text = f"{description_plain} {extra_text}".strip()

    location_raw = categories.get("location")

    created_at_ms = raw_job.get("createdAt")
    date_posted = None
    if created_at_ms:
        date_posted = datetime.fromtimestamp(created_at_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")

    workplace_type = (raw_job.get("workplaceType") or "").lower()
    work_mode = WORKPLACE_TYPE_MAP.get(workplace_type) or extract_work_mode(f"{location_raw or ''} {full_text}")

    return {
        "id": build_job_id("lever", company_slug, raw_job.get("id")),
        "source": "lever",
        "source_job_id": str(raw_job.get("id")),
        "date_scraped": now_iso(),

        "company": company_name,
        "job_title": raw_job.get("text"),
        "department": categories.get("team"),
        "industry": None,  # requires separate company enrichment — see context doc section 5

        "location": parse_location(location_raw),
        "work_mode": work_mode,

        "employment_type": categories.get("commitment"),
        "duration": None,
        "date_posted": date_posted,
        "application_deadline": None,
        "desired_start_date": None,

        "salary": {"min": None, "max": None, "currency": None, "period": None, "raw": None},
        "required_experience_years": extract_experience_years(full_text),
        "education_requirement": None,
        "language_requirements": extract_languages(full_text),
        "visa_sponsorship": None,

        "required_skills": extract_skills(full_text),
        "benefits": extract_benefits(full_text),
        "description": full_text,

        # Lever postings API responses don't expose recruiter contact details.
        "contact_name": None,
        "contact_email": None,

        "job_url": raw_job.get("hostedUrl"),
        "apply_url": raw_job.get("applyUrl") or raw_job.get("hostedUrl"),
        "status": "open",
    }


def normalize_adzuna(raw_job: dict) -> dict:
    description = raw_job.get("description") or ""
    company_name = (raw_job.get("company") or {}).get("display_name")
    location_raw = (raw_job.get("location") or {}).get("display_name")

    salary_min = raw_job.get("salary_min")
    salary_max = raw_job.get("salary_max")
    has_salary = salary_min is not None or salary_max is not None
    salary = {
        "min": salary_min,
        "max": salary_max,
        "currency": "EUR" if has_salary else None,
        "period": "year" if has_salary else None,
        "raw": None,
    }

    contract_time = raw_job.get("contract_time")  # "full_time" | "part_time"
    employment_type = contract_time.replace("_", "-").title() if contract_time else raw_job.get("contract_type")

    created = raw_job.get("created")
    date_posted = created.split("T")[0] if created else None

    # Adzuna aggregates postings from many employers — there's no stable
    # per-employer slug like Greenhouse/Lever provide, so derive one from
    # the company's display name for the id.
    company_slug = slugify(company_name)

    return {
        "id": build_job_id("adzuna", company_slug, raw_job.get("id")),
        "source": "adzuna",
        "source_job_id": str(raw_job.get("id")),
        "date_scraped": now_iso(),

        "company": company_name,
        "job_title": raw_job.get("title"),
        "department": None,
        "industry": None,  # requires separate company enrichment — see context doc section 5

        "location": parse_location(location_raw),
        "work_mode": extract_work_mode(f"{location_raw or ''} {description}"),

        "employment_type": employment_type,
        "duration": None,
        "date_posted": date_posted,
        "application_deadline": None,
        "desired_start_date": None,

        "salary": salary,
        "required_experience_years": extract_experience_years(description),
        "education_requirement": None,
        "language_requirements": extract_languages(description),
        "visa_sponsorship": None,

        "required_skills": extract_skills(description),
        "benefits": extract_benefits(description),
        "description": description,

        # Adzuna is an aggregator; original recruiter contact details (if any)
        # are not exposed by the API.
        "contact_name": None,
        "contact_email": None,

        "job_url": raw_job.get("redirect_url"),
        "apply_url": raw_job.get("redirect_url"),
        "status": "open",
    }
