"""Shared state module for the agent team.

Backward-compatible convenience aliases — prefer importing from
`agent_team.context` directly for new code.
"""
from agent_team.context import get_context

_ctx = get_context()

#: Convenience alias so existing ``from agent_team.state import todo_flow``
#: continues to work.  Because TodoFlow.reset() mutates in-place, this
#: reference stays valid even after a reset.
todo_flow = _ctx.todo_flow
