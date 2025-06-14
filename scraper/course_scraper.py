import os
import json
import re
from datetime import datetime
from urllib.parse import urlparse
from markdownify import markdownify as md
from playwright.sync_api import sync_playwright

BASE_URL = "https://tds.s-anand.net/#/2025-01/"
BASE_ORIGIN = "https://tds.s-anand.net"
OUTPUT_JSON = "app/data/course_content.json"

visited = set()
collected_data = []

def sanitize_title(title):
    return re.sub(r'[\\/*?:"<>|]', "_", title).strip()

def extract_all_internal_links(page):
    links = page.eval_on_selector_all("a[href]", "els => els.map(el => el.href)")
    return list(set(
        link for link in links
        if BASE_ORIGIN in link and '/#/' in link
    ))

def wait_for_main_and_get_html(page):
    page.wait_for_selector("article.markdown-section#main", timeout=10000)
    return page.inner_html("article.markdown-section#main")

def crawl_page(page, url):
    if url in visited:
        return
    visited.add(url)

    print(f"📄 Visiting: {url}")
    try:
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(1000)
        html = wait_for_main_and_get_html(page)
    except Exception as e:
        print(f"❌ Error loading page: {url}\n{e}")
        return

    title = page.title().split(" - ")[0].strip() or f"Page {len(visited)}"
    content = md(html)

    collected_data.append({
        "source": "course",
        "title": title,
        "url": url,
        "content": content
    })

    links = extract_all_internal_links(page)
    for link in links:
        if link not in visited:
            crawl_page(page, link)

def main():
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        crawl_page(page, BASE_URL)

        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(collected_data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Saved {len(collected_data)} course pages to: {OUTPUT_JSON}")
        browser.close()

if __name__ == "__main__":
    main()
