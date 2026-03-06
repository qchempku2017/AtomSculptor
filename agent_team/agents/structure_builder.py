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
from agent_team.tools.planning_tools import (
    complete_task,
    get_plan_summary,
    is_plan_finished,
)
from settings import settings



agent_description = "Structure Builder Agent specializing in atomic simulations and structure manipulations using ASE."
agent_instruction = """
You are a structure builder agent specializing in atomic simulations and structure manipulations using ASE.
Your primary role is to assist the planner agent by performing tasks related to building, modifying, and analyzing atomic structures based on user requests and planner instructions.

You can use the sandbox tools to inspect, create, modify, and delete files in the runtime sandbox when coding or file operations are requested.

If you need material structures during your work, request them from the planner (you are being called by the planner, so communicate any additional needs).
"""



structure_builder = Agent(
    model=LiteLlm(settings.STRUCTURE_BUILDER_MODEL),
    name="structure_builder",
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
        get_plan_summary,
        complete_task,
        is_plan_finished
    ],
    output_key="last_structure_builder_result",
)
