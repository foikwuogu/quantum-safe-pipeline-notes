"""Render a PDF of each published post into pdf/<post-name>.pdf (skips ones that exist).

  python code/render_pdfs.py --pending   exit 0 if any published post has no PDF yet, 1 otherwise
  python code/render_pdfs.py             render the missing PDFs from docs/index.html

The PDFs are committed, so each GitHub Release (and the Zenodo archive made from it) contains them.
Needs Playwright with Chromium: pip install playwright && python -m playwright install chromium
"""
import sys

from blogkit import ROOT, all_posts, is_published

OUT = ROOT / "pdf"


def missing():
    return [(p, m) for p, m, _ in all_posts() if is_published(m) and not (OUT / f"{p.stem}.pdf").exists()]


def render(issue, out_pdf):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.goto((ROOT / "docs" / "index.html").as_uri())
        pg.wait_for_load_state("networkidle")
        pg.evaluate("""(id) => {
            document.querySelectorAll('main#index, article.post, .draft, .back').forEach(e => e.hidden = true);
            document.getElementById(id).hidden = false;
        }""", f"issue-{issue}")
        pg.emulate_media(color_scheme="light")
        pg.pdf(path=str(out_pdf), format="Letter", print_background=True,
               margin={"top": "0.7in", "bottom": "0.7in", "left": "0.7in", "right": "0.7in"})
        b.close()


if __name__ == "__main__":
    todo = missing()
    if "--pending" in sys.argv:
        sys.exit(0 if todo else 1)
    OUT.mkdir(exist_ok=True)
    for p, m in todo:
        render(m["issue"], OUT / f"{p.stem}.pdf")
        print(f"rendered pdf/{p.stem}.pdf")
    if not todo:
        print("all published posts have PDFs")
