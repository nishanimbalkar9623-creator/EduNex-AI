"""Role checks reserved for future protected school-service endpoints."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps

from flask import jsonify

from auth.authentication import current_demo_user


def require_roles(*allowed_roles: str) -> Callable:
    """Enforce role permissions from the authenticated session, not request data."""
    def decorator(view: Callable) -> Callable:
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = current_demo_user()
            if user is None:
                return jsonify(error="Authentication is required."), 401
            if user["role"] not in allowed_roles:
                return jsonify(error="You are not authorized to perform this action."), 403
            return view(*args, **kwargs)
        return wrapped
    return decorator
