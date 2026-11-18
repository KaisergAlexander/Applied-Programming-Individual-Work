"""Step 3: Application document generation.

Takes the top-scoring jobs from Step 2's match_engine output and, for each,
asks Claude to draft a tailored CV positioning note + cover letter. This
step makes real, paid Anthropic API calls — see main() for the guardrails
(threshold/fallback sizing, per-job error isolation, no aggressive retry
looping).

Requires ANTHROPIC_API_KEY in the environment (loaded via .env, same as
the rest of this project).
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import anthropic
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"
APPLICATIONS_DIR = PROJECT_DIR / "applications"
# Your real profile lives in profile.json (gitignored, contains personal data).
# If it does not exist, the fictional profile.example.json is used instead.
_REAL_PROFILE = PROJECT_DIR / "profile.json"
PROFILE_PATH = _REAL_PROFILE if _REAL_PROFILE.exists() else PROJECT_DIR / "profile.example.json"

# Model decision confirmed by the team: claude-sonnet-5.
MODEL = "claude-sonnet-5"

SCORE_THRESHOLD = 70
FALLBACK_TOP_N = 10  # used only if fewer than this many jobs clear the threshold

CV_DELIMITER = "===CV_POSITIONING==="
LETTER_DELIMITER = "===COVER_LETTER==="

SYSTEM_PROMPT = f"""You are a careful, honest career-application assistant helping a real \
candidate tailor application materials to one specific job posting.

STRICT RULE: You must never invent, exaggerate, or imply any experience, skill, \
achievement, qualification, or credential that is not explicitly present in the \
candidate profile JSON you are given. If the posting asks for something the \
candidate profile does not show, either omit it or, if there is a genuinely close \
transferable achievement already in the profile, reference that truthfully — do not \
claim direct experience that doesn't exist. Every claim you write must be traceable \
to a specific field in the provided profile.

LANGUAGE: Write your entire output in English, unless the job posting text itself is \
clearly written in German — in that case, write your entire output in German instead.

OUTPUT FORMAT: Return exactly two sections, in this order, each starting on its own \
line with the literal marker shown (no markdown headers, no extra commentary before, \
between, or after the sections):

{CV_DELIMITER}
<2-4 sentence positioning statement tailored to this role, followed by a short ordered \
list of which existing achievements from the profile to lead with for this job and why \
they're relevant — reference them the way they appear in the profile (company/title + \
achievement), don't reword them into new claims>

