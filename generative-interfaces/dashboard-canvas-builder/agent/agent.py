from __future__ import annotations

# ADK imports
from ag_ui_adk import ADKAgent
from google.adk.assistants import Assistant
from google.adk.assistants.callback_context import CallbackContext
from google.adk.tools import google_search, FunctionTool
from google.adk.tools.agent_tool import AgentTool

# Local imports
from modifiers import before_model, after_model
from tools import tools
from instructions import instruction_provider

def on_before_agent(callback_context: CallbackContext):
  """
    Process inputs and produce structured outputs.
    """
  return None

search_agent = Assistant(
    model='gemini-3.5-flash',
    name='SearchAgent',
    instruction="""
    Process inputs and produce structured outputs.
    """,
    tools=[google_search],
)

dashboard_agent = Assistant(
  name="DashboardAgent",
  model="gemini-3.5-flash",
  tools=tools + [AgentTool(assistant=search_agent)],

  # run-loop modifiers
  before_agent_callback=on_before_agent,
  before_model_callback=before_model,
  after_model_callback = after_model,
  
  # system instructions
  instruction=instruction_provider,
)

# Create ADK middleware assistant instance
dashboard_agent = ADKAgent(
  adk_agent=dashboard_agent,
  service_name="dashboard_app",
  account_id="demo_user",
  session_timeout_seconds=3600,
  use_in_memory_services=True
)
