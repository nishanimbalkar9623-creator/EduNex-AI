"""EduNex AI Phase 1 Flask application factory."""

from __future__ import annotations

import logging
from typing import Any

from flask import Flask, jsonify, render_template, request

from ai.llm import AIServiceUnavailable, generate_response
from ai.memory import add_turn, clear_history, get_history
from ai.tools import handle_school_question
from auth.authentication import auth_bp
from config import Config


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Create the application without coupling Phase 1 to a database or LLM."""
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY must be set in .env before starting EduNex AI.")
    accounts = app.config.get("DEMO_ACCOUNTS", {})
    if not accounts or not all(account.get("password") for account in accounts.values()):
        raise RuntimeError("Configure password hashes for every demo account in .env before starting EduNex AI.")

    app.register_blueprint(auth_bp)

    @app.get("/")
    def home():
        return render_template("login.html")

    @app.get("/dashboard")
    def dashboard():
        from auth.authentication import current_demo_user

        user = current_demo_user()
        if user is None:
            return render_template("login.html"), 401
        return render_template("dashboard.html", user=user)

    @app.post("/api/chat")
    def chat():
        """Call the local LLM with trusted session identity and bounded context."""
        from auth.authentication import current_demo_user

        user = current_demo_user()
        if user is None:
            return jsonify(error="Authentication is required."), 401
        payload = request.get_json(silent=True) or {}
        message = str(payload.get("message", "")).strip()
        if not message:
            return jsonify(error="A message is required."), 400
        school_response = handle_school_question(user, message)
        if school_response is not None:
            add_turn(message, school_response, app.config["AI_MAX_CONTEXT_MESSAGES"])
            return jsonify(success=True, response=school_response, message=school_response, source="school_data")
        service = app.config.get("CHAT_SERVICE", generate_response)
        try:
            response = service(user, message, get_history(app.config["AI_MAX_CONTEXT_MESSAGES"]))
        except AIServiceUnavailable as error:
            return jsonify(success=False, error=str(error)), 503
        except Exception:
            app.logger.exception("Unexpected chat service failure")
            return jsonify(success=False, error="EduNex AI could not process that request. Please try again."), 500
        add_turn(message, response, app.config["AI_MAX_CONTEXT_MESSAGES"])
        return jsonify(success=True, response=response, message=response)

    @app.delete("/api/chat/history")
    def delete_chat_history():
        from auth.authentication import current_demo_user

        if current_demo_user() is None:
            return jsonify(error="Authentication is required."), 401
        clear_history()
        return jsonify(success=True)

    @app.get("/api/health")
    def health():
        from ai.llm import check_ollama_status

        ollama_info = check_ollama_status()
        return jsonify(status="ok", phase=1, ollama=ollama_info)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify(error="Resource not found."), 404

    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_app().run(debug=True)
