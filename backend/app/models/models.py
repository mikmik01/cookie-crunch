from ..db.create_app import db
from sqlalchemy.dialects.mysql import ENUM

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Hero(db.Model):
    __tablename__ = 'heroes'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100))
    difficulty = db.Column(ENUM("easy", "medium", "hard", "extreme"))
    roles = db.Column(db.JSON)
    tags = db.Column(db.JSON)

class ComfortTag(db.Model):
    __tablename__ = 'comfort_tags'

    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), primary_key=True)
    hero_id = db.Column(db.String(50), db.ForeignKey("heroes.id"), primary_key=True)
    comfort_weight = db.Column(db.Float)

    __table_args__ = (
        db.CheckConstraint("comfort_weight >= 0 AND comfort_weight <= 1", name="ck_weight_range"),
    )