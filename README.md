# clay-gcal 📅

Google Calendar CLI for Clay — read and create events.

Built 2026-10-21. `gcal_details.py` added 2026-10-22 when plain
time + title turned out to be too thin for a useful reminder.

## Setup

OAuth 2.0 (web application type):
- Client: `/Users/Shared/openclaw-secrets/google-calendar-oauth-client.json`
- Token: `/Users/Shared/openclaw-secrets/google-calendar-token.json`
  (auto-refreshes; the refresh token was re-consented 2026-10-22)

Token scope is **`calendar` only** — this tool cannot read Gmail. If you want
Gmail monitoring too, re-consent with a `gmail.readonly` scope added.

## Tools

### `gcal.py` — quick look at the next N events

```bash
python3 gcal.py list-calendars
python3 gcal.py next 5
python3 gcal.py "Title" "2026-11-01 15:00" "2026-11-01 16:00"
```

`next` prints `start → end | summary`. That's all — no location, no notes.

### `gcal_details.py` — upcoming events with full detail

```bash
python3 gcal_details.py --hours 48
python3 gcal_details.py --hours 24 --json
```

Adds **location** and **description** to each event, which is what you want
before reminding someone. `--hours` controls the lookahead (default 48).

## Notes

- Python 3.9 `FutureWarning` / `NotOpenSSLWarning` from the Google
  dependencies and `urllib3` are harmless noise. Filter them out.
- Invoke the scripts directly (`python3 gcal.py ...`). Compound interpreter
  invocations get refused by the runtime preflight.
- Times come back in the event's own timezone offset (e.g. `-04:00` for ET).
  Compare against `datetime.now(timezone.utc)` when doing "starts within 2h"
  math — don't compare naive local strings.

## Why this exists

Heartbeats need to answer "is anything starting in the next 2 hours?" and
deliver a reminder worth reading. `gcal.py next` answers the first question
barely; `gcal_details.py` answers the second properly.
