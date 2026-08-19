"""LangChain/Ollama integration and safe chat service boundary."""

from __future__ import annotations

import logging
from typing import Any

import httpx
from flask import current_app
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from ollama import ResponseError

from ai.prompts import build_system_prompt

logger = logging.getLogger(__name__)


class AIServiceUnavailable(RuntimeError):
    """Raised when the local Ollama service cannot provide a safe response."""


def get_llm() -> ChatOllama:
    """Create one reusable LangChain chat model per Flask app instance."""
    cached = current_app.extensions.get("edunex_llm")
    if cached is None:
        timeout_sec = float(current_app.config.get("OLLAMA_TIMEOUT_SECONDS", 180.0))
        cached = ChatOllama(
            model=current_app.config["OLLAMA_MODEL"],
            base_url=current_app.config["OLLAMA_BASE_URL"],
            temperature=current_app.config["AI_TEMPERATURE"],
            sync_client_kwargs={"timeout": timeout_sec},
            async_client_kwargs={"timeout": timeout_sec},
        )
        current_app.extensions["edunex_llm"] = cached
    return cached


def check_ollama_status() -> dict[str, Any]:
    """Check if the local Ollama instance is reachable and model is present."""
    base_url = current_app.config.get("OLLAMA_BASE_URL", "http://localhost:11434")
    model = current_app.config.get("OLLAMA_MODEL", "llama3.2")
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{base_url}/api/tags")
            if resp.status_code == 200:
                raw_models = resp.json().get("models", [])
                names = [m.get("name", "") for m in raw_models]
                available = any(m == model or m.startswith(f"{model}:") for m in names)
                return {"online": True, "model": model, "available": available, "models": names}
    except Exception as err:
        logger.debug("Ollama health check failed: %s", err)
    return {"online": False, "model": model, "available": False}


def generate_response(user: dict[str, str], message: str, history: list[Any]) -> str:
    """Generate a response using role context and bounded session history."""
    messages = [SystemMessage(content=build_system_prompt(user)), *history, HumanMessage(content=message)]
    
    last_error: Exception | None = None
    for attempt in range(1, 3):
        try:
            result = get_llm().invoke(messages)
            content = result.content
            if isinstance(content, list):
                content = " ".join(str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in content)
            response = str(content).strip()
            if response:
                return response
        except (httpx.HTTPError, ResponseError, OSError, ValueError) as error:
            logger.warning("Ollama chat request attempt %d failed: %s", attempt, error)
            last_error = error
        except Exception as error:
            logger.exception("Unexpected exception while calling Ollama attempt %d: %s", attempt, error)
            last_error = error

    raise AIServiceUnavailable("EduNex AI is temporarily unable to connect to its AI service. Please make sure Ollama is running and try again.") from last_error
