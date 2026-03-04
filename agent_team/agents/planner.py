from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


from sandbox.tools import (
    sandbox_create_directory,
    sandbox_delete_path,
    sandbox_list_files,
    sandbox_read_file,
    sandbox_status,
    sandbox_write_file,
)
from settings import settings



agent_description = "Planner that manages a specialized team of agents for materials science tasks."
agent_instruction = """
You are the Planner orchestrating a specialized team for materials science research. You have four specialist sub-agents available:
1. 'mp_agent': Searches and downloads material structures from Materials Project. 
2. 'structure_agent': Performs atomic simulations and structure manipulations using ASE. 
3. 'vision_agent': Visually analyzes and inspects atomic structure images. 

Your job is to understand user requests and delegate them to the most appropriate agent(s).
Analyze what the user is asking for and route the request accordingly. 
If multiple agents are needed, you can request information from multiple agents sequentially. 
For complex tasks, please write a clear TODO list and guide the sub-agents for handling them. 
Provide clear, synthesized responses to the user based on the agents' results.
The user may provide structure files or other inputs inside the 'inputs' directory. So you can check there if needed.
You can use sandbox tools to inspect, create, modify, and delete files in the runtime sandbox when coding or file operations are requested.
"""



planner = Agent(
    model=LiteLlm(settings.PLANNER_MODEL),
    name="agentom",
    description=agent_description,
    instruction=agent_instruction,
    tools=[
        sandbox_status,
        sandbox_list_files,
        sandbox_read_file,
        sandbox_write_file,
        sandbox_create_directory,
        sandbox_delete_path,
    ],
    # sub_agents=[structure_agent, mp_agent],
    output_key="last_planner_result",
)
