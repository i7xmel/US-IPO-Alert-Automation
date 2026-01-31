"""
src/ipo_filter.py
-----------------
Filters the raw IPO list from NASDAQ (via finance-calendars).

Actual NASDAQ columns (confirmed from live data):
  companyname
  proposedexchange
  proposedshareprice
  sharesoffered
  priceddate                     <- the IPO date
  dollarvalueofsharesoffered     <- deal size, pre-calculated by NASDAQ
  dealstatus

Two-step filter:
  1. DATE MATCH   – keep only rows where priceddate == today
  2. OFFER SIZE   – keep only rows where dollarvalueofsharesoffered > $200M
                    (falls back to proposedshareprice x sharesoffered if missing)
"""

import re
from datetime import date, datetime
from config import OFFER_THRESHOLD_USD


def _parse_date_value(val) -> str | None:
    """
    Convert whatever date format NASDAQ returns into "YYYY-MM-DD".
    Handles: datetime objects, "2026-01-31", "01/31/2026", "Jan 31, 2026", etc.
    """
    if val is None:
        return None

    if isinstance(val, (datetime, date)):
        return val.strftime("%Y-%m-%d")

    val_str = str(val).strip()

    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%b %d, %Y", "%B %d, %Y", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(val_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Last resort: pull YYYY-MM-DD pattern from anywhere in the string
    match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", val_str)
    if match:
        return f"{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"

    return None


def _parse_number(val) -> float | None:
    """Clean and convert a value to float. Strips commas, $, spaces."""
    if val is None:
        return None
    val_str = str(val).strip().replace(",", "").replace("$", "").replace(" ", "")
    try:
        return float(val_str)
    except (ValueError, TypeError):
        return None


def filter_ipos(raw_ipos: list[dict], target_date: date | None = None) -> list[dict]:
    """
    Apply date + offer-size filters using the exact NASDAQ column names.
    """
    if target_date is None:
        target_date = date.today()

    today_str = target_date.isoformat()
    passed: list[dict] = []

    for ipo in raw_ipos:
        # ── 1. Same-day date filter ─────────────────────
        parsed_date = _parse_date_value(ipo.get("priceddate"))

        if parsed_date != today_str:
            continue

        # ── 2. Offer amount filter ──────────────────────
        # Primary: use NASDAQ's pre-calculated deal size
        offer_amount = _parse_number(ipo.get("dollarvalueofsharesoffered"))

        # Fallback: calculate ourselves from price x shares
        if not offer_amount:
            price  = _parse_number(ipo.get("proposedshareprice"))
            shares = _parse_number(ipo.get("sharesoffered"))
            if price and shares:
                offer_amount = price * shares
            else:
                print(
                    f"[ipo_filter] Skipping {ipo.get('companyname', '?')} — "
                    f"no deal size or price/shares available"
                )
                continue

        if offer_amount <= OFFER_THRESHOLD_USD:
            continue

        # ── Passed both filters — build clean output dict ──
        # NASDAQ doesn't return a ticker symbol directly,
        # so we use the company name as the identifier
        passed.append({
            "symbol":       ipo.get("companyname", "—"),   # company name as label
            "company":      ipo.get("companyname", "—"),
            "price":        _parse_number(ipo.get("proposedshareprice")),
            "shares":       _parse_number(ipo.get("sharesoffered")),
            "offer_amount": offer_amount,
            "exchange":     ipo.get("proposedexchange", "—"),
            "date":         parsed_date,
        })

    print(
        f"[ipo_filter] {len(passed)} IPO(s) passed filters "
        f"(date={today_str}, threshold=${OFFER_THRESHOLD_USD:,.0f})"
    )
    return passed
