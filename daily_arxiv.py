import os
import re
import json
import glob
import yaml
import logging
import argparse
import datetime
import requests

logging.basicConfig(format='[%(asctime)s %(levelname)s] %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)

arxiv_url = "http://arxiv.org/"

def load_config(config_file:str) -> dict:
    '''
    config_file: input config file path
    return: a dict of configuration
    '''
    # make filters pretty
    def pretty_filters(**config) -> dict:
        keywords = dict()
        EXCAPE = '\"'
        QUOTA = '' # NO-USE
        OR = ' OR ' # TODO
        def parse_filters(filters:list):
            ret = ''
            for idx in range(0,len(filters)):
                filter = filters[idx]
                if len(filter.split()) > 1:
                    ret += (EXCAPE + filter + EXCAPE)
                else:
                    ret += (QUOTA + filter + QUOTA)
                if idx != len(filters) - 1:
                    ret += OR
            return ret
        for k,v in config['keywords'].items():
            keywords[k] = parse_filters(v['filters'])
        return keywords
    with open(config_file,'r') as f:
        config = yaml.load(f,Loader=yaml.FullLoader)
        if 'keywords' in config:
            config['kv'] = pretty_filters(**config)
        else:
            config['kv'] = {}
        logging.info(f'config = {config}')
    return config

def scrape_arxiv_listing(category, max_results=None):
    """
    Scrape arXiv /new listing page for today's papers with abstracts.
    @param category: str, arXiv category code (e.g. cs.CV)
    @param max_results: int or None, max papers to return (None = all)
    @return: (data, data_web) dicts keyed by category name
    """
    url = f"https://arxiv.org/list/{category}/new?skip=0&show=2000"
    logging.info(f"Fetching {url}")
    resp = requests.get(url, timeout=60)
    html = resp.text

    # date: <h3>Showing new listings for Thursday, 28 May 2026</h3>
    date_m = re.search(r'<h3>Showing new listings for \w+, (\d{1,2} \w+ \d{4})</h3>', html)
    if date_m:
        try:
            current_date = datetime.datetime.strptime(date_m.group(1), '%d %B %Y').date()
        except ValueError:
            current_date = datetime.date.today()
    else:
        current_date = datetime.date.today()
    date_str = current_date.isoformat()

    content = dict()
    content_to_web = dict()

    entries = list(re.finditer(
        r'<a\s+name=[\'"]item\d+[\'"]>.*?</a>\s*<a\s+href\s*=\s*["\']/abs/(\d+\.\d+)[^>]*>\s*arXiv:\1',
        html
    ))

    for entry in entries:
        if max_results and len(content) >= max_results:
            break

        paper_id = entry.group(1)
        dd_start = html.find('<dd>', entry.end())
        if dd_start == -1:
            continue
        dd_end = html.find('</dd>', dd_start)
        if dd_end == -1:
            continue
        dd_block = html[dd_start:dd_end]

        # title
        title_m = re.search(
            r"<div\s+class=['\"]list-title[^'\"]*['\"][^>]*>.*?<span[^>]*>Title:</span>\s*(.+?)\s*</div>",
            dd_block, re.DOTALL
        )
        title = ''
        if title_m:
            title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip()
            title = re.sub(r'\s+', ' ', title)

        # authors
        authors = ''
        first_author = ''
        authors_m = re.search(
            r"<div\s+class=['\"]list-authors['\"][^>]*>(.+?)</div>",
            dd_block, re.DOTALL
        )
        if authors_m:
            author_texts = re.findall(r'<a[^>]*>([^<]+)</a>', authors_m.group(1))
            if author_texts:
                first_author = author_texts[0].strip()
                authors = ', '.join(a.strip() for a in author_texts)

        # abstract: <p class='mathjax'>...</p>
        abstract = ''
        abstract_m = re.search(
            r"<p\s+class=['\"]mathjax['\"][^>]*>(.+?)</p>",
            dd_block, re.DOTALL
        )
        if abstract_m:
            abstract = re.sub(r'<[^>]+>', '', abstract_m.group(1)).strip()
            abstract = re.sub(r'\s+', ' ', abstract)

        paper_url = arxiv_url + 'abs/' + paper_id
        paper_data = {
            "title": title,
            "authors": authors,
            "first_author": first_author,
            "abstract": abstract,
            "date": date_str,
            "url": paper_url,
        }
        content[paper_id] = paper_data
        content_to_web[paper_id] = f"- {date_str}, **{title}**, {first_author} et.al., Paper: [{paper_url}]({paper_url})\n"
        logging.info(f"Time = {date_str} title = {title} author = {first_author}")

    logging.info(f"Scraped {len(content)} papers from {category}")
    data = {category: content}
    data_web = {category: content_to_web}
    return data, data_web

def get_daily_papers_by_category(category, max_results=None):
    """Fetch all papers in a given arXiv category via HTML scraping."""
    return scrape_arxiv_listing(category, max_results=max_results)

def save_date_json(filepath, data_dict):
    '''
    write today's papers to a date-stamped JSON file.
    if re-run on the same day, merge with existing data.
    '''
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
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

    with open(filepath, "w") as f:
        json.dump(existing, f)

def generate_daily_md(data_dicts, md_path):
    """Generate a daily markdown file from scraped paper data."""
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

    with open(md_path, 'w') as f:
        f.write(f"# cs.CV Daily Papers — {today}\n\n")
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
    """Scan md/ directory and update README with links to daily files."""
    md_files = sorted(glob.glob(os.path.join(md_dir, '*.md')), reverse=True)
    if not md_files:
        return

    rows = []
    for fp in md_files:
        date_str = os.path.splitext(os.path.basename(fp))[0]
        # count rows with paper links
        count = 0
        with open(fp) as f:
            for line in f:
                if line.startswith('|**'):
                    count += 1
        rows.append((date_str, count, os.path.relpath(fp, os.path.dirname(readme_path))))

    marker = '<!-- DAILY_PAPERS -->'
    try:
        with open(readme_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        content = ''

    if marker in content:
        header = content[:content.index(marker) + len(marker)]
    else:
        header = content + '\n' + marker

    with open(readme_path, 'w') as f:
        f.write(header)
        f.write('\n\n## Daily Papers\n\n')
        f.write('| Date | Papers | Link |\n')
        f.write('|------|--------|------|\n')
        for date_str, count, rel_path in rows:
            f.write(f'| {date_str} | {count} | [cs.CV]({rel_path}) |\n')
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
            data, _ = get_daily_papers_by_category(cat, max_results=category_max_results)
            data_collector.append(data)
    logging.info("GET daily papers end")

    # 1. save to date-stamped JSON
    json_dir = config.get('json_dir', './json')
    date_json = os.path.join(json_dir, f"cv-arxiv-daily-{today}.json")
    save_date_json(date_json, data_collector)

    # 2. generate daily markdown
    md_dir = config.get('md_dir', './md')
    date_md = os.path.join(md_dir, f"{today}.md")
    generate_daily_md(data_collector, date_md)

    # 3. update README index links
    readme_path = config.get('md_readme_path', 'README.md')
    update_readme_links(md_dir, readme_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_path', type=str, default='config.yaml',
                        help='configuration file path')
    args = parser.parse_args()
    config = load_config(args.config_path)
    demo(**config)
