"""Streamlit version of the TV Maze Series Application.

Reuses all API logic from tvmaze.py (the same module the Flask app uses).
Run: streamlit run streamlit_app.py
"""
import streamlit as st

import tvmaze
from tvmaze import TVmazeError

st.set_page_config(page_title="TV Maze Series Explorer", page_icon="📺", layout="wide")

PLACEHOLDER = "https://placehold.co/210x295?text=No+image"


# ---------- Navigation (kept in session_state) ----------
def go(*page):
    st.session_state.page = page


def current_page():
    return st.session_state.get("page", ("home",))


# ---------- Cached API wrappers (tvmaze.py already caches, this also skips reruns) ----------
@st.cache_data(ttl=3600, show_spinner=False)
def cached(fn_name, *args):
    return getattr(tvmaze, fn_name)(*args)


def image_of(item, key="medium"):
    return (item.get("image") or {}).get(key) or PLACEHOLDER


def rating_of(show):
    value = (show.get("rating") or {}).get("average")
    return f"⭐ {value}" if value else "Not rated"


def show_grid(shows, prefix, per_row=6):
    """Poster cards; the button under each poster opens the show page."""
    for start in range(0, len(shows), per_row):
        cols = st.columns(per_row)
        for col, show in zip(cols, shows[start:start + per_row]):
            with col:
                st.image(image_of(show), width="stretch")
                year = (show.get("premiered") or "")[:4]
                st.button(show["name"], key=f"{prefix}-{show['id']}", on_click=go,
                          args=("show", show["id"]), width="stretch")
                extra = f" · shares {', '.join(show['shared_genres'])}" if show.get("shared_genres") else ""
                st.caption(f"{rating_of(show)} · {year}{extra}")


# ---------- Header with search ----------
st.title("📺 TV Maze Series Explorer")
with st.form("search", clear_on_submit=False):
    c1, c2, c3 = st.columns([5, 2, 1])
    query = c1.text_input("Search", placeholder="e.g. Breaking Bad or Bryan Cranston",
                          label_visibility="collapsed")
    kind = c2.radio("Search for", ["Shows", "Actors"], horizontal=True, label_visibility="collapsed")
    submitted = c3.form_submit_button("Search", width="stretch")
if submitted:
    if query.strip():
        go("search", query.strip(), kind)
    else:
        st.warning("Please enter a name to search for.")
st.button("🏠 Home", on_click=go, args=("home",))

page = current_page()

try:
    # ---------- Home ----------
    if page[0] == "home":
        st.subheader("Top rated shows")
        show_grid(cached("get_top_rated"), "home")

    # ---------- Search ----------
    elif page[0] == "search":
        _, q, kind = page
        st.subheader(f"{kind} matching “{q}”")
        if kind == "Shows":
            results = cached("search_shows", q)
            if not results:
                st.info("Nothing found. Try another name.")
            show_grid(results, "search")
        else:
            people = cached("search_people", q)[:12]
            if not people:
                st.info("Nothing found. Try another name.")
            for person in people:
                col_img, col_txt = st.columns([1, 6])
                col_img.image(image_of(person), width=90)
                col_txt.markdown(f"**{person['name']}**")
                col_txt.button("Open profile", key=f"p-{person['id']}", on_click=go,
                               args=("person", person["id"]))

    # ---------- Show detail ----------
    elif page[0] == "show":
        show_id = page[1]
        show = cached("get_show", show_id)
        episodes = cached("get_episodes", show_id)
        left, right = st.columns([1, 3])
        left.image(image_of(show, "original"), width="stretch")
        right.header(show["name"])
        right.write(f"{rating_of(show)} · {', '.join(show.get('genres') or ['–'])} · "
                    f"{show.get('status', '–')} · {show.get('runtime') or '?'} min · "
                    f"premiered {show.get('premiered') or '–'}")
        network = (show.get("network") or show.get("webChannel") or {}).get("name")
        if network:
            right.write(f"Network: {network}")
        right.write(tvmaze.strip_html(show.get("summary")) or "No description available.")
        imdb = (show.get("externals") or {}).get("imdb")
        if imdb:
            right.link_button("View on IMDb", f"https://www.imdb.com/title/{imdb}/")

        st.subheader("Cast")
        try:
            cast = cached("get_cast", show_id)
        except TVmazeError:
            cast = []
        if cast:
            cols = st.columns(6)
            for i, entry in enumerate(cast):
                with cols[i % 6]:
                    st.image(image_of(entry["person"]), width="stretch")
                    st.button(entry["person"]["name"], key=f"cast-{entry['person']['id']}",
                              on_click=go, args=("person", entry["person"]["id"]), width="stretch")
                    st.caption(f"as {entry['character']['name']}")
        else:
            st.caption("No cast information available.")

        st.subheader(f"Episodes ({len(episodes)})")
        for season, eps in tvmaze.group_by_season(episodes).items():
            with st.expander(f"Season {season} ({len(eps)} episodes)"):
                for ep in eps:
                    number = ep.get("number")
                    label = f"E{number}" if number else "Special"
                    st.write(f"**{label}** · {ep['name']} · {ep.get('airdate') or 'no date'}")

        st.subheader("You might also like")
        try:
            related = tvmaze.get_related_shows(show)
        except TVmazeError:
            related = []
        if related:
            show_grid(related, "rel")
        else:
            st.caption("No recommendations available.")

    # ---------- Person detail ----------
    elif page[0] == "person":
        person = cached("get_person", page[1])
        left, right = st.columns([1, 4])
        left.image(image_of(person, "original"), width="stretch")
        right.header(person["name"])
        right.write(f"Born: {person.get('birthday') or '–'} · "
                    f"Country: {(person.get('country') or {}).get('name') or '–'}")
        st.subheader("Shows")
        show_grid(cached("get_credits", page[1]), "credit")

except TVmazeError as err:
    st.error(f"API error: {err}")
    st.button("Back to home", on_click=go, args=("home",), key="err-home")
