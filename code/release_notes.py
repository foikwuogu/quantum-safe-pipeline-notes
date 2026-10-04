"""Write release notes and create a GitHub Release for each newly published issue.

  python code/release_notes.py            writes RELEASE_NOTES.md (all published issues, newest first)
  python code/release_notes.py --github   for each published issue without a release (tag issue-NN):
                                            1. writes .zenodo.json with that issue's metadata,
                                            2. commits and pushes it,
                                            3. creates the GitHub Release at that commit, with the
                                               release notes and the issue's PDF attached.
                                          With Zenodo's GitHub integration switched on for this
                                          repository, Zenodo archives the release and mints its DOI.
                                          Existing releases only get their notes refreshed.

Issues marked `archive: manual` (01 and 02, whose DOIs were made by hand) never get a release,
so they are not archived twice. Locked issues are not included until they are released.
"""
import json
import subprocess
import sys

from blogkit import ROOT, all_posts, is_published, metadata

REPO = "https://github.com/foikwuogu/quantum-safe-pipeline-notes"
SITE = "https://foikwuogu.github.io/quantum-safe-pipeline-notes/"
AUTHOR = "Friday Ogochukwu Ikwuogu"


def notes(p, m, level="##"):
    n, doi = m["issue"], m.get("doi")
    out = [f"{level} Issue {n:02d}: {m['title']}", "",
           f"**Series slot:** {m['series_slot']}  ",
           f"**Published:** {m['published']}  ",
           f"**Read it:** {SITE}#issue-{n}  ",
           f"**Archived:** https://doi.org/{doi}  " if doi else "**Archived:** Zenodo DOI pending (added automatically once minted)  ",
           f"**PDF:** [`pdf/{p.stem}.pdf`]({REPO}/blob/main/pdf/{p.stem}.pdf)  ",
           f"**Source:** [`posts/{p.name}`]({REPO}/blob/main/posts/{p.name})", "",
           m.get("summary", "").strip(), ""]
    sup = m.get("supplements") or []
    if sup:
        out += ["**Companion code:** " + ", ".join(f"[`{s['url'].split('/main/')[-1]}`]({s['url']})" for s in sup), ""]
    cite = f"{AUTHOR}, \"{m['title']},\" Quantum-Safe Pipeline Notes, issue {n}, {str(m['published'])[:4]}."
    if doi:
        cite = cite[:-1] + f". https://doi.org/{doi}"
    out += [f"**Cite as:** {cite}", "", "License: text CC BY 4.0; code MIT.", ""]
    return "\n".join(out)


def run(*cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"{' '.join(cmd)} failed: {r.stderr.strip()}")
    return r


def main():
    posts = all_posts()
    published = sorted([t for t in posts if is_published(t[1])], key=lambda t: t[1]["issue"])
    body = ["# Release notes", "",
            "Quantum-Safe Pipeline Notes: one issue per month on post-quantum cryptography and OT security "
            "for U.S. pipelines. Each issue is released on its date and archived on Zenodo with its own DOI.", ""]
    body += [notes(p, m) for p, m, _ in reversed(published)]
    (ROOT / "RELEASE_NOTES.md").write_text("\n".join(body))
    print(f"RELEASE_NOTES.md: {len(published)} issues")

    if "--github" not in sys.argv:
        return
    for p, m, b in published:
        tag = f"issue-{m['issue']:02d}"
        title = f"Issue {m['issue']:02d}: {m['title']}"
        nf = ROOT / f".release-{tag}.md"
        nf.write_text(notes(p, m, level="###"))
        try:
            if run("gh", "release", "view", tag, check=False).returncode == 0:
                run("gh", "release", "edit", tag, "--title", title, "--notes-file", str(nf))
                print(f"refreshed notes for {tag}")
                continue
            if m.get("archive") == "manual":
                print(f"{tag}: archived by hand, no release created")
                continue
            # Metadata Zenodo reads from the tagged commit.
            (ROOT / ".zenodo.json").write_text(json.dumps(metadata(m, b, posts), indent=2) + "\n")
            run("git", "add", ".zenodo.json")
            if run("git", "diff", "--cached", "--quiet", check=False).returncode != 0:
                run("git", "commit", "-m", f"Zenodo metadata for {tag}")
                run("git", "push")
            sha = run("git", "rev-parse", "HEAD").stdout.strip()
            args = ["gh", "release", "create", tag, "--target", sha, "--title", title,
                    "--notes-file", str(nf), "--latest"]
            pdf = ROOT / "pdf" / f"{p.stem}.pdf"
            if pdf.exists():
                args.append(str(pdf))
            run(*args)
            print(f"created release {tag} at {sha[:7]}")
        finally:
            nf.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
