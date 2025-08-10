import json
from pathlib import Path
from session import engine, heroes

data_path = Path(__file__).parent / "data" / "heroes.json"

heroes_data = json.loads(data_path.read_text())

with engine.connect() as conn:
    conn.execute(heroes.delete())
    print("Cleared heroes table")

    conn.execute(heroes.insert(), heroes_data)
    print(f"Inserted {len(heroes_data)} into table")