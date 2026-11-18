"""Load scraped books into Supabase (table: public.books)."""
import argparse
import json
import os
import sys

from dotenv import load_dotenv
from supabase import create_client

TABLE = "books"
TEST_UPC = "TEST-RESERVED-0000"
REQUIRED = ["upc", "title", "product_url"]


def get_client():
    """Create a Supabase client from environment variables."""
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        sys.exit("Missing SUPABASE_URL and/or SUPABASE_SECRET_KEY. Fill in your local .env file.")
    return create_client(url, key)


def show_examples(rows):
    for row in rows[:3]:
        print(f"  {row['upc']} | {row['title'][:50]} | GBP {row['price_gbp']} | rating {row['rating']}")


def run_test(client):
    """Insert, read back and delete a temporary test book."""
    test_book = {"upc": TEST_UPC, "title": "Connection Test Book", "category": "Test",
                 "price_gbp": 1.00, "price_incl_tax_gbp": 1.00, "tax_gbp": 0.00,
                 "in_stock": True, "stock_count": 1, "rating": 5, "num_reviews": 0}
    ok = False
    try:
        client.table(TABLE).upsert(test_book, on_conflict="upc").execute()
        rows = client.table(TABLE).select("*").eq("upc", TEST_UPC).execute().data
        ok = len(rows) == 1 and rows[0]["title"] == test_book["title"]
        print("Read-back matches." if ok else "Read-back MISMATCH.")
    finally:
        client.table(TABLE).delete().eq("upc", TEST_UPC).execute()
        left = client.table(TABLE).select("upc").eq("upc", TEST_UPC).execute().data
        print("Cleanup verified." if not left else "Cleanup FAILED.")
        ok = ok and not left
    print("CONNECTION TEST PASSED" if ok else "CONNECTION TEST FAILED")
    return ok


def import_books(client, path):
    with open(path, encoding="utf-8") as f:
        books = json.load(f)
    for book in books:
        missing = [k for k in REQUIRED if not book.get(k)]
        if missing:
            sys.exit(f"Book {book.get('upc')} is missing fields: {missing}")
    # Remove duplicate UPCs within the file, then upsert in batches.
    unique = list({b["upc"]: b for b in books}.values())
    for i in range(0, len(unique), 50):
        client.table(TABLE).upsert(unique[i:i + 50], on_conflict="upc").execute()

    upcs = [b["upc"] for b in unique]
    found = []
    for i in range(0, len(upcs), 50):
        found += client.table(TABLE).select("*").in_("upc", upcs[i:i + 50]).execute().data
    print(f"Imported and verified {len(found)}/{len(unique)} books.")
    show_examples(found)
    total = client.table(TABLE).select("upc", count="exact").limit(1).execute().count
    print(f"Total rows in public.books: {total}")
    return len(found) == len(unique)


def main():
    parser = argparse.ArgumentParser(description="Load books into Supabase")
    parser.add_argument("--test", action="store_true", help="run a connection test")
    parser.add_argument("--file", help="JSON file to import")
    args = parser.parse_args()
    if not args.test and not args.file:
        parser.error("use --test or --file")
    try:
        client = get_client()
        ok = run_test(client) if args.test else import_books(client, args.file)
    except Exception as error:
        sys.exit(f"Supabase error: {error}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
