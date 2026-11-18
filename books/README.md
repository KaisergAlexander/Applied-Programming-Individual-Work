# Book Scraper

Scrapes book data from [books.toscrape.com](https://books.toscrape.com) (HTML parsing, no API) and stores it in a Supabase PostgreSQL table.

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
