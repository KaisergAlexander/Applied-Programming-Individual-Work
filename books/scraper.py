"""Scrape book data from https://books.toscrape.com and save it as JSON."""
import argparse
import json
import re
import time
from decimal import Decimal
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/catalogue/page-1.html"
HEADERS = {"User-Agent": "Mozilla/5.0 (university-project book scraper)"}
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def get_soup(url, delay):
    """Download a page and return a BeautifulSoup object (None on failure)."""
    time.sleep(delay)
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"  ! Could not fetch {url}: {error}")
        return None
    response.encoding = "utf-8"
    return BeautifulSoup(response.text, "html.parser")


def parse_price(text):
    """'Â£51.77' -> Decimal('51.77')"""
    match = re.search(r"\d+(?:\.\d+)?", text or "")
    return Decimal(match.group()) if match else None


def parse_book(url, delay):
    """Scrape one book detail page into a dictionary."""
    soup = get_soup(url, delay)
    if soup is None:
        return None

    table = {}
    for row in soup.select("table.table-striped tr"):
        table[row.th.get_text(strip=True)] = row.td.get_text(strip=True)

    availability = table.get("Availability", "")
    stock_match = re.search(r"\((\d+) available\)", availability)
    stock_count = int(stock_match.group(1)) if stock_match else 0

    crumbs = soup.select("ul.breadcrumb li")
    category = crumbs[2].get_text(strip=True) if len(crumbs) >= 3 else None

    star = soup.select_one("p.star-rating")
    rating = 0
    if star:
        for css_class in star.get("class", []):
            rating = RATINGS.get(css_class, rating)

    description = ""
    description_tag = soup.select_one("#product_description")
    if description_tag:
        paragraph = description_tag.find_next_sibling("p")
        description = paragraph.get_text(strip=True) if paragraph else ""

    image = soup.select_one("#product_gallery img")
    return {
        "upc": table.get("UPC"),
        "title": soup.h1.get_text(strip=True),
        "category": category,
        "price_gbp": float(parse_price(table.get("Price (excl. tax)"))),
        "price_incl_tax_gbp": float(parse_price(table.get("Price (incl. tax)"))),
        "tax_gbp": float(parse_price(table.get("Tax"))),
        "in_stock": "in stock" in availability.lower(),
        "stock_count": stock_count,
        "rating": rating,
        "num_reviews": int(table.get("Number of reviews", 0)),
        "description": description,
        "image_url": urljoin(url, image["src"]) if image else None,
        "product_url": url,
    }


def scrape(limit, delay):
    """Walk through catalogue pages and scrape up to `limit` unique books."""
    books, seen = [], set()
    page_url = BASE_URL
    while page_url and len(books) < limit:
        print(f"Listing page: {page_url}")
        soup = get_soup(page_url, delay)
        if soup is None:
            break
        for link in soup.select("article.product_pod h3 a"):
            if len(books) >= limit:
                break
            book = parse_book(urljoin(page_url, link["href"]), delay)
            if book is None or book["upc"] in seen:
                continue
            seen.add(book["upc"])
            books.append(book)
            print(f"  [{len(books)}/{limit}] {book['title']}")
        next_link = soup.select_one("li.next a")
        page_url = urljoin(page_url, next_link["href"]) if next_link else None
    return books


def main():
    parser = argparse.ArgumentParser(description="Scrape books.toscrape.com")
    parser.add_argument("--limit", type=int, default=10, help="max books")
    parser.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    parser.add_argument("--out", default="data/books.json", help="output JSON file")
    args = parser.parse_args()

    books = scrape(args.limit, args.delay)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(books)} books to {args.out}")


if __name__ == "__main__":
    main()
