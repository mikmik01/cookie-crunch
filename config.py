from pathlib import Path

SRC_URL = "https://mlbb.gg/statistics"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"

TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36 "
    "Edg/120.0.0.0"
)

PLAYWRIGHT_WAIT_MS = 5000
PLAYWRIGHT_TIMEOUT_MS = 30000