{LETTER_DELIMITER}
<a complete, professional cover letter draft addressed to the specific company and \
role, 250-400 words, drawing only on real profile content>
"""


def load_latest_matches_file() -> Path:
    candidates = sorted(DATA_DIR.glob("matches_*.json"))
    if not candidates:
        raise FileNotFoundError(f"No matches_*.json files found in {DATA_DIR}")
    return candidates[-1]


def select_shortlist(matches: list[dict]) -> list[dict]:
    shortlist = [m for m in matches if m["match_score"] >= SCORE_THRESHOLD]
    if len(shortlist) < FALLBACK_TOP_N:
        shortlist = matches[:FALLBACK_TOP_N]
    return shortlist


def build_profile_context(profile: dict) -> dict:
    """Only the slices of the profile relevant to tailoring (drop unrelated
    fields like address/phone/extracurriculars/awards to keep the prompt
    focused and reduce the chance of the model reaching for filler)."""
    return {
        "full_name": profile["personal_info"]["full_name"],
        "professional_experience": profile["professional_experience"],
        "education": profile["education"],
        "skills": profile["skills"],
        "preferences": profile["preferences"],
    }


def build_user_message(job: dict, profile_context: dict) -> str:
    job_summary = {
        "company": job.get("company"),
        "job_title": job.get("job_title"),
        "location": job.get("location"),
        "work_mode": job.get("work_mode"),
        "employment_type": job.get("employment_type"),
        "required_experience_years": job.get("required_experience_years"),
        "required_skills": job.get("required_skills"),
        "language_requirements": job.get("language_requirements"),
        "description": job.get("description"),
    }
    return (
        "JOB POSTING:\n"
        f"{json.dumps(job_summary, indent=2, ensure_ascii=False)}\n\n"
        "CANDIDATE PROFILE (use only this — do not add anything not present here):\n"
        f"{json.dumps(profile_context, indent=2, ensure_ascii=False)}"
    )


def parse_response(text: str) -> tuple[str, str]:
    cv_match = re.search(
        rf"{re.escape(CV_DELIMITER)}\s*(.*?)\s*{re.escape(LETTER_DELIMITER)}",
        text, re.DOTALL,
    )
    letter_match = re.search(rf"{re.escape(LETTER_DELIMITER)}\s*(.*)", text, re.DOTALL)
    cv_positioning = cv_match.group(1).strip() if cv_match else ""
    cover_letter = letter_match.group(1).strip() if letter_match else ""
    if not cv_positioning or not cover_letter:
        raise ValueError("Response did not contain both expected sections")
    return cv_positioning, cover_letter


def generate_application(client: anthropic.Anthropic, job: dict, profile_context: dict) -> tuple[str, str]:
    response = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        temperature=0.7,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_message(job, profile_context)}],
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    return parse_response(text)


def main() -> None:
    load_dotenv()

    matches_path = load_latest_matches_file()
    with open(matches_path, encoding="utf-8") as f:
        matches_data = json.load(f)

    with open(PROFILE_PATH, encoding="utf-8") as f:
        profile = json.load(f)
    profile_context = build_profile_context(profile)

    shortlist = select_shortlist(matches_data["matches"])
    print(f"Processing {len(shortlist)} jobs (source: {matches_path.name})\n")

    APPLICATIONS_DIR.mkdir(exist_ok=True)
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env (loaded via .env above)

    results = []
    for i, job in enumerate(shortlist, start=1):
        job_id = job["id"]
        label = f"[{i}/{len(shortlist)}] {job['job_title']} @ {job['company']} (score {job['match_score']})"
        try:
            cv_positioning, cover_letter = generate_application(client, job, profile_context)
        except anthropic.NotFoundError as exc:
            print(f"{label} -> FAILED (model not found: {exc})")
            results.append({"job_id": job_id, "status": "failed", "error": f"model not found: {exc}"})
            continue
        except anthropic.RateLimitError as exc:
            print(f"{label} -> FAILED (rate limited after SDK's built-in retries: {exc})")
            results.append({"job_id": job_id, "status": "failed", "error": f"rate limited: {exc}"})
            continue
        except anthropic.APIStatusError as exc:
            print(f"{label} -> FAILED (API error {exc.status_code}: {exc.message})")
            results.append({"job_id": job_id, "status": "failed", "error": f"API error {exc.status_code}: {exc.message}"})
            continue
        except anthropic.APIConnectionError as exc:
            print(f"{label} -> FAILED (connection error: {exc})")
            results.append({"job_id": job_id, "status": "failed", "error": f"connection error: {exc}"})
            continue
        except ValueError as exc:
            print(f"{label} -> FAILED (malformed response: {exc})")
            results.append({"job_id": job_id, "status": "failed", "error": str(exc)})
            continue

        cv_path = APPLICATIONS_DIR / f"{job_id}_cv_positioning.md"
        letter_path = APPLICATIONS_DIR / f"{job_id}_cover_letter.md"
        cv_path.write_text(
            f"# CV Positioning — {job['job_title']} @ {job['company']}\n\n{cv_positioning}\n",
            encoding="utf-8",
        )
        letter_path.write_text(
            f"# Cover Letter — {job['job_title']} @ {job['company']}\n\n{cover_letter}\n",
            encoding="utf-8",
        )
        print(f"{label} -> ok")
        results.append({
            "job_id": job_id,
            "status": "ok",
            "job_title": job["job_title"],
            "company": job["company"],
            "match_score": job["match_score"],
            "cv_positioning_file": cv_path.name,
            "cover_letter_file": letter_path.name,
        })

    index = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_matches_file": matches_path.name,
        "model": MODEL,
        "score_threshold": SCORE_THRESHOLD,
        "job_count": len(shortlist),
        "succeeded": sum(1 for r in results if r["status"] == "ok"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "results": results,
    }
    index_path = APPLICATIONS_DIR / "index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"\n{index['succeeded']} succeeded, {index['failed']} failed -> {index_path}")


if __name__ == "__main__":
    main()
