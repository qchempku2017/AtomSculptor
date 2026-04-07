"""In-memory session registry — stores chat history and metadata per ADK session."""

from datetime import datetime, timezone

_sessions: dict[str, dict] = {}  # session_id -> {id, name, messages, created_at}
_order: list[str] = []           # insertion order


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def register(session_id: str, name: str) -> dict:
    """Register a new session entry. Returns the entry."""
    entry = {
        "id": session_id,
        "name": name,
        "messages": [],
        "created_at": _now(),
    }
    _sessions[session_id] = entry
    if session_id not in _order:
        _order.append(session_id)
    return entry


def list_sessions() -> list[dict]:
    """Return sessions in creation order (oldest first), without message payloads."""
    return [
        {
            "id": _sessions[sid]["id"],
            "name": _sessions[sid]["name"],
            "created_at": _sessions[sid]["created_at"],
        }
        for sid in _order
        if sid in _sessions
    ]


def add_message(session_id: str, msg: dict) -> None:
    if session_id in _sessions:
        _sessions[session_id]["messages"].append(msg)


def get_messages(session_id: str) -> list[dict]:
    if session_id in _sessions:
        return list(_sessions[session_id]["messages"])
    return []


def delete(session_id: str) -> bool:
    if session_id in _sessions:
        del _sessions[session_id]
        try:
            _order.remove(session_id)
        except ValueError:
            pass
        return True
    return False


def rename(session_id: str, name: str) -> bool:
    if session_id in _sessions:
        _sessions[session_id]["name"] = name
        return True
    return False


def clear() -> None:
    _sessions.clear()
    _order.clear()


def _next_name() -> str:
    n = len(_order) + 1
    return f"Session {n}"
