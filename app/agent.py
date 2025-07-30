import os
from typing import Dict, Any, Optional

from google.adk.agents import Agent

from . import prompt

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
    sub_agents=[
        component_validation_agent,
        arqcor_form_agent,
        version_check_agent,
        code_validation_agent
    ]
)
