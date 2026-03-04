from agent_team.agents.planner import planner
from sandbox import AgentSandbox
from settings import settings

sandbox = AgentSandbox(**settings.get_sandbox_client_kwargs())
sandbox.add(planner)

root_agent = planner
