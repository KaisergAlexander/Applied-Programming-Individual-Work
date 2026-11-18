# Job Scraper Application Tool

A command-line pipeline that collects job postings from public job APIs, scores them against a candidate profile and (optionally) drafts a tailored CV statement and cover letter for the best matches with the Anthropic API.

**Workflow:** 1. Collect data → 2. Match engine → 3. Application documents → 4. Job preparation (not started)

## What each step does
| Step | File | Result | Status |
|---|---|---|---|
| 1. Data collection | `main.py` (+ `fetchers/`, `normalizer.py`, `config.py`) | `data/jobs_<timestamp>.json`: all postings in one common format | Done |
| 2. Match engine | `match_engine.py` | `data/matches_<timestamp>.json`: jobs scored 0-100 with a human-readable reason | Done |
| 3. Applications | `application_generator.py` | `applications/<job_id>_cv_positioning.md` and `..._cover_letter.md` for jobs with score ≥ 70 | Written, needs an Anthropic API key (paid) |
| 4. Job preparation | – | – | Not started |

Details and design decisions are in [PROGRESS.md](PROGRESS.md) and [step1-data-collection-context.md](step1-data-collection-context.md).

## Data sources
- **Greenhouse** and **Lever**: public job-board APIs of selected companies (N26, Celonis, GetYourGuide, HelloFresh, Farfetch). No key needed.
- **Adzuna**: keyword and country search (finance / strategy, Germany). Free API key needed.

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
1. Copy `.env.example` to `.env` and fill in your keys (never commit `.env`):
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
