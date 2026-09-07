#!/usr/bin/env python3
"""Generate markdown for the publications and reading-list pages.

Inputs:
    _data/publications.yml   (hand-edited)
    _data/reading_list.bib   (hand-edited BibTeX; category/subcategory fields control grouping)
Outputs (gitignored, rebuilt on every `quarto render` via the pre-render hook):
    _generated/publications.md
    _generated/reading-list.md
"""

import html
import re
import yaml
from collections import OrderedDict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "_data"
OUT = BASE / "_generated"

NAME_PATTERN = re.compile(r"Chirag\s+M\.?\s+Lakhani|Chirag\s+Lakhani")


def bold_name(authors: str) -> str:
    return NAME_PATTERN.sub(lambda m: f"<strong>{m.group(0)}</strong>", authors)


def render_entry(entry: dict) -> str:
    """Render one publication/reading-list entry as an HTML block."""
    parts = ['<div class="pub-entry">']

    title = html.escape(entry.get("title", ""))
    link = entry.get("link", "")
    if link:
        parts.append(f'<div class="pub-title"><a href="{link}">{title}</a></div>')
    else:
        parts.append(f'<div class="pub-title">{title}</div>')

    authors = entry.get("authors", "")
    if authors:
        parts.append(f'<div class="pub-authors">{bold_name(html.escape(authors))}</div>')

    venue = entry.get("venue", "")
    if venue:
        parts.append(f'<div class="pub-venue">{html.escape(venue)}</div>')

    summary = entry.get("summary", "")
    if summary:
        parts.append(f'<div class="pub-summary">{html.escape(summary)}</div>')

    buttons = []
    if link:
        buttons.append(f'<a class="pub-btn" href="{link}" target="_blank">Paper</a>')
    if entry.get("code"):
        buttons.append(f'<a class="pub-btn" href="{entry["code"]}" target="_blank">Code</a>')
    if entry.get("page"):
        buttons.append(f'<a class="pub-btn" href="{entry["page"]}" target="_blank">Project Page</a>')
    if buttons:
        parts.append('<div class="pub-links">' + " ".join(buttons) + "</div>")

    if entry.get("press"):
        parts.append(f'<div class="pub-press">{entry["press"]}</div>')

    parts.append("</div>")
    return "\n".join(parts)


# ---------------------------------------------------------------- publications

SECTIONS = [
    ("preprints", "Preprints Under Review", None),
    ("published", "Peer-Reviewed Publications", None),
    ("earlier", "Earlier Work", "From my doctoral training in mathematics."),
]


def build_publications() -> str:
    data = yaml.safe_load((DATA / "publications.yml").read_text())
    blocks = []
    for key, heading, note in SECTIONS:
        entries = data.get(key) or []
        if not entries:
            continue
        blocks.append(f"## {heading}\n")
        if note:
            blocks.append(f'<div class="pub-section-note">{html.escape(note)}</div>\n')
        for entry in entries:
            blocks.append(render_entry(entry) + "\n")
    return "\n".join(blocks)


# ---------------------------------------------------------------- reading list


def parse_bib(text):
    """Robust BibTeX parser that handles messy real-world entries."""
    entries = []
    entry_starts = list(re.finditer(r"@(\w+)\s*\{", text))

    for start_match in entry_starts:
        pos = start_match.end()
        depth = 1
        while pos < len(text) and depth > 0:
            if text[pos] == "{":
                depth += 1
            elif text[pos] == "}":
                depth -= 1
            pos += 1
        if depth != 0:
            continue

        block = text[start_match.end() : pos - 1]
        comma_pos = block.find(",")
        if comma_pos == -1:
            continue
        body = block[comma_pos + 1 :]

        entry = {}
        field_pattern = re.compile(r"([\w-]+)\s*=\s*")
        pos = 0
        while pos < len(body):
            field_match = field_pattern.search(body, pos)
            if not field_match:
                break
            key = field_match.group(1).strip().lower()
            val_start = field_match.end()
            while val_start < len(body) and body[val_start] in " \t\n\r":
                val_start += 1
            if val_start >= len(body):
                break

            if body[val_start] == "{":
                depth = 1
                val_end = val_start + 1
                while val_end < len(body) and depth > 0:
                    if body[val_end] == "{":
                        depth += 1
                    elif body[val_end] == "}":
                        depth -= 1
                    val_end += 1
                value = body[val_start + 1 : val_end - 1]
                pos = val_end
            elif body[val_start] == '"':
                val_end = body.index('"', val_start + 1)
                value = body[val_start + 1 : val_end]
                pos = val_end + 1
            else:
                val_end = val_start
                while val_end < len(body) and body[val_end] not in ",\n}":
                    val_end += 1
                value = body[val_start:val_end].strip()
                pos = val_end

            value = re.sub(r"\s+", " ", value).strip()
            value = re.sub(r"\{([^{}]*)\}", r"\1", value)
            entry[key] = value

        if entry.get("title"):
            entries.append(entry)

    return entries


def format_authors(author_str):
    if not author_str:
        return ""
    authors = [a.strip() for a in author_str.split(" and ")]
    formatted = []
    for author in authors:
        if "," in author:
            parts = [p.strip() for p in author.split(",", 1)]
            formatted.append(f"{parts[1]} {parts[0]}" if len(parts) == 2 else author)
        else:
            formatted.append(author)
    return ", ".join(formatted)


def format_venue(entry):
    venue = entry.get("journal") or entry.get("booktitle") or ""
    year = entry.get("year", "")
    if venue and year:
        return f"{venue}, {year}"
    return venue or year


def build_reading_list() -> str:
    text = (DATA / "reading_list.bib").read_text()
    raw_entries = parse_bib(text)

    cat_map = OrderedDict()
    for entry in raw_entries:
        cat = entry.get("category", "Uncategorized")
        sub = entry.get("subcategory", "General")
        link = entry.get("url", "")
        if not link and entry.get("doi"):
            doi = entry["doi"]
            link = doi if doi.startswith("http") else f"https://doi.org/{doi}"
        paper = {
            "title": entry.get("title", ""),
            "authors": format_authors(entry.get("author", "")),
            "venue": format_venue(entry),
            "link": link,
        }
        if entry.get("code"):
            paper["code"] = entry["code"]
        cat_map.setdefault(cat, OrderedDict()).setdefault(sub, [])
        cat_map[cat][sub].append(paper)

    blocks = []
    for cat in sorted(cat_map, key=str.lower):
        blocks.append(f"## {cat}\n")
        for sub in sorted(cat_map[cat], key=str.lower):
            blocks.append(f"### {sub}\n")
            seen = set()
            papers = [p for p in cat_map[cat][sub] if not (p["title"] in seen or seen.add(p["title"]))]
            for paper in sorted(papers, key=lambda p: p["title"].lower()):
                blocks.append(render_entry(paper) + "\n")
    return "\n".join(blocks)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "publications.md").write_text(build_publications())
    (OUT / "reading-list.md").write_text(build_reading_list())
    print(f"Wrote {OUT / 'publications.md'} and {OUT / 'reading-list.md'}")
