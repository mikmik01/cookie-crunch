import os
from flask import Flask, jsonify
from pathlib import Path
from dotenv import load_dotenv
from app.db.session import db
from app.api.v1 import api_v1
import config as config

def create_app():
    # * remember to create a SCHEMA with the database name first. not a CONNECTION
    env_path = Path(__file__).resolve().parents[3] / "dev.env"
    load_dotenv(dotenv_path=env_path)
    # print(user, password, host, port, database)
    
    uri = f"mysql+pymysql://{config.db_user}:{config.db_password}@{config.host}:{config.db_port}/{config.db_name}"
    
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    app.register_blueprint(api_v1, url_prefix="/api/v1")
    
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(code="BAD REQUEST", message=str(e), details={}), 400
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify(code="NOT FOUND", message=str(e), details={}), 404
    
    @app.errorhandler(500)
    def not_found(e):
        return jsonify(code="SERVER ERROR", message=str(e), details={}), 500
    return app

__all__ = ["create_app", "db"]