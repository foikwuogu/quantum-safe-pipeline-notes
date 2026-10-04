**Status: v0.1.0, released 2026-10-03.** Live at https://foikwuogu.github.io/quantum-safe-pipeline-notes/

# Quantum-Safe Pipeline Notes

A monthly technical blog on post-quantum cryptography and operational-technology (OT) security for U.S. oil and gas pipelines, written by Friday Ogochukwu Ikwuogu (ORCID [0009-0009-2222-1318](https://orcid.org/0009-0009-2222-1318)), Independent Researcher, Odessa, Texas.

One issue per month, beginning with the September 2026 slot.

| Issue | Series slot | Title | File |
|---|---|---|---|
| 01 | September 2026 | What EO 14412 means for a pipeline operator's certificate inventory | `posts/2026-09-eo-14412-certificate-inventory.md` |
| 02 | October 2026 | Harvest-now-decrypt-later for SCADA telemetry | coming October 17, 2026 |

## Repository layout

```
posts/              one Markdown file per issue (front matter: title, slot, issue, published date)
code/compute_stats.py   computes every number quoted in a post -> code/stats.json
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

## Adding a month

Copy a post file, set `issue`, `series_slot`, and `published`, write, remove the matching entry from `PLANNED` in `site/build.py`, and run `python site/build.py --final`.

## License and citation

Posts: CC BY 4.0. Code: MIT. See `LICENSE` and `CITATION.cff`.

Issue 01 (Version 1.0): [10.5281/zenodo.23130001](https://doi.org/10.5281/zenodo.23130001).

Views are the author's own and do not represent any employer or client. All posts use public sources only.
