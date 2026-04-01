"""Background runner for the note-aggregation agent.

Monitors the notes directory and triggers the aggregator agent when the
note count reaches a threshold.  All status tracking lives here so the
orchestrator stays focused on stage management.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent_team.agents.aggregator import aggregator

logger = logging.getLogger(__name__)

_NOTES_DIR = Path(__file__).parent / "memories" / "notes"
MAX_NUM_NOTES = 10

_task: asyncio.Task | None = None

_status: dict = {
    "running": False,
    "note_count": 0,
    "threshold": MAX_NUM_NOTES,
    "message": "Idle",
    "last_started_at": None,
    "last_completed_at": None,
    "last_error": None,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_status() -> dict:
    """Return a snapshot of the aggregator's current status."""
    return dict(_status)


def _note_count() -> int:
    return len(list(_NOTES_DIR.glob("*.md"))) if _NOTES_DIR.exists() else 0


def maybe_trigger() -> None:
    """Start background aggregation if the note count has reached the threshold."""
    global _task
    count = _note_count()
    _status.update(note_count=count, threshold=MAX_NUM_NOTES)
    if count >= MAX_NUM_NOTES and (_task is None or _task.done()):
        _task = asyncio.create_task(_run())


async def _run() -> None:
    """Run the aggregator agent autonomously in the background."""
    _status.update(
        running=True,
        message="Aggregating notes into instructions...",
        last_started_at=_now_iso(),
        last_error=None,
    )
    logger.info("Auto-aggregation triggered.")
    try:
        session_service = InMemorySessionService()
        runner = Runner(
            agent=aggregator,
            app_name="aggregator_bg",
            session_service=session_service,
        )
        session = await session_service.create_session(
            app_name="aggregator_bg", user_id="system"
        )
        message = types.Content(
            role="user",
            parts=[types.Part(text=(
                "Please read all current notes, aggregate them into reusable "
                "task-specific instructions, and update the instruction files."
            ))],
        )
        async for _ in runner.run_async(
            user_id="system",
            session_id=session.id,
            new_message=message,
        ):
            pass
        _status.update(
            running=False,
            message="Aggregation complete.",
            last_completed_at=_now_iso(),
            last_error=None,
        )
        logger.info("Auto-aggregation completed.")
    except Exception as exc:
        _status.update(
            running=False,
            message="Aggregation failed.",
            last_completed_at=_now_iso(),
            last_error=str(exc),
        )
        logger.exception("Auto-aggregation failed.")
