from bs4 import BeautifulSoup
from schemas import STAT_FIELDS

def clean_text(val: str) ->  str:
    return " ".join(val.strip().split())

def extract_stats(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if table is None:
        raise RuntimeError("Could not find any table in the HTML")

    rows = table.find_all("tr")
    if not rows:
        raise RuntimeError("No table rows found")
    
    extracted_rows = []

    for tr in rows[1:]:
        cells = tr.find_all(["td", "th"])
        if len(cells) < len(STAT_FIELDS):
            continue

        values = [
            clean_text(cell.get_text(" ", strip=True))
            for cell in cells[: len(STAT_FIELDS)]
        ]

        record = {
            "rank": values[0],
            "lane": values[1],
            "hero": values[2],
            "tier": values[3],
            "win_rate": values[4],
            "ban_rate": values[5],
            "pick_rate": values[6],
            "roles": values[7],
        }

        extracted_rows.append(record)
    
    if not extracted_rows:
        raise RuntimeError("No stats rows were extracted")

    return extracted_rows