import json
from pathlib import Path
from sqlalchemy import delete, insert
from app.db.create_app import create_app
from app.db.session import db
from app.models.models import Hero

def main():
    app = create_app()
    data_path = Path(__file__).resolve().parents[2] / "data" / "heroes.json"
    heroes_data = json.loads(data_path.read_text(encoding="utf-8"))

    with app.app_context():
        with db.engine.begin() as conn:
            conn.execute(delete(Hero))
            conn.execute(insert(Hero), heroes_data)
        print(f"Cleared and inserted {len(heroes_data)} heroes")

if __name__ == "__main__":
    main()