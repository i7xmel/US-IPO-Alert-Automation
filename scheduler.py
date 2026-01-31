"""
scheduler.py
────────────
Run this script ONCE to print the exact commands you need to paste into
your OS scheduler.  It does NOT modify anything automatically.

    python scheduler.py

Dubai Standard Time = UTC + 4  →  9:00 AM Dubai = 05:00 UTC
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MAIN_SCRIPT  = os.path.join(PROJECT_ROOT, "src", "main.py")


def print_instructions() -> None:
    print("=" * 70)
    print("  IPO Monitor – Scheduler Setup Instructions")
    print("=" * 70)

    # ── LINUX / macOS (crontab) ──────────────────────────────────
    print("""
┌─────────────────────────────────────────────────────────────────┐
│  LINUX / macOS  –  crontab                                      │
└─────────────────────────────────────────────────────────────────┘

  Step 1 – Open your crontab editor:

      crontab -e

  Step 2 – Paste the line below (replace <PATH> with your actual path):

      0 5 * * 1-5 /usr/bin/env python3 """ + MAIN_SCRIPT + """ >> """ + os.path.join(PROJECT_ROOT, "ipo_monitor.log") + """ 2>&1

  Explanation of the cron schedule:
      0   5   *   *   1-5
      │   │   │   │   └── Mon–Fri only (US market days)
      │   │   │   └────── Every month
      │   │   └────────── Every day
      │   └────────────── 05:00 UTC  =  09:00 Dubai time
      └────────────────── Minute 0

  Step 3 – Save and exit (Ctrl + S, then Ctrl + X if using nano).

  Step 4 – Verify it was saved:

      crontab -l

""")

    # ── WINDOWS (Task Scheduler) ─────────────────────────────────
    # For Windows we need to know the python path; assume venv or global
    print("""┌─────────────────────────────────────────────────────────────────┐
│  WINDOWS  –  Task Scheduler (schtasks)                          │
└─────────────────────────────────────────────────────────────────┘

  Option A – GUI (easiest)
  ────────────────────────
    1.  Open "Task Scheduler" from the Start menu.
    2.  Right-click "Tasks" in the left pane → Create Basic Task…
    3.  Name it:        IPO Monitor
    4.  Trigger:        Daily
    5.  Start time:     09:00 AM
    6.  Time zone:      (Asia/Dubai) – tick "Use UTC" and set 05:00 AM instead
                        OR leave as local time if your PC is already in Dubai.
    7.  Action:         Start a program
    8.  Program:        python.exe   (or full path, e.g. C:\\Python311\\python.exe)
    9.  Arguments:      """ + MAIN_SCRIPT + """
   10.  Finish the wizard → Done.

  Option B – Command-line (one-liner)
  ────────────────────────────────────
  Open cmd.exe as Administrator and run (edit the paths):

      schtasks /create /tn "IPO Monitor" ^
        /tr "python.exe """ + MAIN_SCRIPT + """" ^
        /sc daily /st 09:00 /ru SYSTEM /rl HIGHEST /f

  Note: If your Windows clock is NOT set to Dubai time, use the GUI
        approach and enable "Use UTC" with start time 05:00 AM.
""")

    # ── DOCKER / SERVER (systemd) ────────────────────────────────
    print("""┌─────────────────────────────────────────────────────────────────┐
│  SERVER  –  systemd timer  (optional, production-grade)         │
└─────────────────────────────────────────────────────────────────┘

  Create two files in /etc/systemd/system/ :

  ── /etc/systemd/system/ipo-monitor.service ──
      [Unit]
      Description=IPO Monitor – daily alert

      [Service]
      ExecStart=/usr/bin/env python3 """ + MAIN_SCRIPT + """
      WorkingDirectory=""" + PROJECT_ROOT + """
      Environment="PYTHONPATH=""" + PROJECT_ROOT + """"
      StandardOutput=append:""" + os.path.join(PROJECT_ROOT, "ipo_monitor.log") + """
      StandardError=append:""" + os.path.join(PROJECT_ROOT, "ipo_monitor.log") + """

  ── /etc/systemd/system/ipo-monitor.timer ──
      [Unit]
      Description=Run IPO Monitor every weekday at 05:00 UTC (09:00 Dubai)

      [Timer]
      OnCalendar=Mon-Fri 05:00 UTC
      Persistent=true

      [Install]
      WantedBy=timers.target

  Then enable & start:
      sudo systemctl daemon-reload
      sudo systemctl enable ipo-monitor.timer
      sudo systemctl start  ipo-monitor.timer
""")


if __name__ == "__main__":
    print_instructions()
