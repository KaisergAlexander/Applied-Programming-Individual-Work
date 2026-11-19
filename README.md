# Applied Programming: Individual Work

Individual work for the Applied Programming course (Nova SBE): four projects, of which the job scraper is an optional extra. Each one lives in its own folder with its own README that explains what it does, how to install it and how to run it, and each folder contains an `AUDIT.md` with the publication audit.

## Live demos
| Project | Open it |
|---|---|
| Book Scraper (Streamlit) | [https://applied-programming-individual-work-menlasp42rjxsjiifgiubp.streamlit.app/](https://applied-programming-individual-work-menlasp42rjxsjiifgiubp.streamlit.app/) |
| TV Maze Series Explorer (Streamlit) | [https://applied-programming-individual-work-avatqjzqrccoznpat4hqft.streamlit.app/](https://applied-programming-individual-work-avatqjzqrccoznpat4hqft.streamlit.app/) |

The Chrome extension and the job scraper run locally (see their READMEs).

## Projects
| # | Folder | What it is | Technologies |
|---|---|---|---|
| 1 | [chrome-extension/](chrome-extension/README.md) | **Momentum Dash replica:** new-tab dashboard with clock, greeting, daily focus, to-do list, weather, quote | JavaScript, HTML, CSS, Chrome Manifest V3 |
| 2 | [books/](books/README.md) | **Books to Scrape:** scrapes 100 books, stores them in a Supabase (PostgreSQL) database and shows them in an interactive dashboard | Python, BeautifulSoup, Supabase, Streamlit, pandas |
| 3 | [tv-maze/](tv-maze/README.md) | **TVmaze API:** TV show explorer on top of the free TVmaze REST API: search shows and actors, ratings, cast, episodes, similar shows | Python, requests, Flask, Streamlit |
| extra | [job-scraper/](job-scraper/README.md) | *Optional, not required:* collects job postings (Greenhouse, Lever, Adzuna), scores them against a candidate profile and can draft application documents | Python, REST APIs, Anthropic API |

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

## What I learned
I came into this course able to write code. Most of my earlier university projects stopped at a notebook or a script that worked on my own laptop. What I was missing was everything *around* the code, and these projects closed exactly that gap, step by step.

- **What an API is.** With TVmaze I learned that an API is a list of web addresses that answer with structured data instead of a web page. A *name* gives me an *ID*, and the ID opens every other request. Once I saw this pattern, the weather service, the job APIs and even the database looked like the same idea, and I also learned that requests fail and that handling this is part of the work.
- **What Supabase is and why I use it.** My data used to sit in a JSON file in my own repository, where only I could use it. Supabase gave me a real hosted PostgreSQL database with an API in front of it. I learned about primary keys, upserts, Row Level Security and above all the difference between a read-only publishable key and a secret key that must never be committed.
- **What Streamlit is.** Streamlit turns a Python script into a website without HTML or JavaScript, and it can be deployed straight from a GitHub repository. That was the moment a script became a link that someone else can open.

Put together, the books project is the whole chain in one place: scrape the data, store it in Supabase, present it with Streamlit, deploy it.

## Reflection
At the beginning of the course I was not sure how much I would take away. As a Business Analytics student I already knew a bit more about Claude Code and GitHub than some classmates, and I expected a repeat of the "vibe coding" we did in other university projects. It turned out to be different. This course went beyond the theory and focused on the applied side: how to take something that runs on my machine and **deploy** it as a product with a public link, a database and documentation. For me this was the biggest difference.

My second reflection is how much AI can do today. It can write a large part of the code, so the code itself is no longer the scarce skill. What matters more is knowing how to work with a tool like Claude Code and knowing which solutions exist, for example Streamlit for the interface and Supabase for storage, so that I can put the pieces together and check that the result is correct. In practice, my job was to decide what to build, to test it, to catch problems (such as the app silently using the wrong data source) and to say honestly what is not finished.

## Limitations
Details are in each project's README and `AUDIT.md`. The main points:

- **Data:** only 100 of the 1,000 books were scraped, and the job scraper covers five companies, so it shows the method rather than the market.
- **Cost:** the job scraper can write tailored CV statements and cover letters, but that step costs real money per call. I wrote it and decided not to run it, because I was not willing to spend credits on an experiment I could not fully control. It is untested.
- **Chrome extension:** I stayed close to the original Momentum idea. I am not a fan of this type of product and I did not work out what I would personally want to see on a new tab, so it is the least distinctive of the projects.
- **Automation:** nothing refreshes by itself and there are no automated tests.
- **Next steps I would take (together with Claude's suggestions):** scrape all books and schedule the refresh, add tests, run the job-scraper CV step on three jobs first to measure the real cost, and give the extension a clear concept of my own.

## AI assistance
I used **Claude Code (Anthropic)** in VS Code for all four projects. I defined the goals and decisions, reviewed the results, ran and tested the apps and the extension, and decided how the repository and the deployment are organised. Claude Code wrote most of the code and ran the Git commands under my direction. Besides that I used the official documentation of TVmaze, Supabase, Streamlit, Flask, Open-Meteo, Adzuna, Greenhouse, Lever and Chrome extensions.
