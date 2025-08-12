from app.db.create_app import create_app
from app.db.session import db
import config as config

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Tables created successfully")
    app.run(debug=True, host=config.host, port=config.server_port)