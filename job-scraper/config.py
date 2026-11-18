"""Configuration for Step 1 data collection (jobs side)."""

# --- Greenhouse & Lever target companies ------------------------------------
# Verified 2026-09-14 by querying the live boards directly (each returns
# HTTP 200 and has open Finance/Strategy-relevant roles at the time of check):
#   - n26, celonis, getyourguide, helloFresh: Germany-headquartered, Greenhouse
#   - farfetch: Portugal-headquartered (Porto/Lisboa), Lever
GREENHOUSE_COMPANIES = [
    {"slug": "n26", "name": "N26"},
    {"slug": "celonis", "name": "Celonis"},
    {"slug": "getyourguide", "name": "GetYourGuide"},
    {"slug": "helloFresh", "name": "HelloFresh"},
]

LEVER_COMPANIES = [
    {"slug": "farfetch", "name": "Farfetch"},
]

# --- Adzuna search scope -----------------------------------------------------
# Target scope for testing (step1-data-collection-context.md, section 3):
# Finance/Strategy roles, Germany & Portugal, Python stack.
# NOTE: Adzuna does not support Portugal as a country code (confirmed
# 2026-09-14: /jobs/pt/... returns UNSUPPORTED_COUNTRY). Supported codes are
# at, au, be, br, ca, ch, de, es, fr, gb, in, it, mx, nl, nz, pl, sg, us, za.
# Portugal coverage instead comes from the Farfetch Lever board.
ADZUNA_COUNTRIES = ["de"]
ADZUNA_KEYWORDS = ["finance", "strategy"]
ADZUNA_RESULTS_PER_PAGE = 20
ADZUNA_MAX_PAGES = 1  # keep the free tier's ~1,000 calls/month in mind
