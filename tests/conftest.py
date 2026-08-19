from werkzeug.security import generate_password_hash

from app import create_app


def make_accounts():
    return {
        "rahul": {"name": "Rahul", "role": "student", "password": generate_password_hash("test-password")},
        "mrs-sharma": {"name": "Mrs. Sharma", "role": "parent", "password": generate_password_hash("test-password")},
        "mr-patil": {"name": "Mr. Patil", "role": "teacher", "password": generate_password_hash("test-password")},
        "dr-deshmukh": {"name": "Dr. Deshmukh", "role": "principal", "password": generate_password_hash("test-password")},
    }


def fake_chat_service(user, message, history):
    """Avoid requiring a local model for unit tests."""
    return f"Hello {user['name']}, you said: {message}"


def pytest_configure(config):
    config.addinivalue_line("markers", "phase1: Phase 1 test")


import pytest


@pytest.fixture()
def app():
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-key",
            "DEMO_ACCOUNTS": make_accounts(),
            "CHAT_SERVICE": fake_chat_service,
        }
    )


@pytest.fixture()
def client(app):
    return app.test_client()
