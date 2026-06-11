from bs4 import BeautifulSoup

from app.schemas.schemas import STAT_FIELDS


def clean_text(val: str) -> str:
    return " ".join(val.strip().split())


def get_lane_signature(cell) -> str:
    svg = cell.find("svg")
    if not svg:
        return ""

    path = svg.find("path")
    if not path:
        return ""

    d = (path.get("d") or "").strip()
    if not d:
        return ""

    return d[:50]


LANE_SIGNATURES = {
    "M244.151,1337.62H231": "Mid",
    "M495.652,1298.32": "Gold",
    "M649.568,1290.79": "Exp",
    "M341.818,1307.34v-4": "Jungle",
    "M113.575,1329.5a9": "Roam",
}


def parse_lane(cell) -> str:
    sig = get_lane_signature(cell)

    for prefix, lane in LANE_SIGNATURES.items():
        if sig.startswith(prefix):
            return lane

    return "Unknown"


def extract_stats(html: str, rank_filter: str | None = None) -> list[dict]:
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

        # Expected visible columns:
        # rank, lane, hero, tier, win_rate, ban_rate, pick_rate, roles
        if len(cells) < 8:
            continue

        values = [
            clean_text(cell.get_text(" ", strip=True))
            for cell in cells[:8]
        ]

        if len(values) < 8:
            continue

        record = {
            "rank_filter": rank_filter or "",
            "rank": values[0],
            "lane": parse_lane(cells[1]),
            "hero": values[2],
            "tier": values[3],
            "win_rate": values[4],
            "ban_rate": values[5],
            "pick_rate": values[6],
            "roles": values[7],
        }

        if not record["hero"]:
            continue

        extracted_rows.append(record)

    if not extracted_rows:
        raise RuntimeError("No stats rows were extracted")

    return extracted_rows