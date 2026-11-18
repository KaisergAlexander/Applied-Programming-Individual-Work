"""Step 2: Match Engine.

Scores every job collected in Step 1 against the candidate profile and
writes a ranked shortlist to data/matches_{timestamp}.json.

Scoring is a transparent, weighted rule-based function (0-100), not a
model — each factor's weight is a constant below so it can be tuned later
without touching the scoring logic itself.

NOTE: the profile is loaded from "profile.json" in the project root (gitignored,
personal data). If it is missing, the fictional "profile.example.json" is used.
"""

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"
# Your real profile lives in profile.json (gitignored, contains personal data).
# If it does not exist, the fictional profile.example.json is used instead.
_REAL_PROFILE = PROJECT_DIR / "profile.json"
PROFILE_PATH = _REAL_PROFILE if _REAL_PROFILE.exists() else PROJECT_DIR / "profile.example.json"

# --- Scoring weights (sum to 100 across categories; tune here) -------------
WEIGHT_TITLE = 35
WEIGHT_LOCATION = 20
WEIGHT_WORK_MODE = 15
WEIGHT_EMPLOYMENT_TYPE = 10
WEIGHT_EXPERIENCE = 15
WEIGHT_LANGUAGE = 5  # treated as a pass/fail bonus: full marks unless a gap is found

# Title relevance tiers (assumption: exact target-industry words score
# highest; adjacent role vocabulary drawn from the candidate's own past
# titles/achievements scores a middle tier; everything else is a low
# baseline rather than zero, since Step 1 collects entire company boards,
# not just relevant postings).
# TODO: STRONG_/MODERATE_TITLE_KEYWORDS are hardcoded for a Finance/Strategy
# profile. They should really be derived from profile["preferences"]
# ["target_industries"] so this scores correctly for a different candidate
# (e.g. someone targeting Pharma/Life Sciences) instead of always assuming
# Finance/Strategy. Left hardcoded for now since we're only testing with
# one finance/strategy profile — revisit if this needs to generalize.
STRONG_TITLE_KEYWORDS = ["strategy", "finance", "financial"]
MODERATE_TITLE_KEYWORDS = [
    "investment", "venture capital", "investor relations", "consulting",
    "corporate development", "m&a", "business development", "analyst",
    "product management", "transfer pricing", "tax", "audit", "treasury",
    "controlling", "fp&a",
]

# CEFR-style proficiency ranking used to compare a job's language
# requirement against the candidate's declared level.
PROFICIENCY_RANK = {
    "a1": 1, "a2": 2, "b1": 3, "b2": 4, "c1": 5, "c2": 6,
    "beginner": 1, "elementary": 2, "intermediate": 3,
    "upper intermediate": 4, "advanced": 5,
    "fluent": 6, "native": 7,
}

EXPERIENCE_TOLERANCE_YEARS = 0.5  # required_min within this margin still counts as "meets"
EXPERIENCE_STRETCH_YEARS = 1.5    # required_min within this margin counts as "stretch"

# Academic-track roles that can lexically contain "finance"/"strategy" but
# are a structurally different career path from corporate Finance/Strategy
# roles. Checked against job_title ONLY (never description/requirements
# text), so a posting that merely mentions "PhD preferred" as a nice-to-have
# is not excluded — only postings where the role itself is academic.
EXCLUDED_TITLE_KEYWORDS = ["professor", "lecturer", "postdoctoral", "postdoc"]


def load_latest_jobs_file() -> Path:
    candidates = sorted(DATA_DIR.glob("jobs_*.json"))
    if not candidates:
        raise FileNotFoundError(f"No jobs_*.json files found in {DATA_DIR}")
    return candidates[-1]


def parse_ym(value: str) -> date:
    year, month = (int(part) for part in value.split("-"))
    return date(year, month, 1)


