"""Streamlit dashboard to browse the scraped books.

Data source: Supabase (public.books, read-only via the publishable key) if
configured, otherwise the local data/books.json file, so the app always runs.
"""
import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
JSON_PATH = Path(__file__).parent / "data" / "books.json"


@st.cache_data(ttl=300, show_spinner="Loading books...")
def load_books():
    """Return (DataFrame, source label). Prefer Supabase, fall back to JSON."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_PUBLISHABLE_KEY")
    if url and key:
        try:
            from supabase import create_client

            client = create_client(url, key)
            rows, start = [], 0
            while True:  # page through results (API returns max 1000 per request)
                page = client.table("books").select("*").range(start, start + 999).execute().data
                rows += page
                if len(page) < 1000:
                    break
                start += 1000
            if rows:
                return pd.DataFrame(rows), "Supabase (PostgreSQL)"
        except Exception as error:
            st.warning(f"Supabase not reachable ({error}). Using local JSON instead.")
    with open(JSON_PATH, encoding="utf-8") as f:
        return pd.DataFrame(json.load(f)), "data/books.json (local)"


st.set_page_config(page_title="Book Scraper", page_icon="📚", layout="wide")
st.title("📚 Book Scraper")
st.caption("Books scraped from books.toscrape.com and stored in Supabase.")

df, source = load_books()
st.caption(f"Data source: **{source}**")

# --- Sidebar filters ---
st.sidebar.header("Filters")
search = st.sidebar.text_input("Search title")
categories = st.sidebar.multiselect("Category", sorted(df["category"].dropna().unique()))
min_rating = st.sidebar.slider("Minimum rating (stars)", 1, 5, 1)
price_min, price_max = float(df["price_gbp"].min()), float(df["price_gbp"].max())
price = st.sidebar.slider("Price (GBP)", price_min, price_max, (price_min, price_max))
only_in_stock = st.sidebar.checkbox("Only in stock")

view = df[df["rating"].ge(min_rating) & df["price_gbp"].between(*price)]
if search:
    view = view[view["title"].str.contains(search, case=False, na=False)]
if categories:
    view = view[view["category"].isin(categories)]
if only_in_stock:
    view = view[view["in_stock"]]

# --- Metrics ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Books", len(view))
c2.metric("Categories", view["category"].nunique())
c3.metric("Avg. price", f"£{view['price_gbp'].mean():.2f}" if len(view) else "–")
c4.metric("Avg. rating", f"{view['rating'].mean():.2f} ★" if len(view) else "–")

# --- Charts ---
left, right = st.columns(2)
with left:
    st.subheader("Books per category")
    st.bar_chart(view["category"].value_counts())
with right:
    st.subheader("Rating distribution")
    st.bar_chart(view["rating"].value_counts().sort_index())

# --- Table ---
st.subheader("Books")
st.dataframe(
    view[["title", "category", "price_gbp", "rating", "in_stock", "stock_count", "product_url"]],
    width="stretch",
    hide_index=True,
    column_config={
        "price_gbp": st.column_config.NumberColumn("Price (£)", format="£%.2f"),
        "rating": st.column_config.NumberColumn("Rating", format="%d ★"),
        "product_url": st.column_config.LinkColumn("Link", display_text="open"),
    },
)

# --- Detail view ---
if len(view):
    st.subheader("Book details")
    title = st.selectbox("Select a book", view["title"].tolist())
    book = view[view["title"] == title].iloc[0]
    img, info = st.columns([1, 3])
    if book.get("image_url"):
        img.image(book["image_url"])
    info.markdown(f"### {book['title']}")
    info.write(f"**Category:** {book['category']} · **Price:** £{book['price_gbp']:.2f} · "
               f"**Rating:** {'★' * int(book['rating'])}{'☆' * (5 - int(book['rating']))}")
    info.write(book.get("description") or "No description available.")
