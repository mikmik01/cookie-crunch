from datetime import datetime
from pathlib import Path

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")

def save_text(text: str, path: Path) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")

def build_raw_html_path(dir: Path, ts: str) -> Path:
    return dir / f"stats_{ts}.html"

def build_csv_path(dir: Path, ts: str) -> Path:
    return dir / f"stats_{ts}.csv"

def build_clean_csv_path(dir: Path, timestamp: str) -> Path:
    return dir / f"stats_cleaned_{timestamp}.csv"


def build_issues_csv_path(dir: Path, timestamp: str) -> Path:
    return dir / f"stats_issues_{timestamp}.csv"