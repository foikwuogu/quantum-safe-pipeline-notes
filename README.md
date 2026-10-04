**Status: v0.1.0, released 2026-10-03.** Live at https://foikwuogu.github.io/quantum-safe-pipeline-notes/

# Quantum-Safe Pipeline Notes

A monthly technical blog on post-quantum cryptography and operational-technology (OT) security for U.S. oil and gas pipelines, written by Friday Ogochukwu Ikwuogu (ORCID [0009-0009-2222-1318](https://orcid.org/0009-0009-2222-1318)), Independent Researcher, Odessa, Texas.

One issue per month, beginning with the September 2026 slot.

| Issue | Series slot | Title | File |
|---|---|---|---|
| 01 | September 2026 | What EO 14412 means for a pipeline operator's certificate inventory | `posts/2026-09-eo-14412-certificate-inventory.md` · [doi:10.5281/zenodo.23130001](https://doi.org/10.5281/zenodo.23130001) |
| 02 | October 2026 | Harvest-now-decrypt-later for SCADA telemetry | `posts/2026-10-hndl-scada-telemetry.md` · [doi:10.5281/zenodo.23130292](https://doi.org/10.5281/zenodo.23130292) |
| 03 | November 2026 | Finding the cryptography inside an OPC UA deployment | locked until 2026-11-03 |
| 04 | December 2026 | Before the FAR post-quantum rule: what OT vendors should be ready to answer | locked until 2026-12-03 |
| 05 | January 2027 | Hybrid key exchange over narrowband SCADA radio: modeling the cost | locked until 2027-01-03 |
| 06 | February 2027 | Firmware-signing roots and the 2040 problem | locked until 2027-02-03 |
| 07 | March 2027 | What a cryptographic bill of materials should tell a pipeline operator | locked until 2027-03-03 |

## Repository layout

```
posts/              one Markdown file per issue (front matter: title, slot, issue, published date)
code/compute_stats.py   numbers quoted in issue 02 -> code/stats.json
code/radio_model.py     narrowband handshake model for issue 05 -> code/radio_model.json
code/lock_drafts.py     author-only: encrypts drafts/ into scheduled/
code/release_due.py     run daily by GitHub Actions: releases posts whose date has arrived
code/render_pdfs.py     renders pdf/<post>.pdf for each published post
code/release_notes.py   writes RELEASE_NOTES.md; creates a GitHub Release (tag issue-NN) per new issue,
                        with that issue's metadata in .zenodo.json so Zenodo archives it
code/find_dois.py       finds the DOI Zenodo minted for each release and writes it into the post
code/blogkit.py         shared helpers (post loading, Zenodo metadata)
pdf/                PDF of every published post
RELEASE_NOTES.md    release notes for every published issue
scheduled/          encrypted future posts + schedule.json (public titles and dates only)
.github/workflows/publish.yml  builds, releases due posts, deploys GitHub Pages
tools/cert_inventory.py companion tool for issue 01 (X.509 quantum-readiness inventory to CSV)
site/template.html  page design; site/build.py renders posts into site/index.html and docs/index.html
docs/               the published website (GitHub Pages serves this folder)
AUTHORS.json        the single source for author name, ORCID, email, affiliation
```

## Build

```
pip install markdown pyyaml cryptography
python code/compute_stats.py      # numbers used in issue 02
python site/build.py --final      # renders posts/ into docs/index.html (GitHub Pages)
```

## Companion tool

```
python tools/cert_inventory.py ./exported_certs inventory.csv
```

Reads exported certificates only; it never connects to a device.

## Scheduled posts

Future issues are stored encrypted in `scheduled/`. Every day at 11:15 UTC, and on every push, the
workflow in `.github/workflows/publish.yml` decrypts any post whose release date has arrived (Central
time), moves it into `posts/`, rebuilds the site, commits, and deploys. The key is the repository
secret `DRAFTS_KEY`; it is never stored in the repository. Until its date, only a locked post's title
and release date are public.

On release day the same run renders the post's PDF, updates `RELEASE_NOTES.md`, writes the issue's
Zenodo metadata to `.zenodo.json`, and creates a GitHub Release (tag `issue-NN`) at that commit with the
PDF attached. With Zenodo's GitHub integration switched on for this repository, Zenodo archives each new
release (a zip of the repository, including `pdf/`) and mints a DOI. The next daily run finds that DOI on
Zenodo and writes it into the post and the release notes. Issues 01 and 02 are marked `archive: manual`
because their DOIs were created by hand, so they never get a release and are not archived twice.

## Adding a month

To publish immediately: add the post to `posts/` and push. To schedule: put it in `drafts/` (never committed), run `DRAFTS_KEY=... python code/lock_drafts.py`, and push `scheduled/`.

## License and citation

Posts: CC BY 4.0. Code: MIT. See `LICENSE` and `CITATION.cff`.

Views are the author's own and do not represent any employer or client. All posts use public sources only.
