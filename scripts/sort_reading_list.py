#!/usr/bin/env python3
"""Read reading_list_input.yml, merge/sort/deduplicate, write to reading_list.yml."""

import yaml
from pathlib import Path
from collections import OrderedDict


def merge_and_sort(data):
    if not data or "categories" not in data:
        return {"categories": []}

    # Merge duplicate categories by name
    cat_map = OrderedDict()
    for category in data["categories"]:
        name = category.get("name", "")
        if name not in cat_map:
            cat_map[name] = {"name": name, "subcategories": []}
        cat_map[name]["subcategories"].extend(category.get("subcategories") or [])

    # Merge duplicate subcategories within each category
    for cat in cat_map.values():
        sub_map = OrderedDict()
        for sub in cat["subcategories"]:
            name = sub.get("name", "")
            if name not in sub_map:
                sub_map[name] = {"name": name, "papers": []}
            sub_map[name]["papers"].extend(sub.get("papers") or [])

        # Deduplicate papers by title and sort
        for sub in sub_map.values():
            seen = {}
            unique = []
            for paper in sub["papers"]:
                title = paper.get("title", "")
                if title not in seen:
                    seen[title] = True
                    unique.append(paper)
            sub["papers"] = sorted(unique, key=lambda p: p.get("title", "").lower())

        cat["subcategories"] = sorted(sub_map.values(), key=lambda s: s.get("name", "").lower())

    data["categories"] = sorted(cat_map.values(), key=lambda c: c.get("name", "").lower())
    return data


if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent / "_data"
    input_file = base / "reading_list_input.yml"
    output_file = base / "reading_list.yml"

    with open(input_file, "r") as f:
        raw = yaml.safe_load(f)

    # Support both formats: bare list or dict with "categories" key
    if isinstance(raw, list):
        data = {"categories": raw}
    elif isinstance(raw, dict) and "categories" in raw:
        data = raw
    else:
        data = {"categories": []}

    data = merge_and_sort(data)

    with open(output_file, "w") as f:
        f.write("# AUTO-GENERATED from reading_list_input.yml — do not edit manually\n")
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"Sorted {input_file} -> {output_file}")
