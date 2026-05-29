"""Test that abstracts in generated MD files are not truncated."""
import os
import sys
import json
import tempfile
import logging

logging.basicConfig(level=logging.WARNING)

from daily_arxiv import scrape_arxiv_listing, generate_daily_md, save_date_json

def test_abstracts_complete():
    # fetch a small sample
    data, _ = scrape_arxiv_listing('cs.CV', max_results=5)
    assert len(list(data.values())[0]) == 5, f"Expected 5 papers, got {len(list(data.values())[0])}"

    with tempfile.TemporaryDirectory() as tmpdir:
        # save JSON for reference
        json_path = os.path.join(tmpdir, 'test.json')
        save_date_json(json_path, [data])

        # generate MD
        md_path = os.path.join(tmpdir, 'test.md')
        generate_daily_md([data], md_path)

        # verify MD file exists and has content
        assert os.path.exists(md_path), "MD file not created"
        with open(md_path) as f:
            md_content = f.read()

        # load original data
        with open(json_path) as f:
            json_data = json.load(f)

        papers = list(json_data.values())[0]
        failures = 0

        for paper_id, info in papers.items():
            original = info.get('abstract', '')

            # find this paper's row in MD
            row_start = md_content.find(f'[{paper_id}]')
            if row_start == -1:
                print(f"FAIL: paper {paper_id} not found in MD")
                failures += 1
                continue

            # extract abstract from MD row (5th column)
            row_end = md_content.find('\n', row_start)
            row = md_content[:row_end]
            # reverse scan to find row beginning
            row_begin = row.rfind('\n', 0, row_start)
            row = md_content[row_begin:row_end]

            cols = row.split('|')
            if len(cols) < 6:
                print(f"FAIL: paper {paper_id} has malformed row: {len(cols)} cols")
                failures += 1
                continue

            md_abstract = cols[4].strip()

            # check: MD abstract should contain the full original
            if len(md_abstract) != len(original):
                print(f"FAIL: paper {paper_id} length mismatch: MD={len(md_abstract)}, JSON={len(original)}")
                print(f"  MD first 100: {md_abstract[:100]}")
                print(f"  MD last 100:  {md_abstract[-100:]}")
                print(f"  JSON last 100: {original[-100:]}")
                failures += 1
            elif md_abstract != original:
                print(f"FAIL: paper {paper_id} content mismatch")
                print(f"  MD:   {md_abstract[:120]}")
                print(f"  JSON: {original[:120]}")
                failures += 1
            else:
                print(f"PASS: {paper_id} ({len(original)} chars)")

        if failures == 0:
            print(f"\nAll 5 abstracts complete. TEST PASSED.")
        else:
            print(f"\n{failures} failures. TEST FAILED.")
            sys.exit(1)

if __name__ == '__main__':
    test_abstracts_complete()
