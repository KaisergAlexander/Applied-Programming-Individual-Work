# Applied Programming: Individual Work

Four small projects for the Applied Programming course. Each one lives in its own folder with its own README that explains what it does, how to install it and how to run it.

## Live demos
| Project | Open it |
|---|---|
| Book Scraper (Streamlit) | [https://applied-programming-individual-work-menlasp42rjxsjiifgiubp.streamlit.app/](https://applied-programming-individual-work-menlasp42rjxsjiifgiubp.streamlit.app/) |
| TV Maze Series Explorer (Streamlit) | [https://applied-programming-individual-work-avatqjzqrccoznpat4hqft.streamlit.app/](https://applied-programming-individual-work-avatqjzqrccoznpat4hqft.streamlit.app/) |

The Chrome extension and the job scraper run locally (see their READMEs).

## Projects
| Folder | What it is | Technologies |
|---|---|---|
| [books/](books/README.md) | Scrapes 100 books from books.toscrape.com, stores them in a Supabase (PostgreSQL) database and shows them in an interactive dashboard | Python, BeautifulSoup, Supabase, Streamlit, pandas |
| [tv-maze/](tv-maze/README.md) | TV show explorer on top of the free TVmaze REST API: search shows and actors, ratings, cast, episodes, similar shows | Python, requests, Flask, Streamlit |
| [job-scraper/](job-scraper/README.md) | Pipeline that collects job postings (Greenhouse, Lever, Adzuna), scores them against a candidate profile and drafts application documents | Python, REST APIs, Anthropic API |
| [chrome-extension/](chrome-extension/README.md) | Momentum-style new-tab dashboard: clock, greeting, daily focus, to-do list, weather, quote | JavaScript, HTML, CSS, Chrome Manifest V3 |

## Quick start
Each project is independent. Open its folder and follow its README. In short:

```bash
# Books dashboard
cd books
pip install -r requirements.txt
streamlit run app.py              # works without any keys (uses the included books.json)

# TV Maze explorer
cd tv-maze
pip install -r requirements.txt
streamlit run streamlit_app.py    # or: python app.py for the Flask version

# Job scraper (works without any key; an optional free Adzuna key adds more jobs)
cd job-scraper
pip install -r requirements.txt
python main.py                    # step 1: collects ~700 jobs
python match_engine.py            # step 2: scores and ranks them

# Chrome extension: chrome://extensions -> Developer mode -> Load unpacked -> select chrome-extension/
```

## Secrets and personal data
No API keys or personal data are stored in this repository. Each project has a `.env.example` (or a `profile.example.json`) that shows what you would have to provide yourself. The real files (`.env`, `profile.json`) are listed in `.gitignore`.
