"""
src/email_sender.py
───────────────────
Sends the IPO-alert email over Gmail SMTP (port 587, STARTTLS).

Uses the App Password stored in .env — never your normal Gmail password.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
from config import SENDER_EMAIL, SENDER_APP_PASSWORD, RECIPIENT_EMAIL

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def _build_html(ipos: list[dict], report_date: date) -> str:
    """Build a clean HTML email body from the filtered IPO list."""

    rows = ""
    for ipo in ipos:
        offer_m = ipo["offer_amount"] / 1_000_000          # millions
        rows += f"""
        <tr>
          <td style="padding:10px 14px; font-weight:700; color:#0f172a;">{ipo.get('symbol','—')}</td>
          <td style="padding:10px 14px; color:#334155;">{ipo.get('company','—')}</td>
          <td style="padding:10px 14px; color:#334155;">${ipo.get('price','—')}</td>
          <td style="padding:10px 14px; color:#334155;">{int(ipo.get('shares',0)):,}</td>
          <td style="padding:10px 14px; font-weight:600; color:#16a34a;">${offer_m:,.1f}M</td>
          <td style="padding:10px 14px; color:#334155;">{ipo.get('exchange','—')}</td>
        </tr>"""

    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family:'Segoe UI', Arial, sans-serif; background:#f1f5f9; padding:30px;">
      <div style="max-width:720px; margin:0 auto; background:#fff; border-radius:12px;
                  box-shadow:0 2px 12px rgba(0,0,0,0.08); overflow:hidden;">

        <!-- Header -->
        <div style="background:linear-gradient(135deg,#0f172a,#1e293b); padding:28px 32px;">
          <h1 style="margin:0; color:#f8fafc; font-size:22px; font-weight:700;">
            📈 IPO Alert — {report_date.strftime('%A, %B %d, %Y')}
          </h1>
          <p style="margin:6px 0 0; color:#94a3b8; font-size:14px;">
            U.S. IPOs pricing today with offer amount &gt; $200M
          </p>
        </div>

        <!-- Table -->
        <div style="padding:24px 28px;">
          <table style="width:100%; border-collapse:collapse; font-size:14px;">
            <thead>
              <tr style="border-bottom:2px solid #e2e8f0;">
                <th style="text-align:left; padding:10px 14px; color:#64748b; font-weight:600;">Ticker</th>
                <th style="text-align:left; padding:10px 14px; color:#64748b; font-weight:600;">Company</th>
                <th style="text-align:left; padding:10px 14px; color:#64748b; font-weight:600;">IPO Price</th>
                <th style="text-align:left; padding:10px 14px; color:#64748b; font-weight:600;">Shares</th>
                <th style="text-align:left; padding:10px 14px; color:#64748b; font-weight:600;">Offer Amount</th>
                <th style="text-align:left; padding:10px 14px; color:#64748b; font-weight:600;">Exchange</th>
              </tr>
            </thead>
            <tbody>{rows}
            </tbody>
          </table>
        </div>

        <!-- Footer -->
        <div style="padding:20px 28px 28px; border-top:1px solid #e2e8f0;">
          <p style="margin:0; color:#94a3b8; font-size:12px;">
            Data source: Nasdaq.com &nbsp;|&nbsp; Sent automatically at 09:00 Dubai time &nbsp;|&nbsp; Automated by ismaeeel.basheer@gmail.com
          </p>
        </div>
      </div>
    </body>
    </html>"""


def send_alert(ipos: list[dict], report_date: date | None = None) -> bool:
    """
    Compose and send the alert email.

    Returns True on success, False on failure.
    """
    if report_date is None:
        report_date = date.today()

    subject = (
        f"IPO Alert! ⚠️ – {report_date.strftime('%Y-%m-%d')} – "
        f"{len(ipos)} ticker(s) above $200M"
    )

    # Build MIME message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    recipients     = [r.strip() for r in RECIPIENT_EMAIL.split(",")]
    msg["To"]      = ", ".join(recipients)

    # Plain-text fallback
    tickers = ", ".join(ipo.get("symbol", "?") for ipo in ipos)
    plain = (
        f"IPO Alert – {report_date}\n\n"
        f"Tickers with offer amount > $200M today: {tickers}\n\n"
        "See HTML version for full details."
    )
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(_build_html(ipos, report_date), "html"))

    # Send
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipients, msg.as_string())
        print(f"[email_sender] Alert sent to {', '.join(recipients)} ✓")
        return True

    except smtplib.SMTPException as exc:
        print(f"[email_sender] SMTP error: {exc}")
        return False
