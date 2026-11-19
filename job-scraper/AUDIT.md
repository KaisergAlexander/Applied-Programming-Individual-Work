# Audit: Job Scraper (optional extra project)

Date: 2026-11-19 · Scope: the `job-scraper/` folder and the repository's Git state · Assistant: Claude Code (Anthropic)

## How the audit was run
I ran the course audit prompt (publication audit for a public GitHub repository) with Claude Code. The audit itself was read-only: it inspected files, Git status, tracked files and Git history, did not print secret values, did not execute project code and did not commit or push. I then reviewed the findings, decided which needed action, fixed them and ran the audit again.

## What was checked
- Secrets and credentials: pattern search (Adzuna and Anthropic keys, tokens, `key = "..."` assignments) in all tracked files and in the full Git history.
- Personal and sensitive data: the candidate profile, names and email addresses in files and documentation.
- Generated output: `data/` and `applications/` (tracked or ignored).
- `.gitignore` rules, `requirements.txt`, `.env.example` and `profile.example.json`.
- README against the required sections: purpose, data collection, persistence, user interaction, setup, learning, limitations and assistance.

## Before (first audit)
| # | Finding | Type | Action needed? |
|---|---|---|---|
| 1 | No secrets or credentials in tracked files or Git history. `.env` and `profile.json` are ignored and were never tracked. | Confirmed (no issue) | No |
| 2 | `profile.example.json` is a fictional profile (Jane Example, example.com email, placeholder address and phone). | Confirmed (no issue) | No |
| 3 | `PROGRESS.md` and a comment in `match_engine.py` named a real person (a first name) who is not the author. A third party's name does not belong in a public repository. | Confirmed issue | **Yes** |
| 4 | The README lacked the required sections *Purpose*, *Data collection*, *Data persistence*, *User interaction*, *Learning* and *Limitations and assistance*. | Confirmed issue | **Yes** |
| 5 | `PROGRESS.md` reports 911 collected jobs (a run on 2026-09-14), while the README quick start says about 700. Job counts change from run to run. | Possible concern (inconsistency) | No change, it is a dated progress log |
| 6 | The step 3 generator (`application_generator.py`) was never run, so it is untested. | Confirmed limitation | Disclosed, not fixable without paid API calls |
| 7 | No screenshot in the README. | Not applicable | No. The instructor said a screenshot is optional when it is not needed to explain a project; the README explains this one. |

## Fixes made
- Finding 3: replaced the name with "one finance/strategy profile" in `PROGRESS.md` and in the comment in `match_engine.py`. The code behaviour is unchanged (comment only). The name was also present in earlier commits, so I rewrote the Git history to replace it in every commit. A backup of the old history was kept outside the repository until the push was checked.
- Finding 4: added all missing sections. The project is marked as an optional extra. Step 3 is described honestly as written but not run, with the reason (cost).
- Finding 6: documented in the README under "Limitations and assistance".
- Finding 7: no action, screenshots are optional here.

## After (repeat audit)
No secrets, no third-party names and no tracked generated output were found. The README now contains all required sections.

## Remaining limitations
- Step 3 is untested and step 4 does not exist.
- The audit assistant did not run the scraper, so the setup instructions were checked by reading, not by a fresh install.
- Names of companies and job postings come from public job boards and were not reviewed individually.
- A pattern search cannot prove that no secret or personal detail exists. Git history was searched for key patterns only.
