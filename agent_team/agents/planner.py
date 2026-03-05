from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


from sandbox.tools import (
    sandbox_create_directory,
    sandbox_delete_path,
    sandbox_list_files,
    sandbox_read_file,
    sandbox_run_command,
    sandbox_status,
    sandbox_write_file,
)
from agent_team.tools.state_management_tools import (
    change_state,
)
from settings import settings
from agent_team.agents.structure_builder import structure_builder
from agent_team.agents.mp_searcher import mp_searcher



agent_description = "Planner that manages a specialized team of agents for materials science tasks."
agent_instruction = """
You are the Planner orchestrating a specialized team for materials science research. You have two specialist sub-agents available:
- **structure_builder**: For building and manipulating atomic structures using ASE
- **mp_searcher**: For searching and downloading materials from Materials Project

**Decision Making:**
1. For simple queries or general conversation: Respond directly WITHOUT changing workflow state.
2. For tasks requiring sub-agents:
   - **If ONLY material search is needed**: Call mp_searcher directly
   - **If ONLY structure building is needed**: Call structure_builder directly
   - **If materials search THEN structure building**: Call mp_searcher first, then structure_builder
   - **Only call what's actually needed** - don't call agents unnecessarily to save tokens
3. After delegating work:
   - Review the results
   - Use `change_state(state_name="to_human", state_value="true")` to return results to user
   - Or continue with more work if needed

**State Management:**
- Use `change_state(state_name="current_stage", state_value="modelling")` to signal the orchestrator that modelling work is in progress
- Only do this if you're delegating to sub-agents and want the full modelling workflow
- For simple sub-agent calls during planning, you don't need to change the stage
"""



planner = Agent(
    model=LiteLlm(settings.PLANNER_MODEL),
    name="planner",
    description=agent_description,
    instruction=agent_instruction,
    tools=[
        sandbox_status,
        sandbox_list_files,
        sandbox_read_file,
        sandbox_write_file,
        sandbox_create_directory,
        sandbox_delete_path,
        sandbox_run_command,
        change_state,
    ],
    sub_agents=[structure_builder, mp_searcher],
    output_key="last_planner_result",
)
