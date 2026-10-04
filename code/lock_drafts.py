"""Encrypt drafts/ into scheduled/ and write the public schedule. Run by the author, never by CI.

Usage:
    python code/lock_drafts.py            # uses DRAFTS_KEY from the environment
    python code/lock_drafts.py --new-key  # prints a new key to store as the repo secret DRAFTS_KEY

Each drafts/<name>.md becomes scheduled/<name>.md.enc (Fernet: AES-128-CBC + HMAC-SHA256).
scheduled/schedule.json lists only issue, slot, title, and release date, which are public.
"""
import json
import os
import sys
from pathlib import Path

import yaml
from cryptography.fernet import Fernet

ROOT = Path(__file__).resolve().parent.parent

if "--new-key" in sys.argv:
    print(Fernet.generate_key().decode())
    sys.exit(0)

key = os.environ.get("DRAFTS_KEY")
if not key:
    sys.exit("Set DRAFTS_KEY first (python code/lock_drafts.py --new-key makes one).")
f = Fernet(key.encode())

out = ROOT / "scheduled"
out.mkdir(exist_ok=True)
schedule = []
for p in sorted((ROOT / "drafts").glob("*.md")):
    meta = yaml.safe_load(p.read_text().split("---", 2)[1])
    (out / (p.name + ".enc")).write_bytes(f.encrypt(p.read_bytes()))
    schedule.append({
        "file": p.name,
        "issue": meta["issue"],
        "series_slot": meta["series_slot"],
        "title": meta["title"],
        "release_date": str(meta["published"]),
    })
(out / "schedule.json").write_text(json.dumps(schedule, indent=2) + "\n")
print(f"locked {len(schedule)} drafts into scheduled/")
