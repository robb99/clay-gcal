#!/usr/bin/env python3
"""Google Calendar utility.

Stores credentials in a machine-level shared directory by default:
  - OAuth client JSON: /Users/Shared/openclaw-secrets/google-calendar-oauth-client.json
  - Token JSON:        /Users/Shared/openclaw-secrets/google-calendar-token.json

Override paths with env vars:
  - GCAL_CLIENT_FILE
  - GCAL_TOKEN_FILE

Usage:
  python3 tools/gcal.py auth
  python3 tools/gcal.py list-calendars
  python3 tools/gcal.py next [N]
  python3 tools/gcal.py create "Title" "YYYY-MM-DD HH:MM" "YYYY-MM-DD HH:MM"
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from datetime import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SECRETS_DIR = Path("/Users/Shared/openclaw-secrets")
CLIENT_FILE = Path(os.environ.get("GCAL_CLIENT_FILE", str(SECRETS_DIR / "google-calendar-oauth-client.json")))
TOKEN_FILE = Path(os.environ.get("GCAL_TOKEN_FILE", str(SECRETS_DIR / "google-calendar-token.json")))

SCOPES = ["https://www.googleapis.com/auth/calendar"]
DEFAULT_TZ = "America/New_York"


def load_creds() -> Credentials:
    if not TOKEN_FILE.exists():
        raise RuntimeError("No token yet. Run: gcal.py auth")

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


def do_auth():
    if not CLIENT_FILE.exists():
        raise RuntimeError(f"Missing OAuth client file at {CLIENT_FILE}")

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_FILE), SCOPES)
    creds = flow.run_local_server(host="127.0.0.1", port=8765, open_browser=False)

    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(creds.to_json())
    print(f"✅ Authorized. Token saved to {TOKEN_FILE}")


def list_calendars():
    service = build("calendar", "v3", credentials=load_creds())
    res = service.calendarList().list().execute()
    for cal in res.get("items", []):
        primary = " (primary)" if cal.get("primary") else ""
        print(f"- {cal.get('summary')} :: {cal.get('id')}{primary}")


def next_events(n: int = 10):
    service = build("calendar", "v3", credentials=load_creds())
    now = datetime.utcnow().isoformat() + "Z"
    res = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=n,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = res.get("items", [])
    if not events:
        print("(no upcoming events)")
        return

    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date"))
        end = e["end"].get("dateTime", e["end"].get("date"))
        print(f"- {start} → {end} | {e.get('summary','(no title)')}")


def create_event(title: str, start_local: str, end_local: str):
    service = build("calendar", "v3", credentials=load_creds())
    start_dt = datetime.strptime(start_local, "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(end_local, "%Y-%m-%d %H:%M")

    body = {
        "summary": title,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": DEFAULT_TZ},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": DEFAULT_TZ},
    }

    ev = service.events().insert(calendarId="primary", body=body).execute()
    print(f"✅ Created: {ev.get('htmlLink')}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "auth":
        do_auth()
    elif cmd == "list-calendars":
        list_calendars()
    elif cmd == "next":
        n = int(sys.argv[2]) if len(sys.argv) >= 3 else 10
        next_events(n)
    elif cmd == "create":
        if len(sys.argv) < 5:
            raise SystemExit('Usage: create "Title" "YYYY-MM-DD HH:MM" "YYYY-MM-DD HH:MM"')
        create_event(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        raise SystemExit(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
