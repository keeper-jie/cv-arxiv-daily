# cv-arxiv-daily

Daily scraping of the latest papers from [arxiv.org](https://arxiv.org) in **cs.CV** (Computer Vision) and **cs.AI** (Artificial Intelligence), automated via GitHub Actions.

## How it works

```
GitHub Action (daily ~01:00 UTC / 09:00 Beijing Time)
  → fetch RSS feed https://rss.arxiv.org/rss/{category}
  → parse title, authors, abstract for each paper
  → save to json/cv-arxiv-daily-YYYY-MM-DD.json
  → generate daily Markdown tables in md/YYYY-MM-DD.md
  → update README with links to all daily entries
```

- **RSS-based** — uses arXiv RSS feeds for stable, structured data (no HTML scraping).
- **Multi-category** — tracks cs.CV and cs.AI; easily extensible via `config.yaml`.
- **Structured JSON** — each date file stores `title`, `authors`, `first_author`, `abstract`, `date`, `url`.
- **Retry & error handling** — HTTP requests include automatic retry with exponential backoff.

## Project structure

```
.
├── daily_arxiv.py              # main scraper script
├── config.yaml                 # configuration (categories, output paths)
├── requirements.txt            # Python dependencies
├── .github/workflows/
│   └── cv-arxiv-daily.yml      # GitHub Actions schedule
├── json/
│   └── cv-arxiv-daily-{date}.json   # daily paper data (auto)
├── md/
│   └── {date}.md                     # daily paper tables (auto)
└── README.md                   # this file + daily paper links
```

## Local development

```bash
# setup
pip install -r requirements.txt

# run
python daily_arxiv.py
```

## Configuration

Edit `config.yaml`:

```yaml
daily_category: true                  # enable category-based scraping
category_list: ["cs.CV", "cs.AI"]     # arXiv categories to track
json_dir: './json'                    # JSON output directory
md_dir: './md'                        # Markdown output directory
```

Add more categories in `category_list` — e.g. `["cs.CV", "cs.AI", "cs.RO"]` — to track additional fields.

## GitHub Actions setup

1. Fork this repo
2. Settings → Actions → General → Workflow permissions → **Read and write permissions**
3. The workflow runs daily at 01:00 UTC (`cron: "0 1 * * *"`). Adjust timezone in `.github/workflows/cv-arxiv-daily.yml` if needed.

<!-- DAILY_PAPERS -->

## Daily Papers

| Date | Papers | Link |
|------|--------|------|
| 2026-09-12 | 273 | [cs.AI](md/2026-09-12.md) |
| 2026-09-11 | 408 | [cs.CV, cs.AI](md/2026-09-11.md) |
| 2026-09-10 | 408 | [cs.CV, cs.AI](md/2026-09-10.md) |
| 2026-09-08 | 174 | [cs.CV](md/2026-09-08.md) |
| 2026-09-07 | 174 | [cs.CV](md/2026-09-07.md) |
| 2026-09-03 | 208 | [cs.CV](md/2026-09-03.md) |
| 2026-09-02 | 227 | [cs.CV](md/2026-09-02.md) |
| 2026-08-31 | 154 | [cs.CV](md/2026-08-31.md) |
| 2026-08-30 | 184 | [cs.CV](md/2026-08-30.md) |
| 2026-08-29 | 184 | [cs.CV](md/2026-08-29.md) |
| 2026-08-28 | 184 | [cs.CV](md/2026-08-28.md) |
| 2026-08-27 | 173 | [cs.CV](md/2026-08-27.md) |
| 2026-08-26 | 194 | [cs.CV](md/2026-08-26.md) |
| 2026-08-24 | 151 | [cs.CV](md/2026-08-24.md) |
| 2026-08-23 | 137 | [cs.CV](md/2026-08-23.md) |
| 2026-08-22 | 137 | [cs.CV](md/2026-08-22.md) |
| 2026-08-21 | 137 | [cs.CV](md/2026-08-21.md) |
| 2026-08-20 | 152 | [cs.CV](md/2026-08-20.md) |
| 2026-08-19 | 171 | [cs.CV](md/2026-08-19.md) |
| 2026-08-18 | 389 | [cs.CV](md/2026-08-18.md) |
| 2026-08-16 | 175 | [cs.CV](md/2026-08-16.md) |
| 2026-08-15 | 175 | [cs.CV](md/2026-08-15.md) |
| 2026-08-14 | 175 | [cs.CV](md/2026-08-14.md) |
| 2026-08-13 | 179 | [cs.CV](md/2026-08-13.md) |
| 2026-08-09 | 207 | [cs.CV](md/2026-08-09.md) |
| 2026-08-08 | 207 | [cs.CV](md/2026-08-08.md) |
| 2026-08-07 | 207 | [cs.CV](md/2026-08-07.md) |
| 2026-08-06 | 208 | [cs.CV](md/2026-08-06.md) |
| 2026-08-05 | 232 | [cs.CV](md/2026-08-05.md) |
| 2026-08-04 | 449 | [cs.CV](md/2026-08-04.md) |
| 2026-08-03 | 153 | [cs.CV](md/2026-08-03.md) |
| 2026-08-02 | 201 | [cs.CV](md/2026-08-02.md) |
| 2026-08-01 | 201 | [cs.CV](md/2026-08-01.md) |
| 2026-07-31 | 201 | [cs.CV](md/2026-07-31.md) |
| 2026-07-30 | 162 | [cs.CV](md/2026-07-30.md) |
| 2026-07-29 | 165 | [cs.CV](md/2026-07-29.md) |
| 2026-07-27 | 110 | [cs.CV](md/2026-07-27.md) |
| 2026-07-26 | 152 | [cs.CV](md/2026-07-26.md) |
| 2026-07-25 | 0 | [Arxiv](md/2026-07-25.md) |
| 2026-07-24 | 152 | [cs.CV](md/2026-07-24.md) |
| 2026-07-23 | 149 | [cs.CV](md/2026-07-23.md) |
| 2026-07-22 | 150 | [cs.CV](md/2026-07-22.md) |
| 2026-07-21 | 332 | [cs.CV](md/2026-07-21.md) |
| 2026-07-20 | 133 | [cs.CV](md/2026-07-20.md) |
| 2026-07-16 | 174 | [cs.CV](md/2026-07-16.md) |
| 2026-07-15 | 178 | [cs.CV](md/2026-07-15.md) |
| 2026-07-14 | 323 | [cs.CV](md/2026-07-14.md) |
| 2026-07-13 | 114 | [cs.CV](md/2026-07-13.md) |
| 2026-07-12 | 151 | [cs.CV](md/2026-07-12.md) |
| 2026-07-11 | 151 | [cs.CV](md/2026-07-11.md) |
| 2026-07-10 | 151 | [cs.CV](md/2026-07-10.md) |
| 2026-07-02 | 271 | [cs.CV](md/2026-07-02.md) |
| 2026-07-01 | 312 | [cs.CV](md/2026-07-01.md) |
| 2026-06-28 | 182 | [cs.CV](md/2026-06-28.md) |
| 2026-06-27 | 182 | [cs.CV](md/2026-06-27.md) |
| 2026-06-26 | 182 | [cs.CV](md/2026-06-26.md) |
| 2026-06-24 | 196 | [cs.CV](md/2026-06-24.md) |
| 2026-06-22 | 179 | [cs.CV](md/2026-06-22.md) |
| 2026-06-21 | 179 | [cs.CV](md/2026-06-21.md) |
| 2026-06-20 | 179 | [cs.CV](md/2026-06-20.md) |
| 2026-06-19 | 179 | [cs.CV](md/2026-06-19.md) |
| 2026-06-18 | 172 | [cs.CV](md/2026-06-18.md) |
| 2026-06-17 | 179 | [cs.CV](md/2026-06-17.md) |
| 2026-06-14 | 161 | [cs.CV](md/2026-06-14.md) |
| 2026-06-13 | 161 | [cs.CV](md/2026-06-13.md) |
| 2026-06-12 | 161 | [cs.CV](md/2026-06-12.md) |
| 2026-06-11 | 179 | [cs.CV](md/2026-06-11.md) |
| 2026-06-10 | 176 | [cs.CV](md/2026-06-10.md) |
| 2026-06-09 | 413 | [cs.CV](md/2026-06-09.md) |
| 2026-06-08 | 168 | [cs.CV](md/2026-06-08.md) |
| 2026-06-07 | 199 | [cs.CV](md/2026-06-07.md) |
| 2026-06-06 | 199 | [cs.CV](md/2026-06-06.md) |
| 2026-06-05 | 199 | [cs.CV](md/2026-06-05.md) |
| 2026-05-31 | 261 | [cs.CV](md/2026-05-31.md) |
| 2026-05-30 | 261 | [cs.CV](md/2026-05-30.md) |
| 2026-05-29 | 261 | [cs.CV](md/2026-05-29.md) |

