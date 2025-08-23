from flask import Blueprint, jsonify, request, abort
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, current_user
from app.db.session import db
from app.models.models import Hero, User

import config as config

bp = Blueprint("api", __name__)


def get_user_details():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    username = data.get("username") or ""
    password = data.get("password") or ""
    return email, username, password


@bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy"
    })


@bp.route("/auth/register", methods=["POST"])
def register():
    email, username, password = get_user_details()
    if len(password) < 8:
        abort(400, description="Password needs to be at least 8 characters")
    if not username:
        abort(400, description="Username cannot be empty")
    if not email:
        abort(400, description="Email cannot be empty")
    if db.session.query(User).filter_by(email=email).first():
        abort(409, description="User already registered")
    
    user = User(email=email, username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify(message=f"Registered {username}"), 201


@bp.route("/auth/login", methods=["POST"])
def login():
    email, username, password = get_user_details()
    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        abort(401, "Invalid email or password")
    
    access = create_access_token(identity=user.id, additional_claims={"email": user.email})
    refresh = create_refresh_token(identity=user.id)
    return jsonify(
        accessToken=access,
        refreshToken=refresh,
        tokenType="Bearer",
        expiresIn=int(config.jwt_access_token_expires)
    )


@bp.route("/auth/refresh", methods=["POST"])
def refresh():
    user_id = get_jwt_identity()
    new_access = create_access_token(identity=user_id)
    return jsonify(
        accessToken=new_access,
        tokenType="Bearer",
        expiresIn=int(config.jwt_access_token_expires)
    )


@bp.get("/users/me")
def me():
    if not current_user:
        abort(404, description="User not found")
    return jsonify(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        createdAt=current_user.created_at.isoformat()
    )


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