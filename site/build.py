"""Build site/index.html (single self-contained page) from posts/*.md and AUTHORS.json.
Usage: python site/build.py [--final] [--as-of YYYY-MM-DD] [--include-drafts]
  --final           removes the DRAFT banner
  --as-of           date used to decide what is live (default: today in America/Chicago)
  --include-drafts  private preview only: also renders drafts/ as if released (never use for docs/)
Locked posts appear as "coming" entries from scheduled/schedule.json (title and date only)."""
import datetime as dt, html, json, re, sys
from pathlib import Path
import markdown, yaml

ROOT = Path(__file__).resolve().parent.parent
FINAL = "--final" in sys.argv
from zoneinfo import ZoneInfo
AS_OF = (sys.argv[sys.argv.index("--as-of") + 1] if "--as-of" in sys.argv
         else dt.datetime.now(ZoneInfo("America/Chicago")).date().isoformat())
PREVIEW = "--include-drafts" in sys.argv
authors = json.loads((ROOT / "AUTHORS.json").read_text())
a = authors["authors"][0]

PLANNED = []  # (series_slot, title) for topics not yet drafted

posts = []
sources = sorted((ROOT / "posts").glob("*.md")) + (sorted((ROOT / "drafts").glob("*.md")) if PREVIEW else [])
for p in sources:
    raw = p.read_text()
    _, fm, body = raw.split("---", 2)
    meta = yaml.safe_load(fm)
    body = re.sub(r"^# .*\n", "", body.strip(), count=1)  # title rendered separately
    h = markdown.markdown(body, extensions=["tables", "sane_lists"])
    h = h.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")
    h = h.replace("[VERIFY", '<mark class="verify">[VERIFY').replace("]</mark>", "]")
    h = re.sub(r'(<mark class="verify">\[VERIFY[^\]]*\])', r"\1</mark>", h)
    h = h.replace("<a href=", '<a target="_blank" rel="noopener" href=')
    words = len(re.findall(r"\w+", body))
    posts.append(dict(meta, id=f"issue-{meta['issue']}", html=h, minutes=max(1, round(words / 220))))

def esc(s): return html.escape(str(s))

def card(p):
    return f'''<a class="entry" href="#{p['id']}" data-go="{p['id']}">
  <span class="mp">MP {p['issue']:02d}</span>
  <span class="entry-body"><span class="slot">{esc(p['series_slot'])}</span>
  <span class="entry-title">{esc(p['title'])}</span>
  <span class="entry-meta">{p['minutes']} min read{" · DOI " + esc(p["doi"]) if p.get("doi") else ""}</span></span></a>'''

def planned(i, slot, title):
    return f'''<div class="entry planned"><span class="mp">MP {i:02d}</span>
  <span class="entry-body"><span class="slot">{esc(slot)} · proposed</span>
  <span class="entry-title">{esc(title)}</span></span></div>'''

def doi_html(p):
    d = p.get("doi")
    if not d: return ""
    return f'<p class="license">DOI: <a target="_blank" rel="noopener" href="https://doi.org/{esc(d)}">https://doi.org/{esc(d)}</a> (archived on Zenodo)</p>'

def doi_cite(p):
    d = p.get("doi")
    return f", https://doi.org/{esc(d)}" if d else ""

def article(p):
    pub = p["published"]
    pub_html = f'<mark class="verify">{esc(pub)}</mark>' if "VERIFY" in str(pub) else esc(pub)
    return f'''<article class="post" id="{p['id']}" hidden>
  <a class="back" href="#index" data-go="index">← All issues</a>
  <p class="tag">Issue {p['issue']:02d} · {esc(p['series_slot'])} slot</p>
  <h1>{esc(p['title'])}</h1>
  <p class="byline">{esc(a['name'])} · <span class="mono">ORCID {esc(a['orcid'])}</span> · Published {pub_html} · {p['minutes']} min read</p>
  <div class="prose">{p['html']}</div>
  {doi_html(p)}
  <p class="license">Text licensed <a target="_blank" rel="noopener" href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. Cite as: {esc(a['name'])}, “{esc(p['title'])},” Quantum-Safe Pipeline Notes, issue {p['issue']}{doi_cite(p)}.</p>
</article>'''

def upcoming(p):
    d = dt.date.fromisoformat(str(p["published"]))
    yr = f", {d.year}" if d.year != dt.date.fromisoformat(AS_OF).year else ""
    return f'''<div class="entry planned"><span class="mp">MP {p['issue']:02d}</span>
  <span class="entry-body"><span class="slot">{esc(p['series_slot'])} · coming {d.strftime("%B")} {d.day}{yr}</span>
  <span class="entry-title">{esc(p['title'])}</span></span></div>'''

is_live = lambda p: "VERIFY" in str(p["published"]) or str(p["published"]) <= AS_OF
live = [p for p in posts if is_live(p)]
soon = [p for p in posts if not is_live(p)]
sched = ROOT / "scheduled" / "schedule.json"
if sched.exists() and not PREVIEW:
    have = {p["issue"] for p in posts}
    for e in json.loads(sched.read_text()):
        if e["issue"] not in have:
            soon.append({"issue": e["issue"], "series_slot": e["series_slot"],
                         "title": e["title"], "published": e["release_date"]})
soon.sort(key=lambda p: p["issue"])
last = max([p["issue"] for p in posts + soon] or [0])
entries = "\n".join([card(p) for p in live] + [upcoming(p) for p in soon]
                    + [planned(last + 1 + i, s, t) for i, (s, t) in enumerate(PLANNED)])
posts = live
n = len(posts)

page = (ROOT / "site" / "template.html").read_text()
banner = ('<div class="draft">Private preview · issues 03 to 07 are locked until their release dates</div>' if PREVIEW
          else "" if FINAL else '<div class="draft">DRAFT · not yet verified by the author · do not cite</div>')
page = (page.replace("{{DRAFT}}", banner)
            .replace("{{ENTRIES}}", entries)
            .replace("{{ARTICLES}}", "\n".join(article(p) for p in posts))
            .replace("{{NAME}}", esc(a["name"]))
            .replace("{{ORCID}}", esc(a["orcid"]))
            .replace("{{EMAIL}}", esc(a["email"]))
            .replace("{{AFFIL}}", esc(a["affiliation"])))
(ROOT / "site" / "index.html").write_text(page)
print(f"built site/index.html with {n} posts, final={FINAL}")

if PREVIEW:
    sys.exit(0)  # never write a preview with unreleased drafts into docs/

# Standalone copy for GitHub Pages (served from /docs), with a full document skeleton.
standalone = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
              '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
              '<meta name="author" content="' + esc(a["name"]) + '">\n</head>\n<body>\n'
              + page + '\n</body>\n</html>\n')
(ROOT / "docs" / "index.html").write_text(standalone)
print("wrote docs/index.html for GitHub Pages")
