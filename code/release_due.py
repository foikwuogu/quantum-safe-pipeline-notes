"""Release scheduled posts whose date has arrived. Run daily by .github/workflows/publish.yml.

For each entry in scheduled/schedule.json with release_date <= today (America/Chicago),
decrypt scheduled/<file>.enc with the DRAFTS_KEY secret into posts/<file>, delete the
encrypted copy, and drop the entry from the schedule. Fails loudly if a post is due and the
key is missing or wrong, so GitHub emails the repository owner instead of silently skipping.
"""
import datetime as dt
import json
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
SCHED = ROOT / "scheduled" / "schedule.json"

today = os.environ.get("RELEASE_AS_OF") or dt.datetime.now(ZoneInfo("America/Chicago")).date().isoformat()
if not SCHED.exists():
    print("no schedule; nothing to release")
    sys.exit(0)

schedule = json.loads(SCHED.read_text())

if "--check-key" in sys.argv:
    # Run every day so a missing or wrong DRAFTS_KEY shows up now, not on release day.
    key = os.environ.get("DRAFTS_KEY")
    if not schedule:
        print("no locked posts to check")
        sys.exit(0)
    if not key:
        sys.exit("DRAFTS_KEY secret is not set; locked posts cannot be released on their dates.")
    from cryptography.fernet import Fernet, InvalidToken
    try:
        f = Fernet(key.encode())
        for e in schedule:
            f.decrypt((ROOT / "scheduled" / (e["file"] + ".enc")).read_bytes())
    except (InvalidToken, ValueError):
        sys.exit("DRAFTS_KEY cannot decrypt the locked posts; re-enter the repository secret exactly.")
    print(f"DRAFTS_KEY OK: all {len(schedule)} locked posts decrypt")
    sys.exit(0)

due = [e for e in schedule if e["release_date"] <= today]
if not due:
    print(f"{today}: nothing due; next release {min((e['release_date'] for e in schedule), default='none')}")
    sys.exit(0)

key = os.environ.get("DRAFTS_KEY")
if not key:
    sys.exit(f"{len(due)} post(s) due on {today} but the DRAFTS_KEY secret is not set.")

from cryptography.fernet import Fernet, InvalidToken  # noqa: E402

f = Fernet(key.encode())
for e in due:
    enc = ROOT / "scheduled" / (e["file"] + ".enc")
    try:
        text = f.decrypt(enc.read_bytes()).decode()
    except InvalidToken:
        sys.exit(f"DRAFTS_KEY cannot decrypt {enc.name}; check the repository secret.")
    text = text.replace("status: scheduled", "status: published", 1)
    (ROOT / "posts" / e["file"]).write_text(text)
    enc.unlink()
    print(f"released issue {e['issue']:02d}: {e['title']}")

remaining = [e for e in schedule if e not in due]
SCHED.write_text(json.dumps(remaining, indent=2) + "\n")
