import os
import sqlalchemy as db
from dotenv import load_dotenv

load_dotenv()

user = "root"
password = "root"
host = "127.0.0.1"
port = 3306
database = "mocha"


if __name__ == "__main__":
    try:
        print(f"Connecting to {host}:{port} / {database} as {user}")
        engine = db.create_engine(
            url=f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        )
        print(f"Connection to {host} for user {user} successful")

        with engine.connect() as conn:
            conn.execute(db.text(
                f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci"
            ))

        metadata_obj = db.MetaData()

        users = db.Table(
            'users',
            metadata_obj,
            db.Column('id', db.VARCHAR(36), primary_key=True),
            db.Column('created_at', db.DateTime, server_default=db.func.now())
        )

        heroes = db.Table(
            'heroes',
            metadata_obj,
            db.Column('id', db.VARCHAR(50), primary_key=True),
            db.Column('name', db.VARCHAR(100)),
            db.Column('difficulty', db.Enum("easy", "medium", "hard", "extreme")),
            db.Column('roles', db.JSON),
            db.Column('tags', db.JSON),
        )

        comfort_tags = db.Table(
            'comfort_tags',
            metadata_obj,
            db.Column('user_id', db.VARCHAR(36), db.ForeignKey("users.id"), primary_key=True),
            db.Column('hero_id', db.VARCHAR(50), db.ForeignKey("heroes.id"), primary_key=True),
            db.Column('comfort_weight', db.Float),
            db.CheckConstraint("comfort_weight >= 0 AND comfort_weight <= 1", name="ck_weight_range")
        )

        metadata_obj.create_all(engine)
        print("Tables created")
    except Exception as e:
        print(f"Connection to {host} failed: {e}")