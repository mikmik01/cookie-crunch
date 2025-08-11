import os
from flask import Flask
from pathlib import Path
from dotenv import load_dotenv
from app.db.session import db

def create_app():
    # * remember to create a SCHEMA with the database name first. not a CONNECTION
    env_path = Path(__file__).resolve().parents[3] / "dev.env"
    load_dotenv(dotenv_path=env_path)

    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")
    # print(user, password, host, port, database)
    
    uri = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

__all__ = ["create_app", "db"]