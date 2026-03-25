"""Central runtime context for the agent team.

Instead of scattering module-level singletons across files, all shared
mutable state lives here inside `AgentContext`.  Obtain the singleton
via `get_context()`.

    from agent_team.context import get_context
    ctx = get_context()
    ctx.todo_flow.set_plan(...)
"""

from __future__ import annotations

from agent_team.planning.todo_flow import TodoFlow


class AgentContext:
    """Container for shared runtime state of the agent team.

    Add new shared state as attributes here rather than creating
    additional module-level globals elsewhere.
    """

    def __init__(self):
        self.todo_flow = TodoFlow()

    def reset(self):
        """Reset all mutable runtime state (e.g. between conversations)."""
        self.todo_flow.reset()


_instance: AgentContext | None = None


def get_context() -> AgentContext:
    """Return (and lazily create) the global AgentContext singleton."""
    global _instance
    if _instance is None:
        _instance = AgentContext()
    return _instance
