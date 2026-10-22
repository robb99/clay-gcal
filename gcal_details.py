#!/usr/bin/env python3
"""Show full details for upcoming calendar events (location, description, reminders).

gcal.py's `next` only prints time + title, which is thin for a reminder.
"""
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent))
from gcal import load_creds, build  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument('--hours', type=int, default=48, help='look ahead this many hours')
p.add_argument('--json', action='store_true', help='JSON output')
args = p.parse_args()

service = build('calendar', 'v3', credentials=load_creds())

now = datetime.now(timezone.utc)
res = service.events().list(
    calendarId='primary',
    timeMin=now.isoformat(),
    timeMax=(now + timedelta(hours=args.hours)).isoformat(),
    maxResults=25,
    singleEvents=True,
    orderBy='startTime',
).execute()

events = res.get('items', [])
if not events:
    print('(no upcoming events)')
    sys.exit(0)

if args.json:
    print(json.dumps([
        {
            'summary': e.get('summary', '(no title)'),
            'start': e.get('start', {}).get('dateTime', e.get('start', {}).get('date')),
            'end': e.get('end', {}).get('dateTime', e.get('end', {}).get('date')),
            'location': e.get('location', ''),
            'description': e.get('description', ''),
        } for e in events
    ], indent=2))
    sys.exit(0)

for e in events:
    start = e.get('start', {}).get('dateTime', e.get('start', {}).get('date'))
    end = e.get('end', {}).get('dateTime', e.get('end', {}).get('date'))
    print(f"- {e.get('summary','(no title)')}")
    print(f"    when:  {start} → {end}")
    loc = e.get('location', '')
    if loc:
        print(f"    where: {loc}")
    desc = (e.get('description') or '').strip()
    if desc:
        print(f"    notes: {desc[:300]}")
    print()
