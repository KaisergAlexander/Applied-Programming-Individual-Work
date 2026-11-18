"""Validate a scraped books JSON file. Usage: python validate.py FILE EXPECTED_COUNT"""
import json
import sys
from decimal import Decimal

path, expected = sys.argv[1], int(sys.argv[2])
books = json.load(open(path, encoding="utf-8"))
errors = []
if len(books) != expected:
    errors.append(f"expected {expected} records, got {len(books)}")
if len({b["upc"] for b in books}) != len(books):
    errors.append("duplicate UPCs")
for b in books:
    if not b["title"] or not b["product_url"]:
        errors.append(f"{b['upc']}: missing title/url")
    if not 1 <= b["rating"] <= 5:
        errors.append(f"{b['upc']}: bad rating {b['rating']}")
    if not isinstance(b["stock_count"], int) or b["stock_count"] < 0:
        errors.append(f"{b['upc']}: bad stock_count")
    try:
        p, t, i = (Decimal(str(b[k])) for k in ("price_gbp", "tax_gbp", "price_incl_tax_gbp"))
        if p + t != i:
            errors.append(f"{b['upc']}: {p}+{t}!={i}")
    except Exception:
        errors.append(f"{b['upc']}: non-numeric price")
print(f"Records: {len(books)}, unique UPCs: {len({b['upc'] for b in books})}")
for b in books[:3]:
    print(json.dumps({**b, "description": b["description"][:60] + "..."}, ensure_ascii=False, indent=1))
print("VALIDATION FAILED:" if errors else "ALL VALIDATIONS PASSED", *errors, sep="\n" if errors else " ")
sys.exit(1 if errors else 0)
