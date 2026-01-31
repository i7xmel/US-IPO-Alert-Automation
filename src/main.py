"""
src/main.py
-----------
Single entry-point for the IPO monitor.

  1. Validates env vars (fail fast with a clear message)
  2. Fetches this month's IPO data from NASDAQ
  3. Prints all dates found (debug) so we can confirm matching works
  4. Filters to same-day IPOs with offer amount > $200M
  5. Sends an email alert if any tickers pass
  6. Logs a "nothing to report" message otherwise

Run manually:
    python src/main.py
"""

import sys
import os
from datetime import date, datetime

# Make sure 'config' and 'src' are importable from anywhere
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config           import validate
from src.ipo_fetcher  import fetch_ipos
from src.ipo_filter   import filter_ipos
from src.email_sender import send_alert


def main() -> None:
    now = datetime.now()
    print("=" * 60)
    print(f"  IPO Monitor  –  {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Env-var check
    try:
        validate()
    except EnvironmentError as exc:
        print(f"\n[FATAL] {exc}")
        sys.exit(1)

    today = date(2026, 1, 29)
    print(f"\n[main] Target date : {today}")

    # 2. Fetch
    raw_ipos = fetch_ipos(target_date=today)
    if not raw_ipos:
        print("[main] No IPO data returned. Done.")
        return

    # 3. Debug: show all priceddate values so we can confirm date matching
    print("\n[main] All priceddate values from NASDAQ:")
    for ipo in raw_ipos:
        print(f"        {ipo.get('priceddate')}  |  {ipo.get('companyname', '?')}")

    # 4. Filter (same-day + offer > $200M)
    qualified = filter_ipos(raw_ipos, target_date=today)
    if not qualified:
        print(
            "\n[main] No same-day IPOs above the $200M offer threshold today. "
            "No email sent."
        )
        return

    # 5. Email
    print(f"\n[main] Qualified: {', '.join(i['symbol'] for i in qualified)}")
    success = send_alert(qualified, report_date=today)

    if not success:
        print("[main] Email sending failed. Check SMTP credentials in .env.")
        sys.exit(1)

    print("\n[main] Done ✓")


if __name__ == "__main__":
    main()
