# Audit: Books to Scrape

Date: 2026-11-19 · Scope: the `books/` folder and the repository's Git state · Assistant: Claude Code (Anthropic)

## How the audit was run
I ran the course audit prompt (publication audit for a public GitHub repository) with Claude Code. The audit itself was read-only: it inspected files, Git status, tracked files and Git history, did not print secret values, did not execute project code and did not commit or push. I then reviewed the findings, decided which needed action, fixed them and ran the audit again.

## What was checked
- Secrets and credentials: pattern search (Supabase secret/publishable keys, JWT-like tokens, Anthropic keys, `key = "..."` assignments) in all tracked files and in the full Git history.
- Sensitive files: whether `.env`, `.streamlit/secrets.toml`, `profile.json`, caches, virtual environments and editor settings are tracked or ignored.
- `.gitignore` rules, checked with `git check-ignore` for each of these paths.
- Dependencies (`requirements.txt`), configuration example (`.env.example`) and database setup (`schema.sql`).
- README against the required sections: purpose, data collection, persistence, user interaction, setup, learning, limitations and assistance.

## Before (first audit)
| # | Finding | Type | Action needed? |
|---|---|---|---|
| 1 | No secrets or credentials in tracked files or in Git history. | Confirmed (no issue) | No |
| 2 | `.env` (holds the real Supabase keys) exists locally but is ignored and not tracked. `.env.example` contains placeholders only. | Confirmed (no issue) | No |
| 3 | The README lacked the required sections *Data persistence*, *User interaction*, *Learning* and *Limitations and assistance*. | Confirmed issue | **Yes** |
| 4 | No screenshot in the README. | Not applicable | No. The instructor said a screenshot is optional when it is not needed to explain a project; the live demo link and the README explain this one. |
| 5 | The commit author email in Git history was my university email address. | Possible concern | **Yes** (my decision) |

## Fixes made
- Finding 3: added the missing sections (Purpose, Data collection, Data persistence, User interaction, Setup, Learning, Limitations and assistance), including the AI assistance disclosure.
- Finding 4: no action, screenshots are optional here.
- Finding 5: rewrote the Git history so that every commit uses my GitHub noreply address instead of my university email. A backup of the old history was kept outside the repository until the push was checked.

## After (repeat audit)
Findings 1 and 2 were confirmed again (no secrets in tracked files or history; `.env`, caches, `.venv` and `.vscode` are ignored). The README now contains all required sections. Nothing else was found.

## Remaining limitations
- A pattern search cannot prove that no secret exists. I did not read the contents of `.env`, and I did not verify the Supabase project settings (Row Level Security was checked only through `schema.sql`, not in the live project).
- The deployed Streamlit app and its hosting settings were not part of the repository audit.
- The audit assistant did not run the code, so setup instructions were checked by reading, not by a fresh install.
