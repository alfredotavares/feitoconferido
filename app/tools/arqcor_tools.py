"""ARQCOR integration tools for Feito/Conferido agent.

Provides tools for creating and managing Solution Adherence
Evaluation forms in the ARQCOR system.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from google.adk.tools import ToolContext

from ..utils.http_clients import get_arqcor_client
from ..utils.formatters import format_validation_scope, format_version_changes
from ..config.settings import get_settings


async def create_arqcor_form(
    ticket_id: str,
    evaluator_name: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Creates a new ARQCOR evaluation form.

    Generates a Solution Adherence Evaluation form with initial
    data from the validation process.

    Args:
        ticket_id: Jira ticket identifier.
        evaluator_name: Name of the architect/evaluator.
        tool_context: ADK tool context containing validation data.

    Returns:
        Dictionary containing:
            - form_id: Generated ARQCOR form identifier
            - status: Form status (draft/submitted)
            - form_url: URL to access the form
            - error: Error message if creation failed

    Example:
        >>> result = await create_arqcor_form("PDI-12345", "João Silva", tool_context)
        >>> print(result)
        {
            "form_id": "ARQCOR-2024-001",
            "status": "draft",
            "form_url": "https://arqcor.company.com/forms/ARQCOR-2024-001"
        }
    """
    settings = get_settings().arqcor
    
    try:
        # Get validation data from context
        jira_data = tool_context.state.get(f"jira_ticket_{ticket_id}", {})
        vt_data = tool_context.state.get(f"vt_{ticket_id}", {})
        
        if not jira_data or not vt_data:
            return {
                "error": "Missing validation data. Please run component validation first."
            }
        
        # Extract required data
        development_cycle = jira_data.get("development_cycle", "")
        components = jira_data.get("components", [])
        architecture = vt_data.get("architecture", "")
        
        # Format validation scope
        validation_scope = format_validation_scope(
            development_cycle,
            architecture,
            components
        )
        
        # Prepare form data
        form_data = {
            "template_id": settings.form_template_id,
            "data": {
                "ticket_reference": ticket_id,
                "evaluation_date": datetime.utcnow().isoformat(),
                "evaluator": evaluator_name,
                "validation_scope": validation_scope,
                "development_cycle": development_cycle,
                "architecture": architecture,
                "status": "draft"
            },
            "metadata": {
                "source": "feito-conferido-agent",
                "version": "1.0"
            }
        }
        
        # Create form via API
        client = await get_arqcor_client()
        response = await client.post("/api/v1/forms", json=form_data)
        result = response.json()
        
        form_id = result.get("form_id")
        
        # Store form ID in context
        tool_context.state[f"arqcor_form_{ticket_id}"] = {
            "form_id": form_id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return {
            "form_id": form_id,
            "status": "draft",
            "form_url": f"{settings.base_url}/forms/{form_id}"
        }
        
    except Exception as e:
        return {
            "error": f"Failed to create ARQCOR form: {str(e)}"
        }


async def update_arqcor_form_with_versions(
    form_id: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Updates ARQCOR form with version change information.

    Adds the version comparison results to the validation scope
    in the ARQCOR form.

    Args:
        form_id: ARQCOR form identifier.
        tool_context: ADK tool context containing version check results.

    Returns:
        Dictionary containing:
            - form_id: ARQCOR form identifier
            - updated: Boolean indicating if update was successful
            - error: Error message if update failed

    Example:
        >>> result = await update_arqcor_form_with_versions("ARQCOR-2024-001", tool_context)
        >>> print(result)
        {"form_id": "ARQCOR-2024-001", "updated": True}
    """
    try:
        # Get version check results from context
        version_results = tool_context.state.get("version_check_results", {})
        
        if not version_results:
            return {
                "form_id": form_id,
                "error": "No version check results found. Please run version check first."
            }
        
        # Format version changes
        version_changes = version_results.get("version_changes", [])
        changes_formatted = []
        
        for change in version_changes:
            changes_formatted.append({
                "component": change["component"],
                "from_version": change["change"].split(" → ")[0] if " → " in change["change"] else "NEW",
                "to_version": change["change"].split(" → ")[1] if " → " in change["change"] else change["change"].replace("NEW → ", "")
            })
        
        version_text = format_version_changes(changes_formatted)
        
        # Get current form data
        client = await get_arqcor_client()
        response = await client.get(f"/api/v1/forms/{form_id}")
        current_form = response.json()
        
        # Update validation scope
        current_scope = current_form.get("data", {}).get("validation_scope", "")
        updated_scope = current_scope + version_text
        
        # Update form
        update_data = {
            "data": {
                "validation_scope": updated_scope
            },
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await client.patch(f"/api/v1/forms/{form_id}", json=update_data)
        
        # Store update info in context
        tool_context.state[f"arqcor_form_versions_updated_{form_id}"] = True
        
        return {
            "form_id": form_id,
            "updated": True
        }
        
    except Exception as e:
        return {
            "form_id": form_id,
            "error": f"Failed to update ARQCOR form: {str(e)}"
        }


async def submit_arqcor_form(form_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Submits an ARQCOR form for approval.

    Changes the form status from draft to submitted and triggers
    the approval workflow.

    Args:
        form_id: ARQCOR form identifier.
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - form_id: ARQCOR form identifier
            - status: New form status
            - submitted: Boolean indicating if submission was successful
            - error: Error message if submission failed

    Example:
        >>> result = await submit_arqcor_form("ARQCOR-2024-001", tool_context)
        >>> print(result)
        {"form_id": "ARQCOR-2024-001", "status": "submitted", "submitted": True}
    """
    try:
        client = await get_arqcor_client()
        
        # Update status to submitted
        update_data = {
            "data": {
                "status": "submitted",
                "submitted_at": datetime.utcnow().isoformat()
            }
        }
        
        await client.patch(f"/api/v1/forms/{form_id}", json=update_data)
        
        # Trigger submission workflow
        await client.post(f"/api/v1/forms/{form_id}/submit")
        
        return {
            "form_id": form_id,
            "status": "submitted",
            "submitted": True
        }
        
    except Exception as e:
        return {
            "form_id": form_id,
            "error": f"Failed to submit ARQCOR form: {str(e)}"
        }


async def get_arqcor_form_status(form_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieves the current status of an ARQCOR form.

    Checks the form status and approval state.

    Args:
        form_id: ARQCOR form identifier.
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - form_id: ARQCOR form identifier
            - status: Current form status
            - evaluator: Name of evaluator
            - created_at: Form creation date
            - submitted_at: Form submission date (if submitted)
            - validation_scope: Current validation scope content
            - error: Error message if retrieval failed

    Example:
        >>> result = await get_arqcor_form_status("ARQCOR-2024-001", tool_context)
        >>> print(result)
        {
            "form_id": "ARQCOR-2024-001",
            "status": "submitted",
            "evaluator": "João Silva",
            "created_at": "2024-01-15T10:00:00Z",
            "submitted_at": "2024-01-15T10:30:00Z",
            "validation_scope": "..."
        }
    """
    try:
        client = await get_arqcor_client()
        
        response = await client.get(f"/api/v1/forms/{form_id}")
        form_data = response.json()
        
        data = form_data.get("data", {})
        
        return {
            "form_id": form_id,
            "status": data.get("status", "unknown"),
            "evaluator": data.get("evaluator", ""),
            "created_at": data.get("evaluation_date", ""),
            "submitted_at": data.get("submitted_at", ""),
            "validation_scope": data.get("validation_scope", "")
        }
        
    except Exception as e:
        return {
            "form_id": form_id,
            "error": f"Failed to get ARQCOR form status: {str(e)}"
        }


async def add_validation_checklist_to_form(
    form_id: str,
    checklist_items: List[Dict[str, Any]],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Adds validation checklist results to ARQCOR form.

    Updates the form with detailed validation checklist items
    for code and contract validation results.

    Args:
        form_id: ARQCOR form identifier.
        checklist_items: List of checklist items with 'item', 'result', and 'notes'.
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - form_id: ARQCOR form identifier
            - checklist_added: Boolean indicating if checklist was added
            - error: Error message if update failed

    Example:
        >>> checklist = [
        ...     {"item": "Dependencies validated", "result": "PASS", "notes": "All approved"},
        ...     {"item": "OpenAPI contracts", "result": "FAIL", "notes": "Missing for user-service"}
        ... ]
        >>> result = await add_validation_checklist_to_form("ARQCOR-2024-001", checklist, tool_context)
        >>> print(result)
        {"form_id": "ARQCOR-2024-001", "checklist_added": True}
    """
    try:
        # Format checklist for ARQCOR
        checklist_text = "\n\nChecklist de Validação:\n"
        
        for item in checklist_items:
            status_emoji = "✅" if item["result"] == "PASS" else "❌"
            checklist_text += f"\n{status_emoji} {item['item']}"
            if item.get("notes"):
                checklist_text += f"\n   Observação: {item['notes']}"
        
        # Get current form
        client = await get_arqcor_client()
        response = await client.get(f"/api/v1/forms/{form_id}")
        current_form = response.json()
        
        # Update validation scope with checklist
        current_scope = current_form.get("data", {}).get("validation_scope", "")
        updated_scope = current_scope + checklist_text
        
        # Update form
        update_data = {
            "data": {
                "validation_scope": updated_scope,
                "checklist_completed": True
            },
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await client.patch(f"/api/v1/forms/{form_id}", json=update_data)
        
        return {
            "form_id": form_id,
            "checklist_added": True
        }
        
    except Exception as e:
        return {
            "form_id": form_id,
            "error": f"Failed to add checklist to ARQCOR form: {str(e)}"
        }