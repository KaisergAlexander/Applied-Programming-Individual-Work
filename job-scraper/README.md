# Job Scraper Application Tool

A command-line pipeline that collects job postings from public job APIs, scores them against a candidate profile and (optionally) drafts a tailored CV statement and cover letter for the best matches with the Anthropic API.

> **Optional extra.** This project is not one of the three required projects. I added it because I enjoyed the idea and my instructor said it was welcome.

**Workflow:** 1. Collect data → 2. Match engine → 3. Application documents → 4. Job preparation (not started)

## Purpose
Looking for a job means reading hundreds of postings. This tool collects them from public job APIs, scores each one against a candidate profile with a transparent rule-based score, and can (optionally) draft application documents for the best matches.

## Data persistence
Each run writes plain JSON files: `data/jobs_<timestamp>.json` (all postings in one common format) and `data/matches_<timestamp>.json` (scored postings). JSON files are enough here because the data is a snapshot that is read by the next script, and they can be opened and checked by hand. They are generated output, so they are listed in `.gitignore` and not in the repository. The personal candidate profile (`profile.json`) is gitignored too; the repository contains only a fictional `profile.example.json`.

## User interaction
It is a command-line tool: run `python main.py`, then `python match_engine.py`, which prints the ranked jobs with the reason for each score.

## Setup
See "Installation", "Configuration" and "Usage" below. No key is required for steps 1 and 2.

## What each step does
| Step | File | Result | Status |
|---|---|---|---|
| 1. Data collection | `main.py` (+ `fetchers/`, `normalizer.py`, `config.py`) | `data/jobs_<timestamp>.json`: all postings in one common format | Done |
| 2. Match engine | `match_engine.py` | `data/matches_<timestamp>.json`: jobs scored 0-100 with a human-readable reason | Done |
| 3. Applications | `application_generator.py` | `applications/<job_id>_cv_positioning.md` and `..._cover_letter.md` for jobs with score ≥ 70 | Written, needs an Anthropic API key (paid) |
| 4. Job preparation | – | – | Not started |

Details and design decisions are in [PROGRESS.md](PROGRESS.md) and [step1-data-collection-context.md](step1-data-collection-context.md).

## Data collection
Data comes from the sources below and is collected by `main.py` with the fetchers in `fetchers/`.

- **Greenhouse** and **Lever**: public job-board APIs of selected companies (N26, Celonis, GetYourGuide, HelloFresh, Farfetch). No key needed.
- **Adzuna**: keyword and country search (finance / strategy, Germany). Optional: needs a free API key, without it this source is skipped and the other two still work.

Companies and search terms are set in `config.py`.

## How the match score works
A transparent, rule-based score from 0 to 100 (no model). Weights are constants at the top of `match_engine.py`: title relevance 35, location 20, work mode 15, employment type 10, experience fit 15, language 5. Each job gets a text reason explaining its score.

## Installation
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```

## Configuration
1. Optional: copy `.env.example` to `.env` and fill in your keys (never commit `.env`). Without keys, steps 1 and 2 still run with Greenhouse and Lever data:
   ```env
   ADZUNA_APP_ID=your_id
   ADZUNA_API_KEY=your_key
   ANTHROPIC_API_KEY=your_key      # only needed for step 3
   ```
   Adzuna keys are free at <https://developer.adzuna.com/>.
2. **Candidate profile:** copy `profile.example.json` to `profile.json` and fill in your own data. `profile.json` is gitignored because it contains personal data. If it does not exist, the scripts use the fictional `profile.example.json`, so everything still runs.

## Usage
```bash
python main.py                    # step 1: collect jobs      -> data/jobs_*.json
python match_engine.py            # step 2: score and rank    -> data/matches_*.json
python application_generator.py   # step 3: needs ANTHROPIC_API_KEY, makes paid API calls
```
Step 2 prints the ranked jobs, for example `[ 80] Senior Manager ... — HelloFresh (Berlin)`.

## Project structure
```
main.py                   step 1 entry point
fetchers/                 one fetcher per source (Greenhouse, Lever, Adzuna)
normalizer.py             converts every source into one common job format
config.py                 companies, countries, keywords
match_engine.py           step 2: scoring
application_generator.py  step 3: CV statement + cover letter via Anthropic API
profile.example.json      fictional candidate profile (template)
data/, applications/      generated output (gitignored)
```

## Known limitations
- Adzuna has no Portugal endpoint, so Portugal is covered via the Farfetch Lever board.
- The title keywords in the match engine are tuned for a finance/strategy profile and are not yet derived from the profile.
- Step 3 only runs with your own API key and costs a few cents per run. It is instructed not to invent experience that is not in the profile.

## Learning
I learned that different services expose very different APIs: Greenhouse and Lever publish one clean JSON feed per company, while Adzuna needs a key and offers search. The real work is the **normalizer**, which converts all sources into one common format so the rest of the code does not care where a job came from. I also learned to prefer a transparent score over a black box: every score comes with a written reason that I can check and explain.

**A challenge:** Adzuna does not support Portugal. Instead of dropping that market, I covered it through a company that hires there and uses Lever (Farfetch), and I documented the gap.

## Limitations and assistance
- **Step 3 was not run.** Writing a tailored CV statement and cover letter for each match needs paid calls to the Anthropic API. The estimated cost for the 28-job shortlist was small, but I was not willing to spend credits on an experiment whose output I could not fully control, so the generator is written but untested. Step 4 (job preparation) was not started.
- **Small coverage:** five companies plus one Adzuna search. It finds a few hundred jobs, not the market.
- **Scoring is tuned for one profile type** (finance and strategy keywords are hardcoded).
- **Next steps I would take:** derive the keywords from the profile, run step 3 on three jobs first to measure the real cost, and add more companies.
- **AI assistance:** built with Claude Code (Anthropic). I defined the workflow and checked the results (a full run of steps 1 and 2 found and scored the postings); Claude Code wrote most of the code. Sources used: the Greenhouse, Lever and Adzuna API documentation.
