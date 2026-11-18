# Progress — Automated Job Finder & Application Tool

**Workflow:** 1. Collect Data → 2. Match Engine → 3. Application → 4. Job Preparation

Last updated: 2026-09-14

## Step 1 — Data Collection: DONE

Scope and design documented in `step1-data-collection-context.md`.

- Sources: Greenhouse + Lever (per-company job board APIs) and Adzuna (keyword/location search).
- `config.py` holds 5 verified companies (checked live against the real APIs on 2026-09-14):
  - Greenhouse: `n26`, `celonis`, `getyourguide`, `helloFresh` (all Germany-headquartered)
  - Lever: `farfetch` (Portugal-headquartered)
- **Known limitation:** Adzuna does not support Portugal as a country code (`UNSUPPORTED_COUNTRY`). `ADZUNA_COUNTRIES` is `["de"]` only — Portugal coverage comes from the Farfetch/Lever board instead.
- `main.py` runs the full pipeline and writes `data/jobs_{timestamp}.json` (gitignored — generated output, not source).
- Latest run: 911 jobs collected (842 Greenhouse, 49 Lever, 20 Adzuna), 0 nulls in critical fields (`id`, `company`, `job_title`), 0 duplicate IDs.

## Step 2 — Match Engine: DONE

`match_engine.py` scores every job from the latest `data/jobs_*.json` against `profile.json` (root of the job-scraper folder, gitignored; falls back to `profile.example.json`).

- Transparent weighted rule-based score (0–100), not a model. Weights are constants at the top of the file:
  - Title relevance 35, Location 20, Work mode 15, Employment type 10, Experience fit 15, Language 5.
- Candidate's experience is estimated at ~2.42 years (summed calendar duration across `professional_experience` entries, current role counted to today).
- Output: `data/matches_{timestamp}.json` — jobs sorted descending by `match_score`, each with a human-readable `match_reason`.
- **Known limitations (intentionally left as-is for now):**
  - `STRONG_/MODERATE_TITLE_KEYWORDS` are hardcoded for a Finance/Strategy profile rather than derived from `profile["preferences"]["target_industries"]`. Fine while only testing with one finance/strategy profile; would need to generalize if scoring a different candidate (e.g. someone targeting Pharma/Life Sciences). Flagged with a `TODO` comment in the code.
  - `EXCLUDED_TITLE_KEYWORDS` (`professor`, `lecturer`, `postdoctoral`, `postdoc`) zeroes out title score for academic-track postings that would otherwise lexically match on "Finance"/"Strategy" — checked against `job_title` only, never description text, so a posting merely mentioning "PhD preferred" is unaffected.
  - One isolated Adzuna data quirk noted, not filtered: a single anonymized posting had its `company` field populated with description text ("Your mission This...") by Adzuna itself, not by our normalizer. Rare (1 of 20 Adzuna jobs) — not worth building a detection heuristic for.
  - Latest run: 28 jobs scored ≥70 (out of 911).

## Step 3 — Application Document Generation: SCAFFOLDED, PAUSED

`application_generator.py` is written but has **not been run yet** — paused pending the Anthropic API key / billing approval.

- Design: loads the latest `data/matches_*.json`, filters to `match_score >= 70` (falls back to top 10 if fewer than 10 clear the threshold — at last check, 28 jobs clear it, so the fallback wouldn't trigger), and calls the Anthropic API once per job to generate:
  1. A tailored CV positioning statement + reordered achievement list (`applications/{job_id}_cv_positioning.md`)
  2. A tailored cover letter draft (`applications/{job_id}_cover_letter.md`)
  - Plus `applications/index.json` summarizing which jobs succeeded/failed.
- System prompt explicitly forbids fabricating any experience/skill/achievement not present in the profile; only the relevant profile slices (experience, education, skills, preferences) are passed as context.
- Output language: English by default, German if the job posting itself is in German.
- Error handling: per-job try/except (NotFoundError, RateLimitError, APIStatusError, APIConnectionError, malformed-response) — one job failing doesn't stop the batch; relies on the SDK's built-in retry (no aggressive manual retry loop).
- `applications/` is gitignored (same convention as `data/`) since it will hold generated, potentially cost-incurring output.

**Model decision: made.** Using `claude-sonnet-5` ($2/$10 per 1M tokens).

**Open item before running:**
- No `ANTHROPIC_API_KEY` is configured anywhere in this environment yet — need the key and billing approval before this step can run.
- Estimated cost for the current 28-job shortlist: roughly $0.40–$0.60 total at Sonnet 5 rates — small, but real, and requires explicit go-ahead per project convention (this step makes real paid API calls).

## Step 4 — Job Preparation: NOT STARTED (on hold)

Intentionally not scoped yet — comes after Step 3 is unblocked and reviewed.

## Environment Notes

- Python venv at `.venv/`, dependencies in `requirements.txt` (`requests`, `python-dotenv`, `anthropic`).
- `.env` (gitignored) holds `ADZUNA_APP_ID` / `ADZUNA_API_KEY` (already set) and will need `ANTHROPIC_API_KEY` once Step 3 resumes.
