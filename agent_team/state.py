"""
Shared state module for the agent team.
Contains singleton instances of shared state like TodoFlow.
"""
from agent_team.planning.todo_flow import TodoFlow

# Singleton instance - safe to import anywhere without circular imports
todo_flow = TodoFlow()