def estimate_candidate_experience_years(profile: dict) -> float:
    """Rough sum of elapsed calendar time across all professional_experience
    entries (internships/Werkstudent roles counted at full calendar
    duration, not FTE-adjusted — a deliberate simplification for an
    early-career profile where every role is part-time or an internship).
    """
    today = datetime.now(timezone.utc).date()
    total_months = 0
    for entry in profile.get("professional_experience", []):
        start = parse_ym(entry["start_date"])
        end = today if entry.get("is_current") else parse_ym(entry["end_date"])
        months = (end.year - start.year) * 12 + (end.month - start.month)
        total_months += max(months, 0)
    return round(total_months / 12, 2)


def _contains_keyword(text: str, keywords: list[str]) -> bool:
    # Word-boundary match so short keywords (e.g. "tax") don't false-positive
    # inside unrelated words.
    return any(re.search(rf"\b{re.escape(kw)}\b", text) for kw in keywords)


def score_title(job_title: str | None) -> tuple[int, str]:
    if not job_title:
        return 5, "no job title to assess"
    title_lower = job_title.lower()
    if _contains_keyword(title_lower, EXCLUDED_TITLE_KEYWORDS):
        return 0, "excluded: academic-track title, not corporate Finance/Strategy"
    if _contains_keyword(title_lower, STRONG_TITLE_KEYWORDS):
        return WEIGHT_TITLE, "strong title match (Finance/Strategy)"
    if _contains_keyword(title_lower, MODERATE_TITLE_KEYWORDS):
        return round(WEIGHT_TITLE * 0.6), "adjacent title match"
    return 5, "title not clearly Finance/Strategy-related"


def score_location(job_location: dict, target_countries: set[str]) -> tuple[int, str]:
    country = (job_location or {}).get("country")
    if country is None:
        return 8, "location unknown"
    if country in target_countries:
        return WEIGHT_LOCATION, f"{country} location match"
    return 3, f"location outside target countries ({country})"


def score_work_mode(work_mode: str | None) -> tuple[int, str]:
    if work_mode is None:
        return 8, "work mode unstated"
    if work_mode == "On-site":
        return WEIGHT_WORK_MODE, "on-site"
    if work_mode == "Hybrid":
        return round(WEIGHT_WORK_MODE * 0.4), "hybrid (partial on-site)"
    return 0, "remote (does not match on-site preference)"


def score_employment_type(employment_type: str | None, sought: set[str]) -> tuple[int, str]:
    if not employment_type:
        return 6, "employment type unstated"
    normalized = employment_type.strip().lower().replace("-", " ")
    sought_normalized = {s.lower().replace("-", " ") for s in sought}
    if normalized in sought_normalized:
        return WEIGHT_EMPLOYMENT_TYPE, f"employment type match ({employment_type})"
    return 0, f"employment type mismatch ({employment_type})"


def score_experience(required_experience_years: dict | None, candidate_years: float) -> tuple[int, str]:
    if not required_experience_years or required_experience_years.get("min") is None:
        return 10, "no experience requirement stated"
    required_min = required_experience_years["min"]
    if required_min <= candidate_years + EXPERIENCE_TOLERANCE_YEARS:
        return WEIGHT_EXPERIENCE, f"experience fits (requires {required_min}+y, candidate ~{candidate_years}y)"
    if required_min <= candidate_years + EXPERIENCE_STRETCH_YEARS:
        return 8, f"experience is a stretch (requires {required_min}+y, candidate ~{candidate_years}y)"
    return 2, f"likely underqualified (requires {required_min}+y, candidate ~{candidate_years}y)"


def _parse_language_requirement(entry: str) -> tuple[str, str | None]:
    match = re.match(r"^(.*?)\s*\(([A-Za-z ]+)\)\s*$", entry.strip())
    if match:
        return match.group(1).strip().lower(), match.group(2).strip().lower()
    return entry.strip().lower(), None


