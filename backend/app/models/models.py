from app.db.session import db
from sqlalchemy.dialects.mysql import ENUM

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.String(100))
    username = db.Column(db.String(20))
    password = db.Column(db.VARCHAR(255))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Hero(db.Model):
    __tablename__ = 'heroes'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100))
    damage_type = db.Column(ENUM("magic", "physical", "N.A.", "hybrid"))
    difficulty = db.Column(ENUM("easy", "medium", "hard", "extreme"))
    stage = db.Column(ENUM("early", "mid", "late", "any"))
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

class Draft(db.Model):
    __tablename__ = 'drafts'

    id = db.Column(db.String(36), primary_key=True)
    created_by = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    phase = db.Column(ENUM("ban", "pick", "done"), nullable=False, server_default="ban")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    max_bans = db.Column(db.Integer, server_default=10)

    creator = db.relationship("User")

class DraftSelection(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    draft_id = db.Column(db.String(36), db.ForeignKey("drafts.id"), nullable=False, index=True)
    hero_id = db.Column(db.String(50), db.ForeignKey("heroes.id"), primary_key=True)
    selection_type = db.Column(ENUM("ban", "pick"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    draft = db.relationship("Draft", backref=db.backref("selections", cascade="all, delete-orphan"))
    hero = db.relationship("Hero")

    __table_args__ = (
        # Prevents picking a banned hero, banning an already picked hero, or duplicates
        db.UniqueConstraint("draft_id", "hero_id", name="uq_draft_hero_once"),
        db.Index("idx_draft_type", "draft_id", "type"),
    )