import os
import re
import json
import glob
import yaml
import logging
import argparse
import datetime
import xml.etree.ElementTree as ET

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(format='[%(asctime)s %(levelname)s] %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)

ARXIV_BASE = "http://arxiv.org/"
RSS_URL_TEMPLATE = "https://rss.arxiv.org/rss/{category}"

NS = {
    'dc': 'http://purl.org/dc/elements/1.1/',
    'arxiv': 'http://arxiv.org/schemas/atom',
}


def _make_session(retries=3, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504)):
    session = requests.Session()
    retry = Retry(total=retries, backoff_factor=backoff_factor,
                  status_forcelist=status_forcelist, raise_on_status=False)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session


def load_config(config_file: str) -> dict:
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    if 'keywords' not in config:
        config['kv'] = {}
    logging.info(f'config = {config}')
    return config


def fetch_rss(session, category):
    url = RSS_URL_TEMPLATE.format(category=category)
    logging.info(f"Fetching RSS: {url}")
    resp = session.get(url, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"RSS request failed with status {resp.status_code}: {url}")
    return resp.text


def parse_rss_date(rss_xml):
    channel = rss_xml.find('channel')
    if channel is None:
        return datetime.date.today()
    pub_date = channel.findtext('pubDate', '')
    if pub_date:
        try:
            return datetime.datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z').date()
        except ValueError:
            pass
    last_build = channel.findtext('lastBuildDate', '')
    if last_build:
        try:
            return datetime.datetime.strptime(last_build, '%a, %d %b %Y %H:%M:%S %z').date()
        except ValueError:
            pass
    return datetime.date.today()


def parse_description(desc_text):
    """Parse RSS description: 'arXiv:ID Announce Type: X \\nAbstract: ...'"""
    abstract = ''
    m = re.search(r'Abstract:\s*(.*)', desc_text, re.DOTALL)
    if m:
        abstract = m.group(1).strip()
    abstract = re.sub(r'\s+', ' ', abstract)
    return abstract


def scrape_arxiv_rss(category, max_results=None):
    """
    Fetch today's papers from arXiv RSS feed.
    Returns (data, data_web) dicts keyed by category name.
    """
    session = _make_session()
    rss_xml_text = fetch_rss(session, category)
    root = ET.fromstring(rss_xml_text)

    current_date = parse_rss_date(root)
    date_str = current_date.isoformat()

    content = {}
    content_to_web = {}

    channel = root.find('channel')
    if channel is None:
        logging.warning(f"No <channel> found in RSS for {category}")
        return {category: content}, {category: content_to_web}

    for item in channel.findall('item'):
        if max_results and len(content) >= max_results:
            break

        link = item.findtext('link', '').strip()
        id_match = re.search(r'(\d+\.\d+)', link)
        if not id_match:
            continue
        paper_id = id_match.group(1)

        title = re.sub(r'\s+', ' ', item.findtext('title', '')).strip()

        creators = item.findtext('dc:creator', '', NS).strip()
        authors = ''
        first_author = ''
        if creators:
            author_list = [a.strip() for a in creators.split(',') if a.strip()]
            if author_list:
                first_author = author_list[0]
                authors = ', '.join(author_list)

        desc_text = item.findtext('description', '')
        abstract = parse_description(desc_text)

        paper_url = ARXIV_BASE + 'abs/' + paper_id
        content[paper_id] = {
            "title": title,
            "authors": authors,
            "first_author": first_author,
            "abstract": abstract,
            "date": date_str,
            "url": paper_url,
        }
        content_to_web[paper_id] = (
            f"- {date_str}, **{title}**, {first_author} et.al., "
            f"Paper: [{paper_url}]({paper_url})\n"
        )
        logging.info(f"Time = {date_str} title = {title} author = {first_author}")

    logging.info(f"Scraped {len(content)} papers from {category}")
    return {category: content}, {category: content_to_web}


def get_daily_papers_by_category(category, max_results=None):
    """Fetch all papers in a given arXiv category via RSS."""
    return scrape_arxiv_rss(category, max_results=max_results)


def save_date_json(filepath, data_dict):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            existing = json.loads(content) if content else {}
    else:
        existing = {}

    for data in data_dict:
        for keyword, papers in data.items():
            if keyword in existing:
                existing[keyword].update(papers)
            else:
                existing[keyword] = papers

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(existing, f)


