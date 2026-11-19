# Book Scraper

Scrapes book data from [books.toscrape.com](https://books.toscrape.com) (HTML parsing, no API), stores it in a Supabase PostgreSQL table and presents it in a Streamlit dashboard.

## Purpose
This project covers the full path of a small data product: **collect** data from a website, **store** it in a cloud database and **present** it in an interface that anyone can open with a link. The source is a practice shop built for scraping, so nothing here touches real customers or real shops.

## Data collection
Books to Scrape has no API, so [scraper.py](scraper.py) downloads the catalogue pages with `requests` and reads the HTML with BeautifulSoup. For each book it collects title, category, prices (with and without tax), stock, star rating, number of reviews, description, cover image URL, product URL and the UPC (a unique product code). It waits one second between requests, skips pages that fail and stops at `--limit`. The included dataset holds **100 books** (the site has 1,000).

## Data persistence
- **`data/books.json`**: the raw result of the scraper. It is a backup and the offline fallback of the app.
- **Supabase (PostgreSQL), table `public.books`**: [load_to_supabase.py](load_to_supabase.py) *upserts* the books with the UPC as primary key, so running it again updates rows instead of creating duplicates. [schema.sql](schema.sql) creates the table.
- **Why a database:** a JSON file only lives on my laptop. With a hosted database the deployed Streamlit app can read the same data from anywhere, and the data can be filtered and queried with SQL.
- **Access control:** Row Level Security makes the table public read-only. Writing needs the secret key, which stays in `.env` and is never committed.

## User interaction
Open the live demo (or run `streamlit run app.py`). Filter by title, category, minimum rating, price range and "in stock only"; read the four key figures (number of books, categories, average price, average rating) and two charts (books per category, rating distribution); browse the table and open a detail view with cover and description. The top of the page states which data source is in use (Supabase or local file).

## Setup
Everything needed to run the project is below: Installation, Environment variables, Supabase SQL setup, then the scraper, loader and Streamlit commands. Without any keys the app runs on the included `data/books.json`.

## Technologies
Python 3, requests, BeautifulSoup4, python-dotenv, supabase-py, Supabase (PostgreSQL), Streamlit, pandas, Git/GitHub.

> **Live demo:** [https://applied-programming-individual-work-menlasp42rjxsjiifgiubp.streamlit.app/](https://applied-programming-individual-work-menlasp42rjxsjiifgiubp.streamlit.app/) (Streamlit app, `app.py`).

## Streamlit app (quick start)
Browse the scraped books in an interactive dashboard (filters by title, category, rating, price and stock; charts; book detail view with cover and description):
```bash
pip install -r requirements.txt
streamlit run app.py
```
The app opens at http://localhost:8501. It reads from Supabase if `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` are set in `.env` (read-only via RLS). Without them it automatically falls back to the included `data/books.json`, so it works right after cloning with no setup. The data source in use is shown at the top of the page.

## Installation
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```

## Environment variables
Copy `.env.example` to `.env` and fill in your values (never commit `.env`):
```env
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SECRET_KEY=YOUR_SECRET_KEY
SUPABASE_PUBLISHABLE_KEY=YOUR_PUBLISHABLE_KEY   # optional, only used by the Streamlit app
```
`SUPABASE_SERVICE_ROLE_KEY` is accepted as a fallback for legacy projects. Find keys in Supabase → Project Settings → API Keys.

## Supabase SQL setup
Open the Supabase SQL Editor and run `schema.sql`. It creates `public.books`, a category index, Row Level Security (public read-only) and grants. It is safe to run repeatedly.

## Scraper usage
```bash
python scraper.py --limit 10 --delay 1 --out data/books.json
```
Options: `--limit` (max books), `--delay` (seconds between requests), `--out` (JSON file).
Validate output: `python validate.py data/books.json 10`

## Database loader usage
```bash
python load_to_supabase.py --test                    # connection test (temporary record)
python load_to_supabase.py --file data/books.json    # upsert books
```

## Verify stored data
In the Supabase SQL Editor:
```sql
select count(*) from public.books;
select upc, title, price_gbp, rating from public.books limit 5;
```

## Troubleshooting
- **Missing SUPABASE_URL / key**: check your `.env` file exists and is filled in.
- **`relation "public.books" does not exist`**: run `schema.sql`.
- **Permission denied / RLS error**: use the secret/service-role key, not the publishable key.
- **Streamlit shows "local" instead of Supabase**: set `SUPABASE_PUBLISHABLE_KEY` in `.env` (the publishable key, never the secret key).
- **Timeouts / HTTP errors when scraping**: increase `--delay`; failed pages are skipped.

## Learning
Before this project my data lived in a JSON file inside my own repository, which only I could use. Here I learned what a **database service** adds. Supabase is a hosted PostgreSQL database with an API in front of it. I learned to design a table with a primary key, to write data with an upsert, and to protect it with Row Level Security. The most important lesson was the **two kinds of keys**: a publishable key that may only read, and a secret key that can write and must never reach Git. I learned **Streamlit** as the way to turn a Python script into a website without writing HTML or JavaScript, and how it is deployed from a GitHub repository.

**A challenge:** after I added the read-only key, the app ran without errors but still showed "local file" as its source. Nothing had crashed; it had silently used the fallback. I found the cause by checking which source the app really used, and fixed the key setup. This is why the app now states its data source at the top of the page.

## Limitations and assistance
- **Small dataset:** 100 of the 1,000 books on the site. The scraper can walk all pages; I stopped at 100 because it was enough to show the whole pipeline.
- **No automatic refresh:** the scraper and the loader are run by hand. The data never changes because the source is a static practice site.
- **No tests** beyond a small output check (`validate.py`).
- **Next steps I would take:** scrape all 1,000 books, schedule the refresh, and add price history in a second table.
- **AI assistance:** I built this with Claude Code (Anthropic) in VS Code. I defined the goal, reviewed the results and tested the live app; Claude Code wrote most of the code and the SQL. Sources used: the Supabase and Streamlit documentation and the Books to Scrape practice site.
