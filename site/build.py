"""Build site/index.html (single self-contained page) from posts/*.md and AUTHORS.json.
Usage: python site/build.py [--final] [--as-of YYYY-MM-DD]
  --final removes the DRAFT banner; posts dated after --as-of (default: today) appear as "coming" entries only."""
import datetime as dt, html, json, re, sys
from pathlib import Path
import markdown, yaml

ROOT = Path(__file__).resolve().parent.parent
FINAL = "--final" in sys.argv
AS_OF = sys.argv[sys.argv.index("--as-of") + 1] if "--as-of" in sys.argv else dt.date.today().isoformat()
authors = json.loads((ROOT / "AUTHORS.json").read_text())
a = authors["authors"][0]

PLANNED = [
    ("November 2026", "Finding the cryptography inside an OPC UA deployment"),
    ("December 2026", "What the FAR post-quantum rule proposal will ask of OT vendors"),
    ("January 2027", "Hybrid key exchange over narrowband SCADA radio: a bench test"),
    ("February 2027", "Firmware-signing roots and the 2040 problem"),
    ("March 2027", "Reading the CISA/NIST CBOM guidance as a pipeline operator"),
]

posts = []
for p in sorted((ROOT / "posts").glob("*.md")):
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
  <span class="entry-meta">{p['minutes']} min read</span></span></a>'''

def planned(i, slot, title):
    return f'''<div class="entry planned"><span class="mp">MP {i:02d}</span>
  <span class="entry-body"><span class="slot">{esc(slot)} · proposed</span>
  <span class="entry-title">{esc(title)}</span></span></div>'''

def article(p):
    pub = p["published"]
    pub_html = f'<mark class="verify">{esc(pub)}</mark>' if "VERIFY" in str(pub) else esc(pub)
    return f'''<article class="post" id="{p['id']}" hidden>
  <a class="back" href="#index" data-go="index">← All issues</a>
  <p class="tag">Issue {p['issue']:02d} · {esc(p['series_slot'])} slot</p>
  <h1>{esc(p['title'])}</h1>
  <p class="byline">{esc(a['name'])} · <span class="mono">ORCID {esc(a['orcid'])}</span> · Published {pub_html} · {p['minutes']} min read</p>
  <div class="prose">{p['html']}</div>
  <p class="license">Text licensed <a target="_blank" rel="noopener" href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. Cite as: {esc(a['name'])}, “{esc(p['title'])},” Quantum-Safe Pipeline Notes, issue {p['issue']}.</p>
</article>'''

def upcoming(p):
    d = dt.date.fromisoformat(str(p["published"]))
    return f'''<div class="entry planned"><span class="mp">MP {p['issue']:02d}</span>
  <span class="entry-body"><span class="slot">{esc(p['series_slot'])} · coming {d.strftime("%B")} {d.day}</span>
  <span class="entry-title">{esc(p['title'])}</span></span></div>'''

is_live = lambda p: "VERIFY" in str(p["published"]) or str(p["published"]) <= AS_OF
live = [p for p in posts if is_live(p)]
soon = [p for p in posts if not is_live(p)]
last = max([p["issue"] for p in posts] or [0])
entries = "\n".join([card(p) for p in live] + [upcoming(p) for p in soon]
                    + [planned(last + 1 + i, s, t) for i, (s, t) in enumerate(PLANNED)])
posts = live
n = len(posts)

page = (ROOT / "site" / "template.html").read_text()
page = (page.replace("{{DRAFT}}", "" if FINAL else '<div class="draft">DRAFT · not yet verified by the author · do not cite</div>')
            .replace("{{ENTRIES}}", entries)
            .replace("{{ARTICLES}}", "\n".join(article(p) for p in posts))
            .replace("{{NAME}}", esc(a["name"]))
            .replace("{{ORCID}}", esc(a["orcid"]))
            .replace("{{EMAIL}}", esc(a["email"]))
            .replace("{{AFFIL}}", esc(a["affiliation"])))
(ROOT / "site" / "index.html").write_text(page)
print(f"built site/index.html with {n} posts, final={FINAL}")

# Standalone copy for GitHub Pages (served from /docs), with a full document skeleton.
standalone = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
              '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
              '<meta name="author" content="' + esc(a["name"]) + '">\n</head>\n<body>\n'
              + page + '\n</body>\n</html>\n')
(ROOT / "docs" / "index.html").write_text(standalone)
print("wrote docs/index.html for GitHub Pages")
