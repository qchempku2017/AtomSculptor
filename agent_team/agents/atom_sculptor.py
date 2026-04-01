from __future__ import annotations

import logging
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

from agent_team import aggregator_runner
from agent_team.agents.planner import planner

logger = logging.getLogger(__name__)

# Re-export so existing consumers (e.g. web_gui) keep working.
get_aggregator_status = aggregator_runner.get_status

# ── State keys & values ──────────────────────────────────────────────
STAGE = "current_stage"
TO_HUMAN = "to_human"
NOTE_WRITTEN = "note_written"

PLANNING = "planning"
MODELLING = "modelling"
TRUE = "true"
FALSE = "false"

MAX_ITERATIONS = 5


class Orchestrator(BaseAgent):
    """Top-level orchestrator that alternates between planning and modelling."""

    # ── state helpers ─────────────────────────────────────────────────

    @staticmethod
    def _get(ctx: InvocationContext, key: str, default: str = "") -> str:
        return ctx.session.state.get(key, default)

    @staticmethod
    def _set(ctx: InvocationContext, key: str, value: str) -> None:
        ctx.session.state[key] = value

    # ── planner delegation ────────────────────────────────────────────

    @staticmethod
    async def _run_planner(
        ctx: InvocationContext,
    ) -> AsyncGenerator[Event, None]:
        """Delegate to the planner, retrying once if the last event isn't from it."""
        event = None
        async for event in planner.run_async(ctx):
            yield event
        if event is not None and event.author != "planner":
            async for event in planner.run_async(ctx):
                yield event

    @staticmethod
    def _system_event(ctx: InvocationContext, text: str) -> Event:
        return Event(
            author="system",
            invocation_id=ctx.invocation_id,
            branch=ctx.branch,
            content=types.Content(role="user", parts=[types.Part(text=text)]),
        )

    # ── main loop ─────────────────────────────────────────────────────

    async def _run_async_impl(
        self, ctx: InvocationContext,
    ) -> AsyncGenerator[Event, None]:
        aggregator_runner.maybe_trigger()

        for _ in range(MAX_ITERATIONS):
            self._set(ctx, NOTE_WRITTEN, FALSE)
            self._set(ctx, TO_HUMAN, FALSE)
            stage = self._get(ctx, STAGE, PLANNING)

            # ── Planning stage ────────────────────────────────────
            if stage == PLANNING:
                async for event in self._run_planner(ctx):
                    yield event

                if self._get(ctx, TO_HUMAN) == TRUE:
                    return

                # Planner didn't transition to modelling → nothing to do
                if self._get(ctx, STAGE, PLANNING) == PLANNING:
                    return

                continue  # stage changed → re-enter loop as modelling

            # ── Modelling stage ───────────────────────────────────
            async for event in self._run_planner(ctx):
                yield event

            if self._get(ctx, TO_HUMAN) == TRUE:
                if self._get(ctx, NOTE_WRITTEN) != TRUE:
                    yield self._system_event(
                        ctx,
                        "Do you want to write notes for future agents "
                        "based on what you learned during this modelling phase?",
                    )
                    async for event in self._run_planner(ctx):
                        yield event
                return

            # Modelling done, no human return → loop back to planning
            self._set(ctx, STAGE, PLANNING)

        # Fallback: max iterations reached
        async for event in self._run_planner(ctx):
            yield event


atom_sculptor = Orchestrator(
    name="atom_sculptor",
    sub_agents=[planner],
)