def generate_daily_md(data_dicts, md_path):
    def pretty_math(s):
        ret = ''
        match = re.search(r"\$.*\$", s)
        if match is None:
            return s
        math_start, math_end = match.span()
        space_trail = space_leading = ''
        if s[:math_start][-1] != ' ' and '*' != s[:math_start][-1]:
            space_trail = ' '
        if s[math_end:][0] != ' ' and '*' != s[math_end:][0]:
            space_leading = ' '
        return s[:math_start] + f'{space_trail}${match.group()[1:-1].strip()}${space_leading}' + s[math_end:]

    today = datetime.date.today().isoformat()

    all_categories = sorted({cat for d in data_dicts for cat in d.keys() if d[cat]})
    title_cats = ', '.join(all_categories) if all_categories else 'Arxiv'

    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title_cats} Daily Papers — {today}\n\n")
        f.write(f"[Back to README](../README.md)\n\n")

        for ddict in data_dicts:
            for category, papers in ddict.items():
                if not papers:
                    continue
                f.write(f"## {category}\n\n")
                f.write(f"|Publish Date|Title|Authors|Abstract|PDF|\n")
                f.write(f"|---|---|---|---|---|\n")

                sorted_papers = sorted(papers.items(),
                    key=lambda x: x[1].get('date', '') if isinstance(x[1], dict) else '',
                    reverse=True)

                for paper_id, info in sorted_papers:
                    if not isinstance(info, dict):
                        continue
                    title = pretty_math(info.get('title', ''))
                    date_val = info.get('date', '')
                    first_author = info.get('first_author', '')
                    abstract = info.get('abstract', '')
                    url = info.get('url', '')
                    f.write(f"|**{date_val}**|**{title}**|{first_author} et.al.|{abstract}|[{paper_id}]({url})|\n")

                f.write('\n')

    paper_count = sum(len(v) for d in data_dicts for v in d.values())
    logging.info(f"Generated {md_path} with {paper_count} papers")


def update_readme_links(md_dir, readme_path):
    md_files = sorted(glob.glob(os.path.join(md_dir, '*.md')), reverse=True)
    if not md_files:
        return

    rows = []
    for fp in md_files:
        date_str = os.path.splitext(os.path.basename(fp))[0]
        count = 0
        categories = []
        with open(fp, encoding='utf-8') as f:
            for line in f:
                if line.startswith('|**'):
                    count += 1
                elif line.startswith('## ') and not line.startswith('## Daily'):
                    categories.append(line.strip().lstrip('# ').strip())
        cat_label = ', '.join(categories) if categories else 'Arxiv'
        rel = os.path.relpath(fp, os.path.dirname(readme_path)).replace('\\', '/')
        rows.append((date_str, count, rel, cat_label))

    marker = '<!-- DAILY_PAPERS -->'
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = ''

    if marker in content:
        header = content[:content.index(marker) + len(marker)]
    else:
        header = content + '\n' + marker

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write('\n\n## Daily Papers\n\n')
        f.write('| Date | Papers | Link |\n')
        f.write('|------|--------|------|\n')
        for date_str, count, rel_path, cat_label in rows:
            f.write(f'| {date_str} | {count} | [{cat_label}]({rel_path}) |\n')
        f.write('\n')

    logging.info(f"Updated README links with {len(rows)} daily entries")


def demo(**config):
    data_collector = []

    daily_category = config.get('daily_category', False)
    category_list = config.get('category_list', [])
    category_max_results = config.get('category_max_results', None)
    today = datetime.date.today().isoformat()

    logging.info("GET daily papers begin")
    if daily_category:
        for cat in category_list:
            logging.info(f"Category: {cat}")
            try:
                data, _ = get_daily_papers_by_category(cat, max_results=category_max_results)
                paper_count = sum(len(v) for v in data.values())
                if paper_count == 0:
                    logging.warning(f"No papers found for {cat}, skipping save")
                    continue
                data_collector.append(data)
            except Exception as e:
                logging.error(f"Failed to fetch papers for {cat}: {e}")
    logging.info("GET daily papers end")

    if not data_collector:
        logging.warning("No data collected, skipping file generation")
        return

    json_dir = config.get('json_dir', './json')
    date_json = os.path.join(json_dir, f"cv-arxiv-daily-{today}.json")
    save_date_json(date_json, data_collector)

    md_dir = config.get('md_dir', './md')
    date_md = os.path.join(md_dir, f"{today}.md")
    generate_daily_md(data_collector, date_md)

    readme_path = config.get('md_readme_path', 'README.md')
    update_readme_links(md_dir, readme_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_path', type=str, default='config.yaml',
                        help='configuration file path')
    args = parser.parse_args()
    config = load_config(args.config_path)
    demo(**config)
