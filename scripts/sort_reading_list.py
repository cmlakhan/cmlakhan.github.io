#!/usr/bin/env python3
"""Parse reading_list.bib, group by category/subcategory, sort, write to reading_list.yml."""

import re
import yaml
from pathlib import Path
from collections import OrderedDict


def parse_bib(text):
    """Robust BibTeX parser that handles messy real-world entries.

    Handles:
    - Missing commas between fields
    - Nested braces in values (e.g., abstracts, titles with {DNA})
    - Both {braced} and "quoted" values
    - Whitespace-separated keys with spaces/tabs (e.g., @article {key, ...)
    - Fields like elocation-id with hyphens
    """
    entries = []

    # Find each entry: @type{key, ...} or @type{key, ...}
    # We need to handle nested braces, so we can't use a simple regex for the whole block
    entry_starts = list(re.finditer(r'@(\w+)\s*\{', text))

    for i, start_match in enumerate(entry_starts):
        # Find the matching closing brace by counting brace depth
        pos = start_match.end()
        depth = 1
        while pos < len(text) and depth > 0:
            if text[pos] == '{':
                depth += 1
            elif text[pos] == '}':
                depth -= 1
            pos += 1

        if depth != 0:
            continue

        block = text[start_match.end():pos - 1]  # content between outer braces

        # Skip the citation key (everything before the first comma)
        comma_pos = block.find(',')
        if comma_pos == -1:
            continue
        body = block[comma_pos + 1:]

        entry = {}
        # Parse fields by finding key = value patterns
        # Value can be {braced} (with nesting), "quoted", or bare word/number
        field_pattern = re.compile(
            r'([\w-]+)\s*=\s*'  # field name (allows hyphens like elocation-id)
        )

        pos = 0
        while pos < len(body):
            field_match = field_pattern.search(body, pos)
            if not field_match:
                break

            key = field_match.group(1).strip().lower()
            val_start = field_match.end()

            # Skip whitespace
            while val_start < len(body) and body[val_start] in ' \t\n\r':
                val_start += 1

            if val_start >= len(body):
                break

            # Parse the value
            if body[val_start] == '{':
                # Braced value — find matching close brace
                depth = 1
                val_end = val_start + 1
                while val_end < len(body) and depth > 0:
                    if body[val_end] == '{':
                        depth += 1
                    elif body[val_end] == '}':
                        depth -= 1
                    val_end += 1
                value = body[val_start + 1:val_end - 1]
                pos = val_end
            elif body[val_start] == '"':
                # Quoted value
                val_end = body.index('"', val_start + 1)
                value = body[val_start + 1:val_end]
                pos = val_end + 1
            else:
                # Bare value (number, month name, etc.)
                val_end = val_start
                while val_end < len(body) and body[val_end] not in ',\n}':
                    val_end += 1
                value = body[val_start:val_end].strip()
                pos = val_end

            # Clean up value: collapse whitespace
            value = re.sub(r'\s+', ' ', value).strip()
            # Remove inner protective braces (e.g., {DNA} -> DNA)
            value = re.sub(r'\{([^{}]*)\}', r'\1', value)

            entry[key] = value

        if entry.get('title'):
            entries.append(entry)

    return entries


def format_authors(author_str):
    """Convert BibTeX author string to readable format.

    Handles both formats:
    - "First Last and First Last"
    - "Last, First and Last, First"
    """
    if not author_str:
        return ''

    authors = [a.strip() for a in author_str.split(' and ')]
    formatted = []
    for author in authors:
        if ',' in author:
            # "Last, First M." -> "First M. Last"
            parts = [p.strip() for p in author.split(',', 1)]
            if len(parts) == 2:
                formatted.append(f"{parts[1]} {parts[0]}")
            else:
                formatted.append(author)
        else:
            formatted.append(author)
    return ', '.join(formatted)


def format_venue(entry):
    """Build venue string from journal/booktitle and year."""
    venue = entry.get('journal') or entry.get('booktitle') or ''
    year = entry.get('year', '')
    if venue and year:
        return f"{venue}, {year}"
    return venue or year


def build_yaml(entries):
    """Group entries by category/subcategory, sort, deduplicate."""
    cat_map = OrderedDict()

    for entry in entries:
        cat_name = entry.get('category', 'Uncategorized')
        sub_name = entry.get('subcategory', 'General')

        if cat_name not in cat_map:
            cat_map[cat_name] = OrderedDict()
        if sub_name not in cat_map[cat_name]:
            cat_map[cat_name][sub_name] = []

        link = entry.get('url', '')
        if not link and entry.get('doi'):
            doi = entry['doi']
            if doi.startswith('http'):
                link = doi
            else:
                link = f"https://doi.org/{doi}"

        paper = {
            'title': entry.get('title', ''),
            'authors': format_authors(entry.get('author', '')),
            'venue': format_venue(entry),
            'link': link,
        }

        # Optional fields
        if entry.get('code'):
            paper['code'] = entry['code']
        if entry.get('notes'):
            paper['notes'] = entry['notes']

        cat_map[cat_name][sub_name].append(paper)

    # Build sorted structure
    categories = []
    for cat_name in sorted(cat_map.keys(), key=str.lower):
        subcategories = []
        for sub_name in sorted(cat_map[cat_name].keys(), key=str.lower):
            # Deduplicate by title
            seen = {}
            unique = []
            for p in cat_map[cat_name][sub_name]:
                if p['title'] not in seen:
                    seen[p['title']] = True
                    unique.append(p)
            papers = sorted(unique, key=lambda p: p['title'].lower())
            subcategories.append({'name': sub_name, 'papers': papers})
        categories.append({'name': cat_name, 'subcategories': subcategories})

    return {'categories': categories}


if __name__ == '__main__':
    base = Path(__file__).resolve().parent.parent / '_data'
    input_file = base / 'reading_list.bib'
    output_file = base / 'reading_list.yml'

    text = input_file.read_text()
    entries = parse_bib(text)
    data = build_yaml(entries)

    with open(output_file, 'w') as f:
        f.write('# AUTO-GENERATED from reading_list.bib — do not edit manually\n')
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"Parsed {len(entries)} entries from {input_file} -> {output_file}")
