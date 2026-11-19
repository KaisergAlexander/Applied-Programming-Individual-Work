# Audit: TVmaze API

Date: 2026-11-19 · Scope: the `tv-maze/` folder and the repository's Git state · Assistant: Claude Code (Anthropic)

## How the audit was run
I ran the course audit prompt (publication audit for a public GitHub repository) with Claude Code. The audit itself was read-only: it inspected files, Git status, tracked files and Git history, did not print secret values, did not execute project code and did not commit or push. I then reviewed the findings, decided which needed action, fixed them and ran the audit again.

## What was checked
- Secrets and credentials: pattern search in all tracked files and in the full Git history. This project needs no API key.
- Sensitive and generated files: `.env`, `profile.json`, `__pycache__`, `.venv` and `.vscode` (tracked or ignored, checked with `git check-ignore`).
- `.gitignore` rules, `requirements.txt` and setup instructions.
- README against the required sections: purpose, data collection, persistence, user interaction, setup, learning, limitations and assistance.

## Before (first audit)
| # | Finding | Type | Action needed? |
|---|---|---|---|
| 1 | No secrets or credentials in tracked files or Git history. The project uses a public API without a key. | Confirmed (no issue) | No |
| 2 | A local `tv-maze/__pycache__/` folder exists but is ignored and not tracked. | Confirmed (no issue) | No |
| 3 | The README told the reader that "the project's `.vscode/settings.json` already points to `.venv`", but `.vscode/` is ignored, so the file is not in the repository and the instruction would not work after cloning. | Confirmed issue | **Yes** |
| 4 | The README lacked the required sections *Purpose*, *Data collection*, *Data persistence*, *User interaction*, *Learning* and *Limitations and assistance*. | Confirmed issue | **Yes** |
| 5 | No screenshot in the README. | Not applicable | No. The instructor said a screenshot is optional when it is not needed to explain a project; the live demo link and the README explain this one. |

## Fixes made
- Finding 3: removed the sentence about the ignored settings file. The remaining instruction (select the `.venv` interpreter) works without it.
- Finding 4: added all missing sections. *Data persistence* is marked "Not applicable" with the reason (the app reads the live API and stores nothing except a short in-memory cache). Added the AI assistance disclosure.
- Finding 5: no action, screenshots are optional here.

## After (repeat audit)
No secrets, no tracked caches or environments, and `.gitignore` rules work for all checked paths. The README now contains all required sections and no longer references a file that is not in the repository.

## Remaining limitations
- The audit assistant did not run the code, so the setup instructions were checked by reading, not by a fresh install.
- The behaviour depends on the public TVmaze API, which I do not control and which was not audited.
- A pattern search cannot prove that no secret exists.
