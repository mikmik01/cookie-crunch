import json
from pathlib import Path
from backend.app.db.create_app import engine, heroes

data_path = Path(__file__).resolve().parents[2] / "data" / "heroes.json"

heroes_data = json.loads(data_path.read_text())

with engine.connect() as conn:
    conn.execute(heroes.delete())
    print("Cleared heroes table")

    conn.execute(heroes.insert(), heroes_data)
    conn.commit()
    print(f"Inserted {len(heroes_data)} into table")