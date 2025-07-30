"""Component Validation Subagent for architectural compliance.

This subagent is responsible for validating that all components in a ticket
are approved in the Technical Vision (VT). It handles the critical first stage
of the FEITO CONFERIDO validation process.
"""

import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from typing import Dict, Any

from . import prompt

USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"

if USE_MOCK:
    from ...tools.mock.tools_mocked import (
        get_jira_ticket,
        validate_pdi_components,
        validate_components_in_vt
    )
else:
    from ...tools.integrations.jira import (
        get_jira_ticket,
        validate_pdi_components
    )
    
    from ...tools.integrations.blizzdesign import validate_components_in_vt


async def validate_components_stage(
    ticket_id: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Execute component validation stage.
    
    Validates that all components in the ticket are approved in the
    Technical Vision (VT).
    
    Args:
        ticket_id: Jira ticket identifier (PDI or JT).
        tool_context: ADK tool context for state management.
        
    Returns:
        Dictionary containing validation results with status, errors,
        warnings, and component information.
    """
    try:
        # Get ticket information
        ticket_info = await get_jira_ticket(ticket_id, tool_context)
        
        if "error" in ticket_info:
            return {
                "status": "FAILED",
                "error": f"Failed to retrieve ticket: {ticket_info['error']}",
                "components": []
            }
        
        # Validate PDI components if it's a PDI ticket
        if ticket_id.startswith("PDI-"):
            pdi_validation = await validate_pdi_components(ticket_id, tool_context)
            
            if not pdi_validation.get("is_valid", False):
                warnings = pdi_validation.get("warnings", [])
                
                # Check for critical errors
                if any("status" in w and ("done" in w.lower() or "concluído" in w.lower()) 
                      for w in warnings):
                    return {
                        "status": "FAILED",
                        "error": "PDI has completed status - cannot proceed",
                        "warnings": warnings,
                        "components": []
                    }
                
                return {
                    "status": "WARNING",
                    "warnings": warnings,
                    "components": ticket_info.get("components", [])
                }
        
        # Validate components against VT
        components = ticket_info.get("components", [])
        
        if not components:
            return {
                "status": "FAILED",
                "error": "No components found in ticket",
                "components": []
            }
        
        vt_validation = await validate_components_in_vt(ticket_id, components, tool_context)
        
        if "error" in vt_validation:
            return {
                "status": "FAILED",
                "error": f"VT validation error: {vt_validation['error']}",
                "components": components
            }
        
        if not vt_validation.get("is_valid", False):
            unapproved = vt_validation.get("unapproved_components", [])
            return {
                "status": "FAILED",
                "error": f"Components not approved in VT: {', '.join(unapproved)}",
                "unapproved_components": unapproved,
                "components": components
            }
        
        return {
            "status": "SUCCESS",
            "components": components,
            "message": "All components validated successfully against VT"
        }
        
    except Exception as e:
        return {
            "status": "FAILED",
            "error": f"Unexpected error during component validation: {str(e)}",
            "components": []
        }


# Component Validation Subagent Configuration
component_validation_agent = Agent(
    name="component_validation_subagent",
    model="gemini-2.5-flash",
    description="Subagente especializado para validar componentes arquitetônicos em relação à Visão Técnica.",
    instruction=prompt.COMPONENT_VALIDATION_PROMPT,
    tools=[validate_components_stage]
)
