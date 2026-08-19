"""Environment-backed application configuration."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
# Resolve the project-local file explicitly so launching `python app.py` from a
# parent folder cannot silently load a different .env file.
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.2"))
    AI_MAX_CONTEXT_MESSAGES = int(os.getenv("AI_MAX_CONTEXT_MESSAGES", "6"))
    OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))
    DEMO_ACCOUNTS = {
        "rahul": {
            "name": "Rahul",
            "role": "student",
            "password": os.getenv("DEMO_RAHUL_PASSWORD"),
        },
        "mrs-sharma": {
            "name": "Mrs. Sharma",
            "role": "parent",
            "password": os.getenv("DEMO_SHARMA_PASSWORD"),
        },
        "mr-patil": {
            "name": "Mr. Patil",
            "role": "teacher",
            "password": os.getenv("DEMO_PATIL_PASSWORD"),
        },
        "dr-deshmukh": {
            "name": "Dr. Deshmukh",
            "role": "principal",
            "password": os.getenv("DEMO_DESHMUKH_PASSWORD"),
        },
    }
