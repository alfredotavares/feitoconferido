"""ARQCOR Form Management Subagent.

This subagent handles the creation and management of ARQCOR forms
for documenting the architectural compliance validation process.
"""

import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from typing import Dict, Any, Optional

from . import prompt

USE_MOCK_TOOLS = os.getenv("USE_MOCK_TOOLS", "false").lower() == "true"

if USE_MOCK_TOOLS:
    from ...tools.mock.tools_mocked import (
        create_arqcor_form,
        update_arqcor_form_with_versions,
        add_validation_checklist_to_form
    )
else:
    from ...tools.integrations.arqcor import (
        create_arqcor_form,
        update_arqcor_form_with_versions,
        add_validation_checklist_to_form
)


async def manage_arqcor_form(
    ticket_id: str,
    evaluator_name: str,
    operation: str,
    tool_context: ToolContext,
    form_id: Optional[str] = None,
    update_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Manage ARQCOR form operations.
    
    Handles creation, updates, and checklist additions for ARQCOR forms.
    
    Args:
        ticket_id: Jira ticket identifier.
        evaluator_name: Name of the architect performing validation.
        operation: Operation type ('create', 'update_versions', 'add_checklist').
        tool_context: ADK tool context.
        form_id: ARQCOR form ID (required for updates).
        update_data: Additional data for updates.
        
    Returns:
        Dictionary containing operation results and form information.
    """
    try:
        if operation == "create":
            result = await create_arqcor_form(ticket_id, evaluator_name, tool_context)
            
            if "error" in result:
                return {
                    "status": "FAILED",
                    "error": f"Form creation failed: {result['error']}"
                }
            
            return {
                "status": "SUCCESS",
                "form_id": result.get("form_id"),
                "form_url": result.get("form_url"),
                "message": "ARQCOR form created successfully"
            }
            
        elif operation == "update_versions" and form_id:
            result = await update_arqcor_form_with_versions(form_id, tool_context)
            
            if "error" in result:
                return {
                    "status": "WARNING",
                    "warning": f"Version update failed: {result['error']}",
                    "form_id": form_id
                }
            
            return {
                "status": "SUCCESS",
                "form_id": form_id,
                "message": "Form updated with version information"
            }
            
        elif operation == "add_checklist" and form_id and update_data:
            checklist_items = update_data.get("checklist_items", [])
            result = await add_validation_checklist_to_form(
                form_id, 
                checklist_items,
                tool_context
            )
            
            if "error" in result:
                return {
                    "status": "WARNING",
                    "warning": f"Checklist update failed: {result['error']}",
                    "form_id": form_id
                }
            
            return {
                "status": "SUCCESS", 
                "form_id": form_id,
                "message": "Validation checklist added to form"
            }
            
        else:
            return {
                "status": "FAILED",
                "error": f"Invalid operation or missing required parameters"
            }
            
    except Exception as e:
        return {
            "status": "FAILED",
            "error": f"Unexpected error in ARQCOR form management: {str(e)}"
        }


# ARQCOR Form Management Subagent Configuration
arqcor_form_agent = Agent(
    name="arqcor_form_subagent",
    model="gemini-2.5-flash",
    description="Subagente especializado para gerenciamento de formulários de conformidade do ARQCOR.",
    instruction=prompt.ARQCOR_FORM_PROMPT,
    tools=[manage_arqcor_form]
)
