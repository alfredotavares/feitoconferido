import os
from typing import Dict, Any, Optional

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from .tools.utils.datetime_tool import get_current_datetime

from app.sub_agents import (
    component_validation_agent,
    arqcor_form_agent,
    version_check_agent,
    code_validation_agent
)

MODEL: str = os.getenv("VERTEX_AI_MODEL", "gemini-2.5-flash")

root_agent = Agent(
    name="feito_conferido_coordinator",
    model=MODEL,
    description="Core orchestrator for architectural compliance validation using specialized subagents.",
    instruction=prompt.FEITO_CONFERIDO_AGENT_PROMPT,
    tools=[
        AgentTool(agent=component_validation_agent),
        AgentTool(agent=arqcor_form_agent),
        AgentTool(agent=version_check_agent),
        AgentTool(agent=code_validation_agent),
        get_current_datetime
    ]
)
