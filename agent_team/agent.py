from agent_team.agents.planner import planner
from sandbox import Sandbox
from settings import settings

sandbox = Sandbox(settings.SANDBOX_DIR)
sandbox.add_agent(planner)

root_agent = planner
