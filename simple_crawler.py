import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

def get_all_sublinks(start_url, max_depth=2):
    visited = set()
    to_visit = [(start_url, 0)]
    base_domain = urlparse(start_url).netloc
    all_links = set()

    while to_visit:
        url, depth = to_visit.pop()
        if url in visited or depth > max_depth:
            continue
        visited.add(url)

        try:
            response = requests.get(url, timeout=10)
        except requests.RequestException:
            continue

        if 'text/html' not in response.headers.get('Content-Type', ''):
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            full_url = urljoin(url, a_tag['href'])
            parsed = urlparse(full_url)
            if parsed.netloc == base_domain:
                clean_url = parsed.scheme + '://' + parsed.netloc + parsed.path
                all_links.add(clean_url)
                if clean_url not in visited:
                    to_visit.append((clean_url, depth + 1))

    return sorted(all_links)

def get_links_with_js(url, max_depth=2):
    visited = set()
    to_visit = [(url, 0)]
    base_domain = "itwebshop.au.dk"
    found_links = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        while to_visit:
            link, depth = to_visit.pop()
            if link in visited or depth > max_depth:
                continue
            visited.add(link)

            try:
                page.goto(link, timeout=15000)
            except Exception:
                continue

            anchors = page.locator("a[href]")
            hrefs = anchors.evaluate_all("elements => elements.map(e => e.href)")

            for href in hrefs:
                if base_domain in href:
                    found_links.add(href)
                    if href not in visited:
                        to_visit.append((href, depth + 1))
        
        browser.close()
    return found_links

# Example usage
links = get_all_sublinks("https://itwebshop.au.dk/")
for link in links:
    print(link)
