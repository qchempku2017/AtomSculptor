from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.callback_context import CallbackContext  
from google.genai import types  
from typing import Optional  

from agent_team.tools.code_graph_tools import ask_code_graph_local
from sandbox.tools import (
    sandbox_run_command,
)
from agent_team.tools.planning_tools import (
    complete_task,
    start_task,
    get_plan_summary,
    is_plan_finished,
)
from settings import settings

TOOLBOX_DIR = "toolbox/structure_modelling"



agent_description = "Structure Builder Agent specializing in atomic simulations and structure manipulations."
agent_instruction = f"""
You are an expert in atomic modelling using Python, ASE, RDKit, and Pymatgen. 
Your tasks are to build and manipulate atomic structures based on user requests and planner instructions, such as building surfaces, interfaces, supercells, etc.

Advanced structure building CLI such as interface building are available inside `{TOOLBOX_DIR}` for complex tasks. Inside the sandbox, run them with `python3`, for example `python3 {TOOLBOX_DIR}/structure_tools.py ...`. Check the `[tool]_doc.md` inside the folder for details.
**Always check the toolbox first before writing codes from scratch.**

You can use the sandbox_run_command in the runtime sandbox when coding or file operations are requested.

Also, you can ask the code graph for usage about packages like PyMatgen, ASE, RDKit, etc. using the ask_code_graph_local tool if needed.
If you are not sure, or get errors while writing codes, ask the code graph for help.

Save the structures in only one format (default to .extxyz or .xyz), and do not render or visualize the structures if not directly required.
"""

# clean up any temporary files you created during the process, and only return the final structure file path or relevant information to the user.


structure_builder = Agent(
    model=LiteLlm(settings.STRUCTURE_BUILDER_MODEL),
    name="structure_builder",
    description=agent_description,
    instruction=agent_instruction,
    tools=[
        ask_code_graph_local,
        sandbox_run_command,
        get_plan_summary,
        start_task,
        complete_task,
        is_plan_finished,
    ],
    output_key="last_structure_builder_result",
)
