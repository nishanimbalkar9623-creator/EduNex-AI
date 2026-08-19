"""Short-lived, session-backed chat context with a conservative size limit."""

from __future__ import annotations

from flask import session
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

_SESSION_KEY = "chat_history"
_MAX_ITEM_CHARS = 600


def get_history(max_messages: int) -> list[BaseMessage]:
    """Hydrate validated, bounded history from the authenticated browser session."""
    raw_history = session.get(_SESSION_KEY, [])
    history: list[BaseMessage] = []
    for item in raw_history[-max_messages:]:
        if not isinstance(item, dict) or item.get("role") not in {"user", "assistant"}:
            continue
        content = str(item.get("content", ""))[:_MAX_ITEM_CHARS]
        history.append(HumanMessage(content=content) if item["role"] == "user" else AIMessage(content=content))
    return history


def add_turn(message: str, response: str, max_messages: int) -> None:
    """Persist only a small recent window; permanent memory is intentionally deferred."""
    history = session.get(_SESSION_KEY, [])
    if not isinstance(history, list):
        history = []
    history.extend(
        [
            {"role": "user", "content": message[:_MAX_ITEM_CHARS]},
            {"role": "assistant", "content": response[:_MAX_ITEM_CHARS]},
        ]
    )
    session[_SESSION_KEY] = history[-max_messages:]
    session.modified = True


def clear_history() -> None:
    """Remove the current user's temporary chat context."""
    session.pop(_SESSION_KEY, None)
