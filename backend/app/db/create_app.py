import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from app.db.session import db
from app.api.v1 import api_v1
from app.models.models import User
import config as config

jwt = JWTManager()

def create_app():
    # * remember to create a SCHEMA with the database name first. not a CONNECTION
    env_path = Path(__file__).resolve().parents[3] / "dev.env"
    load_dotenv(dotenv_path=env_path)
    # print(user, password, host, port, database)
    
    uri = f"mysql+pymysql://{config.db_user}:{config.db_password}@{config.host}:{config.db_port}/{config.db_name}"
    
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_SECRET_KEY"] = config.jwt_secret_key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = config.jwt_access_token_expires
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = config.jwt_refresh_token_expires
    
    db.init_app(app)
    jwt.init_app(app)
    
    @jwt.user_lookup_loader
    def load_user(_h, data):
        return db.session.get(User, data["sub"])

    app.register_blueprint(api_v1, url_prefix="/api/v1")
    
    return app

__all__ = ["create_app", "db"]