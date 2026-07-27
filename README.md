# cv-arxiv-daily

Daily scraping of the latest Computer Vision papers from [arxiv.org](https://arxiv.org), automated via GitHub Actions.

## How it works

```
GitHub Action (daily 9:00 UTC)
  → scrape https://arxiv.org/list/cs.CV/new
  → extract title, authors, abstract for each paper
  → save to docs/cv-arxiv-daily-YYYY-MM-DD.json
  → merge all dates → generate Markdown tables below
```

- **No API key required** — parses the HTML listing page directly, avoiding ArXiv API rate limits.
- **Structured JSON** — each date file stores `title`, `authors`, `first_author`, `abstract`, `date`, `url`.
- **Incremental** — README is regenerated from all historical date JSONs on each run.

## Project structure

```
.
├── daily_arxiv.py              # main scraper script
├── config.yaml                 # configuration
├── requirements.txt            # Python dependencies
├── .github/workflows/
│   └── cv-arxiv-daily.yml      # GitHub Actions schedule
├── docs/
│   ├── cv-arxiv-daily-{date}.json      # daily paper data (auto)
│   ├── cv-arxiv-daily-web-{date}.json  # web format (auto)
│   └── index.md                        # GitHub Pages output (auto)
└── README.md                   # this file + daily paper tables
```

## Local development

```bash
# setup
python3 -m venv venv
venv/bin/pip install -r requirements.txt

# run
venv/bin/python daily_arxiv.py
```

## Configuration

Edit `config.yaml`:

```yaml
daily_category: true            # enable category-based scraping
category_list: ["cs.CV"]        # arXiv categories to track
publish_readme: true            # update README.md
publish_gitpage: true           # update docs/index.md
```

Add more categories in `category_list` — e.g. `["cs.CV", "cs.RO", "cs.AI"]` — to track multiple fields.

## GitHub Actions setup

1. Fork this repo
2. Settings → Actions → General → Workflow permissions → **Read and write permissions**
3. The workflow runs daily at 9:00 UTC (`cron: "0 9 * * *"`). Adjust timezone in `.github/workflows/cv-arxiv-daily.yml` if needed.

<!-- DAILY_PAPERS -->

## Daily Papers

| Date | Papers | Link |
|------|--------|------|
| 2026-07-27 | 110 | [cs.CV](md/2026-07-27.md) |
| 2026-07-26 | 152 | [cs.CV](md/2026-07-26.md) |
| 2026-07-25 | 0 | [cs.CV](md/2026-07-25.md) |
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

