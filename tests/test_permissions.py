from flask import jsonify

from auth.permissions import require_roles


def test_role_is_checked_from_session(client, app):
    @app.get("/principal-only")
    @require_roles("principal")
    def principal_only():
        return jsonify(ok=True)

    client.post("/api/auth/login", json={"username": "rahul", "password": "test-password"})
    assert client.get("/principal-only").status_code == 403
    client.post("/api/auth/login", json={"username": "dr-deshmukh", "password": "test-password"})
    assert client.get("/principal-only").status_code == 200
