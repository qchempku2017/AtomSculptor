"""
Shared state module for the agent team.
Contains singleton instances of shared state like TodoFlow.
"""
from agent_team.planning.todo_flow import TodoFlow


todo_flow = TodoFlow()
