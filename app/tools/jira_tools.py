"""Jira integration tools for Feito/Conferido agent.

Provides tools for interacting with Jira to fetch tickets,
extract components, and update ticket information.
"""

from typing import Dict, List, Any, Optional
from google.adk.tools import ToolContext

from ..utils.http_clients import get_jira_client
from ..utils.formatters import parse_jira_components, parse_development_cycle
from ..config.settings import get_settings


async def get_jira_ticket(ticket_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieves a Jira ticket by its ID.

    Fetches ticket information including custom fields for components,
    development cycle, and ARQCOR registration.

    Args:
        ticket_id: The Jira ticket identifier (e.g., "PDI-12345").
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing ticket information:
            - ticket_id: The ticket ID
            - summary: Ticket summary/title
            - status: Current ticket status
            - components: List of component names
            - development_cycle: Development cycle information
            - description: PDI description
            - arqcor_id: Associated ARQCOR ID if any
            - error: Error message if retrieval failed

    Example:
        >>> result = await get_jira_ticket("PDI-12345", tool_context)
        >>> print(result)
        {
            "ticket_id": "PDI-12345",
            "summary": "Deploy new user service",
            "status": "In Progress",
            "components": ["user-service", "auth-module"],
            "development_cycle": "Sprint 23",
            "description": "Deploy user-service and auth-module...",
            "arqcor_id": "ARQCOR-123"
        }
    """
    settings = get_settings().jira
    
    try:
        client = await get_jira_client()
        
        # Build URL with required fields
        params = {
            "fields": f"summary,status,{settings.components_field},"
                     f"{settings.description_field},{settings.arqcor_field},"
                     f"customfield_10101",  # Development cycle field
            "expand": "renderedFields"
        }
        
        response = await client.get(f"/issue/{ticket_id}", params=params)
        data = response.json()
        
        fields = data.get("fields", {})
        
        # Extract components
        components_raw = fields.get(settings.components_field, [])
        components = parse_jira_components(components_raw)
        
        # Extract development cycle
        cycle_raw = fields.get("customfield_10101", "")
        development_cycle = parse_development_cycle(cycle_raw)
        
        # Store ticket info in context state for later use
        tool_context.state[f"jira_ticket_{ticket_id}"] = {
            "summary": fields.get("summary", ""),
            "components": components,
            "development_cycle": development_cycle
        }
        
        return {
            "ticket_id": ticket_id,
            "summary": fields.get("summary", ""),
            "status": fields.get("status", {}).get("name", "Unknown"),
            "components": components,
            "development_cycle": development_cycle,
            "description": fields.get(settings.description_field, ""),
            "arqcor_id": fields.get(settings.arqcor_field, "")
        }
        
    except Exception as e:
        return {
            "ticket_id": ticket_id,
            "error": f"Failed to fetch Jira ticket: {str(e)}"
        }


async def get_ticket_components(ticket_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Extracts components from a Jira ticket's Test and Homologation tab.

    Specifically looks for components in the custom field designated
    for Test and Homologation information.

    Args:
        ticket_id: The Jira ticket identifier.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - ticket_id: The ticket ID
            - components: List of component names
            - count: Number of components found
            - error: Error message if extraction failed

    Example:
        >>> result = await get_ticket_components("PDI-12345", tool_context)
        >>> print(result)
        {
            "ticket_id": "PDI-12345",
            "components": ["user-service", "auth-module", "notification-service"],
            "count": 3
        }
    """
    # First try to get from state if we already fetched this ticket
    state_key = f"jira_ticket_{ticket_id}"
    if state_key in tool_context.state:
        components = tool_context.state[state_key].get("components", [])
        return {
            "ticket_id": ticket_id,
            "components": components,
            "count": len(components)
        }
    
    # Otherwise fetch the ticket
    ticket_info = await get_jira_ticket(ticket_id, tool_context)
    
    if "error" in ticket_info:
        return ticket_info
    
    components = ticket_info.get("components", [])
    
    return {
        "ticket_id": ticket_id,
        "components": components,
        "count": len(components)
    }


async def validate_pdi_components(ticket_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Validates PDI components are properly documented.

    Checks that all components listed in the ticket are mentioned
    in the PDI description field.

    Args:
        ticket_id: The PDI ticket identifier.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - ticket_id: The ticket ID
            - is_valid: Boolean indicating if validation passed
            - components_not_in_description: List of components not mentioned
            - warnings: List of validation warnings
            - error: Error message if validation failed

    Example:
        >>> result = await validate_pdi_components("PDI-12345", tool_context)
        >>> print(result)
        {
            "ticket_id": "PDI-12345",
            "is_valid": False,
            "components_not_in_description": ["notification-service"],
            "warnings": ["Component 'notification-service' not mentioned in PDI description"]
        }
    """
    try:
        # Fetch ticket information
        ticket_info = await get_jira_ticket(ticket_id, tool_context)
        
        if "error" in ticket_info:
            return ticket_info
        
        components = ticket_info.get("components", [])
        description = ticket_info.get("description", "").lower()
        status = ticket_info.get("status", "")
        
        warnings = []
        components_not_in_description = []
        
        # Check if status is Done or Concluído
        if status.lower() in ["done", "concluído"]:
            warnings.append(f"PDI has status '{status}' - cannot proceed with completed PDI")
        
        # Check if all components are mentioned in description
        for component in components:
            if component.lower() not in description:
                components_not_in_description.append(component)
                warnings.append(f"Component '{component}' not mentioned in PDI description")
        
        # Check if there are no components
        if not components:
            warnings.append("No components found in PDI")
        
        is_valid = len(warnings) == 0
        
        # Store validation result in state
        tool_context.state[f"pdi_validation_{ticket_id}"] = {
            "is_valid": is_valid,
            "warnings": warnings
        }
        
        return {
            "ticket_id": ticket_id,
            "is_valid": is_valid,
            "components_not_in_description": components_not_in_description,
            "warnings": warnings
        }
        
    except Exception as e:
        return {
            "ticket_id": ticket_id,
            "error": f"Failed to validate PDI: {str(e)}"
        }


async def get_arqcor_ticket(arqcor_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieves an ARQCOR ticket from Jira.

    Fetches ARQCOR issue information including JT field and status.

    Args:
        arqcor_id: The ARQCOR ticket identifier.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - arqcor_id: The ARQCOR ID
            - status: ARQCOR ticket status
            - jt_field: Value of JT field
            - is_valid: Boolean indicating if ARQCOR is valid for processing
            - error: Error message if retrieval failed

    Example:
        >>> result = await get_arqcor_ticket("ARQCOR-123", tool_context)
        >>> print(result)
        {
            "arqcor_id": "ARQCOR-123",
            "status": "Open",
            "jt_field": "JT-147338",
            "is_valid": True
        }
    """
    settings = get_settings().jira
    
    try:
        client = await get_jira_client()
        
        params = {
            "fields": f"summary,status,{settings.jt_field}",
        }
        
        response = await client.get(f"/issue/{arqcor_id}", params=params)
        data = response.json()
        
        fields = data.get("fields", {})
        status = fields.get("status", {}).get("name", "Unknown")
        jt_field = fields.get(settings.jt_field, "")
        
        # Validate ARQCOR
        is_valid = True
        if not jt_field:
            is_valid = False
        if status.lower() in ["rejected", "rejeitado"]:
            is_valid = False
        
        return {
            "arqcor_id": arqcor_id,
            "status": status,
            "jt_field": jt_field,
            "is_valid": is_valid
        }
        
    except Exception as e:
        return {
            "arqcor_id": arqcor_id,
            "error": f"Failed to fetch ARQCOR ticket: {str(e)}"
        }


async def update_ticket_comment(ticket_id: str, comment: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Adds a comment to a Jira ticket.

    Posts a comment to the specified ticket, useful for recording
    validation results or manual action requirements.

    Args:
        ticket_id: The Jira ticket identifier.
        comment: Comment text to add.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - ticket_id: The ticket ID
            - success: Boolean indicating if comment was added
            - error: Error message if operation failed

    Example:
        >>> result = await update_ticket_comment(
        ...     "PDI-12345",
        ...     "Feito/Conferido validation completed successfully",
        ...     tool_context
        ... )
        >>> print(result)
        {"ticket_id": "PDI-12345", "success": True}
    """
    try:
        client = await get_jira_client()
        
        data = {"body": comment}
        
        await client.post(f"/issue/{ticket_id}/comment", json=data)
        
        return {
            "ticket_id": ticket_id,
            "success": True
        }
        
    except Exception as e:
        return {
            "ticket_id": ticket_id,
            "success": False,
            "error": f"Failed to add comment: {str(e)}"
        }