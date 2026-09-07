# cmlakhan.github.io

Personal academic website of Chirag M. Lakhani, built with [Quarto](https://quarto.org) and published to GitHub Pages.

## Structure

| File | What it is |
|---|---|
| `index.qmd` | Home page: About Me + research interests |
| `publications.qmd` | Publications page (content generated from `_data/publications.yml`) |
| `software.qmd` | Released software tools |
| `reading-list.qmd` | Reading list (content generated from `_data/reading_list.bib`) |
| `_data/publications.yml` | Publication entries — edit this to add/update papers |
| `_data/reading_list.bib` | Reading list BibTeX — paste entries here, with `category`/`subcategory` fields |
| `scripts/build_content.py` | Generates the publication and reading-list markdown at render time |
| `_quarto.yml` | Site config: navbar, theme, deploy settings |
| `styles.css` | Custom styling |
| `assets/` | Headshot, favicons, CV PDFs |
| `_old_jekyll/` | The previous Jekyll site, archived — safe to delete |

## How to update

1. Edit the relevant file (see table above). For a new paper, add an entry to `_data/publications.yml` under `preprints:` or `published:`. For a reading-list paper, paste its BibTeX into `_data/reading_list.bib` and add `category = {...}` and `subcategory = {...}` fields.
2. Preview locally (optional): `quarto preview`
3. Commit and push to `main`. GitHub Actions renders the site and publishes it to the `gh-pages` branch automatically.

## Adding a new page

Create `mypage.qmd` with a YAML header (`title: "..."`), write markdown, and add it to the `navbar` section of `_quarto.yml`. Jupyter notebooks (`.ipynb`) can also be added as pages and will render with their outputs.
