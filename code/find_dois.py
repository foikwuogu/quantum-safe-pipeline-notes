"""Look up the DOI Zenodo minted for each released issue and write it into the post.

Zenodo's GitHub integration archives a release a few minutes after it is created, so the DOI
is not known in the same run. Each daily run searches Zenodo's public records (no token needed)
for published issues that have no `doi:` yet, matching the exact title and the author's surname.
"""
import requests

from blogkit import all_posts, is_published, write_front_matter_field

SURNAME = "Ikwuogu"


def lookup(title):
    r = requests.get("https://zenodo.org/api/records",
                     params={"q": f'title:"{title}"', "size": 25, "sort": "mostrecent"}, timeout=60)
    r.raise_for_status()
    for hit in r.json().get("hits", {}).get("hits", []):
        md = hit.get("metadata", {})
        names = " ".join(c.get("name", "") or c.get("person_or_org", {}).get("name", "") for c in md.get("creators", []))
        if md.get("title") == title and SURNAME in names:
            return hit.get("doi") or hit.get("pids", {}).get("doi", {}).get("identifier")
    return None


if __name__ == "__main__":
    for p, m, _ in all_posts():
        if not is_published(m) or m.get("doi"):
            continue
        try:
            doi = lookup(m["title"])
        except Exception as e:  # network trouble should not block the site build
            print(f"issue {m['issue']:02d}: Zenodo lookup failed ({e}); will retry tomorrow")
            continue
        if doi:
            write_front_matter_field(p, "doi", doi)
            print(f"issue {m['issue']:02d}: DOI {doi}")
        else:
            print(f"issue {m['issue']:02d}: no Zenodo record yet")
