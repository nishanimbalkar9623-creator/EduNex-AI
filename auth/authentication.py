"""Session-based authentication for the non-production Phase 1 demo."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request, session
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _account_without_password(username: str) -> dict[str, str] | None:
    account = current_app.config["DEMO_ACCOUNTS"].get(username)
    if not account:
        return None
    return {"username": username, "name": account["name"], "role": account["role"]}


def current_demo_user() -> dict[str, str] | None:
    """Return the authenticated session identity; never trust chat-provided roles."""
    username = session.get("username")
    return _account_without_password(username) if username else None


def _valid_login(username: str, password: str) -> bool:
    account = current_app.config["DEMO_ACCOUNTS"].get(username)
    if not account or not account.get("password"):
        return False
    return check_password_hash(account["password"], password)


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or request.form
    username = str(payload.get("username", "")).strip().lower()
    password = str(payload.get("password", ""))
    if not _valid_login(username, password):
        return jsonify(error="Invalid username or password."), 401
    session.clear()
    session["username"] = username
    return jsonify(user=current_demo_user())


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify(message="You have been logged out.")


@auth_bp.get("/me")
def me():
    user = current_demo_user()
    if user is None:
        return jsonify(error="Authentication is required."), 401
    return jsonify(user=user)