def score_language(language_requirements: list[str], candidate_languages: dict[str, int]) -> tuple[int, str]:
    if not language_requirements:
        return WEIGHT_LANGUAGE, "no language gap"
    for entry in language_requirements:
        lang, level = _parse_language_requirement(entry)
        candidate_rank = candidate_languages.get(lang)
        if candidate_rank is None:
            return 0, f"language gap: requires {entry}, candidate has no listed proficiency"
        if level:
            required_rank = PROFICIENCY_RANK.get(level)
            if required_rank and candidate_rank < required_rank:
                return 0, f"language gap: requires {entry}, candidate proficiency is lower"
    return WEIGHT_LANGUAGE, "no language gap"


def build_candidate_language_ranks(profile: dict) -> dict[str, int]:
    ranks = {}
    for entry in profile.get("skills", {}).get("languages", []):
        language = entry["language"].strip().lower()
        proficiency = entry["proficiency"].lower()
        rank = 0
        for key, value in PROFICIENCY_RANK.items():
            if key in proficiency:
                rank = max(rank, value)
        ranks[language] = rank
    return ranks


def score_job(job: dict, profile: dict, candidate_years: float, candidate_languages: dict[str, int]) -> tuple[int, str]:
    preferences = profile["preferences"]
    target_countries = {loc["country"] for loc in preferences["target_locations"] if loc.get("country")}
    sought_employment_types = set(preferences["employment_types_sought"])

    title_score, title_reason = score_title(job.get("job_title"))
    location_score, location_reason = score_location(job.get("location"), target_countries)
    work_mode_score, work_mode_reason = score_work_mode(job.get("work_mode"))
    employment_score, employment_reason = score_employment_type(job.get("employment_type"), sought_employment_types)
    experience_score, experience_reason = score_experience(job.get("required_experience_years"), candidate_years)
    language_score, language_reason = score_language(job.get("language_requirements") or [], candidate_languages)

    total = title_score + location_score + work_mode_score + employment_score + experience_score + language_score
    reason = ", ".join([title_reason, location_reason, work_mode_reason, employment_reason, experience_reason, language_reason])
    return round(max(0, min(100, total))), reason


def main() -> None:
    jobs_path = load_latest_jobs_file()
    with open(jobs_path, encoding="utf-8") as f:
        jobs_data = json.load(f)

    with open(PROFILE_PATH, encoding="utf-8") as f:
        profile = json.load(f)

    candidate_years = estimate_candidate_experience_years(profile)
    candidate_languages = build_candidate_language_ranks(profile)

    matches = []
    for job in jobs_data["jobs"]:
        score, reason = score_job(job, profile, candidate_years, candidate_languages)
        matches.append({**job, "match_score": score, "match_reason": reason})

    matches.sort(key=lambda j: j["match_score"], reverse=True)

    output = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "profile_reference": {
            "file": PROFILE_PATH.name,
            "candidate_name": profile.get("personal_info", {}).get("full_name"),
            "estimated_experience_years": candidate_years,
        },
        "source_jobs_file": jobs_path.name,
        "scoring_weights": {
            "title": WEIGHT_TITLE,
            "location": WEIGHT_LOCATION,
            "work_mode": WEIGHT_WORK_MODE,
            "employment_type": WEIGHT_EMPLOYMENT_TYPE,
            "experience": WEIGHT_EXPERIENCE,
            "language": WEIGHT_LANGUAGE,
        },
        "match_count": len(matches),
        "matches": matches,
    }

    DATA_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = DATA_DIR / f"matches_{timestamp}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Scored {len(matches)} jobs against profile '{output['profile_reference']['candidate_name']}'")
    print(f"Candidate estimated experience: ~{candidate_years} years\n")
    print(f"Output -> {output_path}\n")
    print("Top 10 matches:")
    for job in matches[:10]:
        location = job.get("location", {}).get("raw") or "?"
        print(f"  [{job['match_score']:>3}] {job['job_title']} — {job['company']} ({location})")


if __name__ == "__main__":
    main()
