# Audit: Momentum Dash replica (Chrome extension)

Date: 2026-11-19 · Scope: the `chrome-extension/` folder and the repository's Git state · Assistant: Claude Code (Anthropic)

## How the audit was run
I ran the course audit prompt (publication audit for a public GitHub repository) with Claude Code. The audit itself was read-only: it inspected files, Git status, tracked files and Git history, did not print secret values, did not execute project code and did not commit or push. I then reviewed the findings, decided which needed action, fixed them and ran the audit again.

## What was checked
- Secrets and credentials: pattern search in all tracked files and in the full Git history. The extension uses no API key (Open-Meteo and picsum.photos are used without one).
- Personal data: names, email addresses and similar details in the code and the README.
- Sensitive and generated files: `.env`, caches, `.venv`, `.vscode` (tracked or ignored).
- `manifest.json` permissions: only `storage` and `geolocation`, and host access to `api.open-meteo.com` only.
- Setup instructions (manual installation in Chrome developer mode).
- README against the required sections: purpose, data collection, persistence, user interaction, setup, learning, limitations and assistance.

## Before (first audit)
| # | Finding | Type | Action needed? |
|---|---|---|---|
| 1 | No secrets, credentials or personal data in the folder or in Git history. The only email-like strings in the repository are the placeholders in other projects. | Confirmed (no issue) | No |
| 2 | Permissions are minimal and match what the code does. | Confirmed (no issue) | No |
| 3 | The README lacked the required sections *Purpose*, *Data collection*, *Data persistence*, *User interaction*, *Learning* and *Limitations and assistance*. | Confirmed issue | **Yes** |
| 4 | No screenshot in the README. | Not applicable | No. The instructor said a screenshot is optional when it is not needed to explain a project; the README describes every feature. |
| 5 | The extension sends the browser's coordinates to Open-Meteo and requests a background image from picsum.photos, which reveals the IP address to these services. The README already states the coordinates part. | Possible concern | Documented, no code change |
| 6 | `quotes.js` bundles quotes without a stated source. | Possible concern | No change (short list of well-known quotes, no code or private data) |

## Fixes made
- Finding 3: added all missing sections and the AI assistance disclosure.
- Finding 4: no action, screenshots are optional here.
- Finding 5: accepted. The location permission is optional and the weather widget hides without it.

## After (repeat audit)
No secrets, no personal data and no tracked generated files were found. The README now contains all required sections.

## Remaining limitations
- The audit assistant did not load the extension in Chrome, so the installation steps were checked by reading, not by running them in this audit.
- A pattern search cannot prove that no secret exists.
