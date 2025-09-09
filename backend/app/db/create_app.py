from flask import Flask
from flask_jwt_extended import JWTManager
from app.db.session import db
import config as config
from sqlalchemy import create_engine, text

jwt = JWTManager()

def create_app():
    # * remember to create a SCHEMA with the database name first. not a CONNECTION
    tmp_uri = f"mysql+pymysql://{config.db_user}:{config.db_password}@{config.host}:{config.db_port}/"
    _engine = create_engine(tmp_uri, future=True, isolation_level="AUTOCOMMIT")

    with _engine.connect() as conn:
        conn.execute(text(
            f"CREATE DATABASE IF NOT EXISTS `{config.db_name}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        ))
    uri = f"mysql+pymysql://{config.db_user}:{config.db_password}@{config.host}:{config.db_port}/{config.db_name}"

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_SECRET_KEY"] = config.jwt_secret_key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = config.jwt_access_token_expires
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = config.jwt_refresh_token_expires
    
    db.init_app(app)
    jwt.init_app(app)

    from app.api.v1.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    
    @jwt.user_lookup_loader
    def load_user(_h, data):
        from app.models.models import User
        return db.session.get(User, data["sub"])
    
    print("App instance created successfully")
    return app

__all__ = ["create_app", "db"]