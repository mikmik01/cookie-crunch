import sqlalchemy as db
from dotenv import load_dotenv

load_dotenv(dotenv_path="/dev.env")

user = "root"
password = "root"
host = "127.0.0.1"
port = 3306
database = "mocha"

def init_engine():
    # * remember to create a SCHEMA with the database name first. not a CONNECTION
    print(f"Connecting to {host}:{port} / {database} as {user}")
    return db.create_engine(
        url=f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    )

def test_engine_connection(engine):
    try:
        conn = engine.connect()
        print("Engine connected successfully")
        conn.close()
    except Exception as e:
        print("Failed to connect to the engine: ", e)

engine = init_engine()


try:
    test_engine_connection(engine=engine)

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