import requests

from config import TIMEOUT, USER_AGENT, PLAYWRIGHT_TIMEOUT_MS

def fetch_page_requests(url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    res = requests.get(url, headers=headers, timeout=TIMEOUT)
    res.raise_for_status()
    if not res.text.strip():
        raise RuntimeError("Page is empty")
    return res.text

def fetch_page_edge(url: str) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(user_agent=USER_AGENT)
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("table tbody tr", timeout=60000)
        
        prev_count = 0

        for i in range(60):
            rows = page.locator("table tbody tr").count()
            print(f"Loop {i}: {rows} rows")

            if rows == prev_count and i > 3:
                break
            prev_count = rows

            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(1500)

        html = page.content()
        browser.close()
        return html
    
def fetch_page(url: str) -> str:
    html = fetch_page_requests(url)

    if "Rank" in html and "Hero" in html and "Win rate" in html:
        return html

    return fetch_page_edge(url)