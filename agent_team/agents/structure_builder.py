from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.callback_context import CallbackContext  
from google.genai import types  
from typing import Optional  

from agent_team.tools.code_graph_tools import ask_code_graph_local
from agent_team.tools.tools_creation import (
    create_toolbox_tool,
    list_toolbox_tools,
    validate_toolbox_tool,
)
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

## Creating New Tools

When the user asks you to create a reusable tool, or when you need a tool that doesn't exist yet, use the `create_toolbox_tool` function. Provide:
- `group`: toolbox group (e.g. "structure_modelling", "analysis", or a new group name)
- `tool_name`: a snake_case name for the tool (e.g. "geometry_tools")
- `description`: a short one-line description
- `code`: the Python source code with your imports and function definitions

Each public function (not starting with `_`) becomes a CLI sub-command automatically.
Functions must accept simple types (str, int, float, bool, list, dict) and return a dict.

The following sandbox utilities are auto-imported in generated tools:
- `sandbox_root()`, `sandbox_output_dir()`, `resolve_output_path(name)`, `display_path(path)`

After creating a tool, use `validate_toolbox_tool` to confirm it works, then use it via `sandbox_run_command`.
Use `list_toolbox_tools` to see all available default and custom tools.

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
        create_toolbox_tool,
        list_toolbox_tools,
        validate_toolbox_tool,
        get_plan_summary,
        start_task,
        complete_task,
        is_plan_finished,
    ],
    output_key="last_structure_builder_result",
)
