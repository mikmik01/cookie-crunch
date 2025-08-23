import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parents[1] / "dev.env"
print(env_path)
load_dotenv(dotenv_path=env_path)

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
host = os.getenv("HOST")
db_port = os.getenv("DB_PORT")
server_port = os.getenv("SERVER_PORT")
db_name = os.getenv("DB_NAME")
jwt_secret_key = os.getenv("JWT_SECRET_KEY")
jwt_access_token_expires = os.getenv("JWT_ACCESS_TOKEN_EXPIRES")
jwt_refresh_token_expires = os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 3600)