# Step 1: Data Collection — Context Document

**Project:** Automated Job Finder & Application Tool (Applied Programming & AI)
**Workflow:** 1. Collect Data (Jobs, Profile) → 2. Match Engine → 3. Application → 4. Job Preparation
**This document covers:** Step 1 only, and only the *jobs* side of data collection (profile data collection is deferred).

---

## 1. Scope

- Build a proof of concept that collects **open job listings** from 1–2 platforms.
- Output a single **structured JSON file** per collection run.
- Filtering, scoring, and matching against a candidate profile happen in **Step 2** — this step only normalizes raw postings into a consistent schema.
- Design choices below (fields, sources) should make it straightforward to add more sources later without changing the schema.

---

## 2. Data Sources

| Source | Type | Why |
|---|---|---|
| **Greenhouse & Lever job board APIs** | Public, unauthenticated JSON per company (`boards-api.greenhouse.io/v1/boards/{company}/jobs`, `api.lever.co/v0/postings/{company}`) | Same schema across every company — scaling from 2 to 10+ sources means adding company slugs, not new parsing logic |
| **Adzuna Job Search API** | Free-tier (~1,000 calls/month), keyword + location search, JSON | Multi-employer aggregation in one call, covers Germany and Portugal |

**Explicitly excluded for this POC:**
- **LinkedIn** — no public jobs API; scraping it violates its terms of service.
- **Indeed** — its job-search-oriented public API (Publisher Jobs API) has been deprecated.

*(Assumption — confirm or adjust: these two sources are treated as the POC baseline, to be scaled to 10+ ATS-based sources plus Adzuna later.)*

## 3. Target Scope for Testing

*(Assumption — confirm or adjust)*
- Roles: Finance / Strategy
- Locations: Germany & Portugal
- Tech stack: Python

## 4. Output File Structure

Each collection run produces one JSON file with a metadata envelope wrapping the job array — this keeps run-level info (when it ran, which sources, how many results) alongside the data itself.

```json
{
  "schema_version": "1.0",
  "collected_at": "2026-09-09T10:00:00Z",
  "sources": ["greenhouse", "lever", "adzuna"],
  "job_count": 1,
  "jobs": [
    {
      "id": "greenhouse_acme_98213",
      "source": "greenhouse",
      "source_job_id": "98213",
      "date_scraped": "2026-09-09T10:00:00Z",

      "company": "Acme Corp",
      "job_title": "Strategy Intern",
      "department": "Corporate Strategy",
      "industry": null,

      "location": { "city": "Berlin", "country": "DE", "raw": "Berlin, Germany" },
      "work_mode": "Hybrid",

      "employment_type": "Internship",
      "duration": "6 months",
      "date_posted": "2026-08-20",
      "application_deadline": null,
      "desired_start_date": "2027-02-01",

      "salary": { "min": null, "max": null, "currency": "EUR", "period": null, "raw": null },
      "required_experience_years": { "min": 0, "max": 1 },
      "education_requirement": "Bachelor",
      "language_requirements": ["English", "German (B2)"],
      "visa_sponsorship": null,

      "required_skills": ["Excel", "PowerPoint", "Financial Modeling"],
      "benefits": ["Meal allowance", "Public transport ticket"],
      "description": "...",

      "contact_name": null,
      "contact_email": null,

      "job_url": "https://boards.greenhouse.io/acme/jobs/98213",
      "apply_url": "https://boards.greenhouse.io/acme/jobs/98213#apply",
      "status": "open"
    }
  ]
}
```

**ID generation:** `id` = `{source}_{company_slug}_{source_job_id}`, kept distinct from `source_job_id` (the platform's own ID) so the same posting can be re-fetched or matched across sources without collision.

## 5. Known Data Gaps (by design, not bugs)

- **`industry`** — not present in raw postings; would require a separate company lookup/enrichment step, out of scope for now.
- **`benefits`, `required_skills`, `required_experience_years`** — rarely structured fields in the raw source; extracted from free-text `description` via keyword matching or light NLP as part of this step.
- **`salary`** — expect frequent nulls, especially for German postings. The EU Pay Transparency Directive required salary ranges in job ads EU-wide from June 7, 2026, but Germany hasn't finished national transposition and only ~15.8% of German postings currently disclose salary. Portugal already had its own transparency law beforehand, so PT postings may populate this more often.
- **`contact_name` / `contact_email`** — rarely present in ATS feeds. If captured, treat as personal data under GDPR: fine for internal/educational use, not for redistribution.

## 6. Next Steps (not yet started)

- Write fetch scripts for Greenhouse/Lever (per-company) and Adzuna (keyword/location search)
- Implement text-parsing for skills/benefits/experience from `description`
- Validate output against this schema before handing off to Step 2
