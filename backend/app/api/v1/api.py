from flask import Blueprint, jsonify
from app.db.session import db
from app.models.models import Hero

bp = Blueprint("api", __name__)

@bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy"
    })

@bp.route("/heroes", methods=["GET"])
def list_heroes():
    query = db.session.query(Hero)
    heroes = query.all()
    result = [
        {
            "id": hero.id,
            "name": hero.name,
            "difficulty": hero.difficulty,
            "roles": hero.roles,
            "tags": hero.tags
        }
        for hero in heroes
    ]
    return jsonify(result), 200

@bp.route("/heroes/<string:hero_id>")
def get_hero_by_id(hero_id):
    hero = db.session.query(Hero).filter_by(id=hero_id).first()
    
    if not hero:
        return jsonify({
            "code": "NOT_FOUND",
            "message": f"Hero with id '{hero_id}' not found",
            "details": {}
        }), 404
    
    return jsonify({
        "id": hero.id,
        "name": hero.name,
        "difficulty": hero.difficulty,
        "roles": hero.roles,
        "tags": hero.tags
    }), 200