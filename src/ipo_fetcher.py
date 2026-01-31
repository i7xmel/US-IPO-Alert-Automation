"""
src/ipo_fetcher.py
──────────────────
Uses the 'finance-calendars' package which wraps NASDAQ's public API.
No API key needed. No scraping. Returns clean structured data.

We call two methods:
  - get_upcoming_ipos_this_month()  → IPOs not yet priced (scheduled)
  - get_priced_ipos_this_month()    → IPOs already priced this month

Both are combined so we catch today's IPO whether it flipped to
"priced" status already or is still showing as "upcoming".

Returned columns from NASDAQ typically include:
  Company, IPO Date, Price, Shares, Status, Exchange, etc.
"""

from datetime import date
import pandas as pd

try:
    from finance_calendars import finance_calendars as fc
except ImportError:
    raise ImportError(
        "finance-calendars is not installed.\n"
        "Run:  pip install -r requirements.txt"
    )


def fetch_ipos(target_date: date | None = None) -> list[dict]:
    """
    Fetch this month's upcoming + priced IPOs from NASDAQ via finance-calendars.
    Returns a list of dicts (one per IPO row).
    """
    if target_date is None:
        target_date = date.today()

    print(f"[ipo_fetcher] Fetching IPO data from NASDAQ (finance-calendars)...")

    all_rows: list[pd.DataFrame] = []

    # ── Upcoming (not yet priced) ────────────────────
    try:
        upcoming_df = fc.get_upcoming_ipos_this_month()
        if upcoming_df is not None and not upcoming_df.empty:
            print(f"[ipo_fetcher] Upcoming IPOs this month: {len(upcoming_df)}")
            all_rows.append(upcoming_df)
        else:
            print("[ipo_fetcher] No upcoming IPOs this month.")
    except Exception as exc:
        print(f"[ipo_fetcher] Could not fetch upcoming IPOs: {exc}")

    # ── Already priced ───────────────────────────────
    try:
        priced_df = fc.get_priced_ipos_this_month()
        if priced_df is not None and not priced_df.empty:
            print(f"[ipo_fetcher] Priced IPOs this month: {len(priced_df)}")
            all_rows.append(priced_df)
        else:
            print("[ipo_fetcher] No priced IPOs this month.")
    except Exception as exc:
        print(f"[ipo_fetcher] Could not fetch priced IPOs: {exc}")

    # ── Merge ────────────────────────────────────────
    if not all_rows:
        print("[ipo_fetcher] No IPO data returned at all.")
        return []

    combined = pd.concat(all_rows, ignore_index=True)

    # Normalize column names to lowercase, strip whitespace
    combined.columns = [c.strip().lower().replace(" ", "_") for c in combined.columns]

    print(f"[ipo_fetcher] Total rows after merge: {len(combined)}")
    print(f"[ipo_fetcher] Columns available: {list(combined.columns)}")

    # Convert to list of dicts for downstream processing
    ipos: list[dict] = combined.to_dict(orient="records")
    return ipos
