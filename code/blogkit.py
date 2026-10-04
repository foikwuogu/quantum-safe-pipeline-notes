"""Shared helpers: post loading, Zenodo metadata, and PDF rendering.

Zenodo metadata is written to .zenodo.json at each issue's release tag, so Zenodo's GitHub
integration archives that release with the issue's own title, description, and links.
"""
import datetime as dt
import json
import os
import re
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://foikwuogu.github.io/quantum-safe-pipeline-notes/"
SERIES = "Quantum-Safe Pipeline Notes"
TODAY = os.environ.get("RELEASE_AS_OF") or dt.datetime.now(ZoneInfo("America/Chicago")).date().isoformat()


def read_post(p):
    _, fm, body = p.read_text().split("---", 2)
    return yaml.safe_load(fm), body


def all_posts():
    return [(p, *read_post(p)) for p in sorted((ROOT / "posts").glob("*.md"))]


def is_published(meta):
    return meta.get("status") == "published" and str(meta.get("published")) <= TODAY


def write_front_matter_field(path, key, value):
    s = path.read_text()
    head, fm, body = s.split("---", 2)
    if re.search(rf"^{key}:", fm, flags=re.M):
        fm = re.sub(rf"^{key}:.*$", f'{key}: "{value}"', fm, count=1, flags=re.M)
    else:
        fm = re.sub(r"^status: published$", f'status: published\n{key}: "{value}"', fm, count=1, flags=re.M)
    path.write_text("---" + fm + "---" + body)


def references(body):
    """Plain-text reference strings from the post's Sources list."""
    if "**Sources**" not in body:
        return []
    refs = []
    for line in body.split("**Sources**", 1)[1].splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        t = line[2:]
        t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: m.group(1) if m.group(1) == m.group(2) else f"{m.group(1)}. {m.group(2)}", t)
        t = t.replace("**", "").replace("*", "").replace("`", "")
        refs.append(t.strip())
    return refs


def metadata(meta, body, posts):
    authors = json.loads((ROOT / "AUTHORS.json").read_text())
    creators = []
    for a in authors["authors"] + authors.get("collaborators", []):
        c = {"name": f"{a['family']}, {a['given']}", "affiliation": a["affiliation"]}
        if a.get("orcid"):
            c["orcid"] = a["orcid"]
        creators.append(c)
    n = meta["issue"]
    paras = "".join(f"<p>{p.strip()}</p>" for p in meta["summary"].strip().split("\n\n"))
    desc = (paras + f"<p>Issue {n:02d} ({meta['series_slot']} slot) of {SERIES}, a monthly technical blog on "
            "post-quantum cryptography and OT security for U.S. pipelines. Uses public sources only; views are "
            "the author's own and do not represent any employer or client.</p>")
    rel = [
        {"identifier": f"{SITE}#issue-{n}", "relation": "isIdenticalTo", "resource_type": "publication-technicalnote", "scheme": "url"},
        {"identifier": SITE, "relation": "isPartOf", "resource_type": "other", "scheme": "url"},
    ]
    for s in meta.get("supplements") or []:
        rel.append({"identifier": s["url"], "relation": "isSupplementedBy", "resource_type": s.get("type", "software"), "scheme": "url"})
    prev = next((m for _, m, _ in posts if m["issue"] == n - 1 and m.get("doi")), None)
    if prev:
        rel.append({"identifier": prev["doi"], "relation": "continues", "resource_type": "publication-technicalnote", "scheme": "doi"})
    return {
        "upload_type": "publication",
        "publication_type": "technicalnote",
        "title": meta["title"],
        "creators": creators,
        "description": desc,
        "publication_date": str(meta["published"]),
        "access_right": "open",
        "license": "cc-by-4.0",
        "keywords": meta.get("keywords", []),
        "version": f"issue-{n:02d}",
        "language": "eng",
        "related_identifiers": rel,
        "references": references(body),
        "notes": f"Issue {n:02d} of {SERIES}. Text licensed CC BY 4.0. (c) {str(meta['published'])[:4]} Friday Ogochukwu Ikwuogu.",
    }
