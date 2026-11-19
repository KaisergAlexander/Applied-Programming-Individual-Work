# TV Maze Series Application

A TV show discovery website built with Flask and the free [TVmaze API](https://www.tvmaze.com/api). Search for shows or actors and see ratings, cast, episodes by season and similar shows, in a modern dark interface. It also teaches how REST APIs work: every feature below is built from real API responses.

> **Live demo:** [https://applied-programming-individual-work-avatqjzqrccoznpat4hqft.streamlit.app/](https://applied-programming-individual-work-avatqjzqrccoznpat4hqft.streamlit.app/) (Streamlit version, `streamlit_app.py`).

## Purpose
A website that connects to the free TVmaze API and turns its raw responses into something a person can use: search a show or an actor, see ratings, cast, episodes and similar shows. The goal was to understand how a program talks to an API, so every feature is built directly from API responses.

## Data collection
All data comes live from the public [TVmaze REST API](https://www.tvmaze.com/api) (`https://api.tvmaze.com`). No account and no API key are needed. [tvmaze.py](tvmaze.py) sends the requests with `requests`, checks the status code, handles timeouts and missing fields, and returns clean Python data. The endpoints and how their IDs connect are described under "API endpoints used" below.

## Data persistence
**Not applicable (no database).** The app stores nothing, because TVmaze already is the database and its data changes all the time. Saving a copy would make it outdated and add work without benefit. The only storage is a short-lived in-memory cache (`functools.lru_cache`) that avoids asking the API for the same page twice while the app runs.

## User interaction
Open the live demo (or run the app locally). Type a show name in the search bar, or switch to "Actors" to search a person. Click a poster to open the show page with description, rating, cast, episodes grouped by season and "You Might Also Like". Click an actor to see their other shows.

## Setup
See "Installation and execution" below. No configuration or keys are needed.

## Two versions
- `streamlit_app.py`: Streamlit version, can be hosted online (live demo above).
- `app.py` + `templates/` + `static/`: the original Flask version, runs locally.

Both use the same API module `tvmaze.py`.

## Features

- **Dark, responsive UI** (IMDb/Netflix style): sticky navigation with search bar, poster cards with hover effects, works on phones.
- **Home page** with the top rated shows.
- **Show search**: results as poster cards with rating and year.
- **Show page**: poster, genres, status, runtime, network, description.
- **Ratings**: the TVmaze rating (`rating.average`) is shown prominently. TVmaze does not provide IMDb scores, only IMDb IDs, so the page shows a link to the show's IMDb page when an ID exists. Missing ratings show "Not available". No scraping, no other rating source, no API keys.
- **Cast**: main cast with actor photo, name and character. Each actor is clickable.
- **Actor pages**: an actor's other TV shows (newest first), each clickable.
- **Actor search**: choose "Actors" in the search bar to find actors and see their TV credits.
- **Episodes**: grouped by season in collapsible sections (`<details>`), with episode number, title and air date. Specials are labelled "Special".
- **You Might Also Like**: shows that share genres with the current show, with posters and ratings (see below).
- **Error handling**: empty search, nothing found, unknown show/person (404 page), connection errors, timeouts, HTTP errors, missing images (placeholder), missing ratings, missing cast. If cast or recommendations fail, the rest of the page still loads.
- **Terminal version** (`main.py`) that still prints episodes by season.

## Technologies

Python 3, [Flask](https://flask.palletsprojects.com/), [requests](https://requests.readthedocs.io/), HTML (Jinja2 templates), CSS. No JavaScript is needed. No database. Responses are cached in memory with `functools.lru_cache` to avoid repeated calls.

## Project structure

| File | Purpose |
|---|---|
| `tvmaze.py` | All TVmaze API logic and error handling (shared by web and terminal) |
| `streamlit_app.py` | Streamlit version of the interface (search, show page, cast, episodes, recommendations, actor pages) |
| `app.py` | Flask routes: `/`, `/search`, `/show/<id>`, `/person/<id>` |
| `templates/` | `base.html` (layout), `_macros.html` (cards), `home.html`, `search.html`, `show.html`, `person.html`, `error.html` |
| `static/style.css` | Dark theme and responsive layout |
| `main.py` | Terminal version |
| `requirements.txt` | Dependencies: `requests`, `flask`, `streamlit` |

## API endpoints used

Base URL: `https://api.tvmaze.com`

| Endpoint | Why we need it |
|---|---|
| `GET /search/shows?q=<name>` | Turns a name typed by a human into a list of matching shows, each with a unique numeric `id`. |
| `GET /shows/<id>` | Full details of one show: poster, genres, `rating.average`, status, summary and `externals.imdb` (the IMDb ID used for the IMDb link). |
| `GET /shows/<id>/episodes` | Every episode of one show (season, number, title, air date). |
| `GET /shows/<id>/cast` | The actors of a show and the characters they play, including each actor's `person.id`. |
| `GET /search/people?q=<name>` | Turns an actor name into a list of matching people, each with a unique `id`. |
| `GET /people/<id>` | Details of one person (photo, birthday, country). |
| `GET /people/<id>/castcredits?embed=show` | The shows a person acted in. `embed=show` includes the full show data (poster, rating) in the same response, so no extra request per show is needed. |
| `GET /shows?page=<n>` | One page of 250 shows from the TVmaze index (genres and rating included). Used for the home page and for recommendations. |

### How IDs connect the requests

The endpoints cannot take names, only IDs, so one request provides the ID for the next one.

**Show ID**
1. `/search/shows?q=The Big Bang Theory` returns the show with `id` 66.
2. The app uses 66 in `/shows/66` (details), `/shows/66/episodes` (episodes) and `/shows/66/cast` (cast). The page URL is `/show/66` as well, so every show page is addressable by its ID.

**Person ID**
1. `/shows/66/cast` (or `/search/people?q=...`) returns each actor with a `person.id`, e.g. 4 for Johnny Galecki.
2. The app uses it in `/people/4` and `/people/4/castcredits?embed=show` to list the actor's other shows.
3. Each of those shows has its own `id`, which leads back to a show page. Shows and people link into each other this way.

### How "You Might Also Like" works

TVmaze has no "similar shows" endpoint, so recommendations are based on **genre similarity**:

1. Read the `genres` of the current show (from `/shows/<id>`).
2. Download one index page, `/shows?page=<id // 250>`, which is the page of 250 shows containing the current show. The whole catalogue (tens of thousands of shows) is never downloaded.
3. Keep the shows that share at least one genre, excluding the current show itself.
4. Rank them by number of shared genres, then by TVmaze rating, and show the best 6. The shared genres are shown on each card.

Because only one page is used, recommendations come from shows with nearby IDs (roughly the same period of TVmaze's catalogue). This is a deliberate trade-off for speed.

## Installation and execution

**Streamlit version:**
```powershell
pip install -r requirements.txt
streamlit run streamlit_app.py
```
Opens at <http://localhost:8501>.

**Flask version:**

Requires Python 3. From the project folder (Windows PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open <http://localhost:5000> in your browser. Stop the server with `Ctrl+C`.

Terminal version: `python main.py`

### VS Code: "Import requests could not be resolved"

VS Code is using a different Python than the one with the packages. Press `Ctrl+Shift+P` -> **Python: Select Interpreter** -> choose `.\.venv\Scripts\python.exe`, then run **Developer: Reload Window** if needed.
## Development Progress

| Version | What was added |
|---|---|
| v0.1 | Terminal app: `/search/shows` and `/shows/{id}/episodes`, season grouping, error handling. |
| v0.2 | Fixed the VS Code `requests` import warning (project `.venv`). Moved API logic into `tvmaze.py`. First Flask web interface at `localhost:5000`. |
| v0.3 | Modern dark UI with posters and responsive cards. Show details and ratings (TVmaze rating, IMDb link). Cast with actor photos and clickable actors. Actor pages and actor search (`/search/people`, `/people/{id}/castcredits`). Collapsible episodes per season. "You Might Also Like" recommendations by genre. Removed API explanations from the website (documented here instead). Response caching. |

> Maintenance rule: update this README (features, endpoints, progress table) whenever functionality is added.

## Learning
I learned what an **API** really is: a list of web addresses that answer with structured data (JSON) instead of a web page. I also learned the pattern behind almost every API: a request with a *name* returns an *ID*, and the ID is the key to every other request (details, cast, episodes, person, credits). Once I understood that chain, the other APIs in this course looked the same. I also learned that APIs fail in normal operation, with timeouts, 404 errors and missing fields such as a show without a rating or an image, and that handling this is part of the work rather than an extra.

**A challenge:** I wanted a "similar shows" feature, but TVmaze has no endpoint for it. I solved it by comparing genres: I read the genres of the current show, download one index page of 250 shows and rank those that share genres, using the rating as tie-breaker. Downloading the whole catalogue would have been too slow, so I accepted a smaller, faster answer.

## Limitations and assistance
- **Recommendations are approximate:** they only look at one page of 250 shows near the current show's ID, so they come from roughly the same period of the catalogue.
- **No IMDb rating:** TVmaze provides only its own rating and the IMDb ID. The app links to IMDb instead of showing a score.
- **No persistence:** every visit calls the live API. If TVmaze is down, the app shows an error message.
- **Two interfaces:** the Flask version runs locally only; the Streamlit version is the one hosted online.
- **AI assistance:** I built this with Claude Code (Anthropic) in VS Code. I defined the features, reviewed and tested them; Claude Code wrote most of the code. Sources used: the official TVmaze API documentation and the Flask and Streamlit documentation.
