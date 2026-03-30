import urllib.request, json, os, re

def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

orcid = "0009-0000-5093-3771"
works = get(f"https://pub.orcid.org/v3.0/{orcid}/works")

for g in works["group"]:
    put_code = g["work-summary"][0]["put-code"]
    d = get(f"https://pub.orcid.org/v3.0/{orcid}/work/{put_code}")

    title = d["title"]["title"]["value"]
    journal = (d.get("journal-title") or {}).get("value", "")
    pub_date = d.get("publication-date") or {}
    year = (pub_date.get("year") or {}).get("value", "2024")
    month = (pub_date.get("month") or {}).get("value", "01")
    wtype = d.get("type", "article")
    doi = next(
        (e["external-id-value"] for e in d["external-ids"]["external-id"] if e["external-id-type"] == "doi"),
        ""
    )
    authors = [
        c["credit-name"]["value"]
        for c in d.get("contributors", {}).get("contributor", [])
        if c.get("credit-name")
    ]

    # Map ORCID type to HugoBlox publication_type
    pub_type_map = {
        "journal-article": "article-journal",
        "preprint": "article",
        "conference-paper": "paper-conference",
    }
    pub_type = pub_type_map.get(wtype, "article-journal")

    # Slug from title
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
    folder = f"content/publications/{slug}"
    os.makedirs(folder, exist_ok=True)

    authors_yaml = "\n".join(f"  - {a}" for a in authors) if authors else "  - Admin"

    content = f"""---
title: '{title}'
authors:
{authors_yaml}
date: '{year}-{month}-01'
doi: '{doi}'
publication_types:
  - '{pub_type}'
publication: '*{journal}*'
---
"""
    path = f"{folder}/index.md"
    with open(path, "w") as f:
        f.write(content)
    print(f"Created: {path}")
    print(f"  Title:   {title}")
    print(f"  Journal: {journal}")
    print(f"  Date:    {year}-{month}")
    print(f"  DOI:     {doi}")
    print()
