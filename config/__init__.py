"""
config/__init__.py
------------------
Reads every value from the .env file and exposes them as module-level
constants.  Import this anywhere instead of calling os.getenv() directly.

NOTE: FINNHUB_API_KEY is no longer required. We now scrape stockanalysis.com
which is free and needs no API key.
"""

import os
from dotenv import load_dotenv

# Walk up from this file to the project root to find .env
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_BASE_DIR, ".env"))

# ── Gmail SMTP ───────────────────────────────────────
SENDER_EMAIL: str        = os.getenv("SENDER_EMAIL", "")
SENDER_APP_PASSWORD: str = os.getenv("SENDER_APP_PASSWORD", "")
RECIPIENT_EMAIL: str     = os.getenv("RECIPIENT_EMAIL", "")

# ── Filter ───────────────────────────────────────────
# Offer amount threshold in USD (default 200 million)
OFFER_THRESHOLD_USD: float = float(
    os.getenv("OFFER_THRESHOLD_MILLIONS", "200")
) * 1_000_000


def validate() -> None:
    """
    Raise early if any required env var is missing.
    Call this at the very start of main() so failures are obvious.
    """
    missing = []
    for name, value in {
        "SENDER_EMAIL":        SENDER_EMAIL,
        "SENDER_APP_PASSWORD": SENDER_APP_PASSWORD,
        "RECIPIENT_EMAIL":     RECIPIENT_EMAIL,
    }.items():
        if not value:
            missing.append(name)

    if missing:
        raise EnvironmentError(
            "Missing required environment variables:\n  - "
            + "\n  - ".join(missing)
            + "\n\nOpen your .env file and fill in the values."
        )
