import requests
from collections import OrderedDict

from app.core.config import (
    TIMEOUT,
    USER_AGENT,
    PLAYWRIGHT_TIMEOUT_MS,
    RANK_FILTERS,
    build_stats_url,
)


def fetch_page_requests(url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    res = requests.get(url, headers=headers, timeout=TIMEOUT)
    res.raise_for_status()

    if not res.text.strip():
        raise RuntimeError("Page is empty")

    return res.text


def _get_visible_rows(page) -> list[tuple[str, str]]:
    rows = page.locator("table tbody tr")
    count = rows.count()

    collected = []

    for i in range(count):
        row = rows.nth(i)

        try:
            row_text = " ".join(row.inner_text(timeout=3000).split())
            row_html = row.evaluate("el => el.outerHTML")
        except Exception:
            continue

        if row_text and row_html:
            collected.append((row_text, row_html))

    return collected


def _build_table_html(row_htmls: list[str]) -> str:
    rows = "\n".join(row_htmls)

    return f"""
    <html>
      <body>
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Lane</th>
              <th>Hero</th>
              <th>Tier</th>
              <th>Win Rate</th>
              <th>Ban Rate</th>
              <th>Pick Rate</th>
              <th>Roles</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
      </body>
    </html>
    """


def fetch_page_edge(url: str) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=USER_AGENT)

        print(f"Opening URL: {url}")

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=PLAYWRIGHT_TIMEOUT_MS,
        )

        page.wait_for_selector("table tbody tr", timeout=PLAYWRIGHT_TIMEOUT_MS)
        page.wait_for_timeout(2000)

        seen_rows: OrderedDict[str, str] = OrderedDict()
        prev_unique_count = 0
        stale_rounds = 0

        for i in range(80):
            visible_rows = _get_visible_rows(page)

            for row_text, row_html in visible_rows:
                seen_rows[row_text] = row_html

            unique_count = len(seen_rows)
            print(f"Scroll {i}: collected {unique_count} unique rows")

            if unique_count == prev_unique_count:
                stale_rounds += 1
            else:
                stale_rounds = 0

            if stale_rounds >= 3 and i > 3:
                break

            prev_unique_count = unique_count

            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(1500)

        browser.close()

        if not seen_rows:
            raise RuntimeError(f"No rows collected from {url}")

        return _build_table_html(list(seen_rows.values()))


def fetch_page(url: str) -> str:
    return fetch_page_edge(url)


def fetch_pages_by_rank(base_url: str | None = None) -> dict[str, str]:
    pages: dict[str, str] = {}

    for rank_filter in RANK_FILTERS:
        url = build_stats_url(rank_filter)
        print(f"Fetching {rank_filter}: {url}")
        pages[rank_filter] = fetch_page_edge(url)

    return pages