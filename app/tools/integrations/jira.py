"""Jira integration tools for Feito/Conferido agent.

Provides tools for interacting with Jira to fetch tickets,
extract components, and update ticket information.
"""

from typing import Dict, Any
from google.adk.tools import ToolContext

from ...utils.http_clients import get_jira_client
from ...utils.formatters import parse_jira_components, parse_development_cycle
from ...config.settings import get_settings


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
            - ticket_key: The ticket key from Jira
            - summary: Ticket summary/title
            - description: Ticket description
            - status: Current ticket status
            - status_category: Status category name
            - assignee: Assigned user display name
            - reporter: Reporter user display name
            - priority: Priority name if available
            - components: List of component names
            - development_cycle: Development cycle information
            - pdi_description: PDI description from custom field
            - arqcor_id: Associated ARQCOR ID if any
            - error: Error message if retrieval failed

    Example:
        >>> result = await get_jira_ticket("PDI-12345", tool_context)
        >>> print(result)
        {
            "ticket_id": "10001",
            "ticket_key": "PDI-12345",
            "summary": "Deploy new user service",
            "status": "In Progress",
            "status_category": "In Progress",
            "assignee": "João Silva",
            "components": ["user-service", "auth-module"],
            "development_cycle": "Sprint 23",
            "pdi_description": "Deploy user-service and auth-module...",
            "arqcor_id": "ARQCOR-123"
        }
    """
    settings = get_settings().jira
    
    try:
        client = await get_jira_client()
        
        # Build URL with required fields
        params = {
            "fields": f"summary,description,assignee,reporter,priority,status,"
                     f"{settings.components_field},{settings.description_field},"
                     f"{settings.arqcor_field},customfield_10101",  # Development cycle field
            "expand": "renderedFields"
        }
        
        response = await client.get(f"/rest/api/2/issue/{ticket_id}", params=params)
        data = response.json()
        
        # Extract main ticket data
        ticket_id_internal = data.get("id", "")
        ticket_key = data.get("key", "")
        fields = data.get("fields", {})
        
        # Extract basic fields
        summary = fields.get("summary", "")
        description = fields.get("description", "")
        
        # Extract status information
        status_obj = fields.get("status", {})
        status = status_obj.get("name", "Unknown")
        status_category = status_obj.get("statusCategory", {}).get("name", "Unknown")
        
        # Extract assignee and reporter
        assignee_obj = fields.get("assignee")
        assignee = assignee_obj.get("displayName", "") if assignee_obj else ""
        
        reporter_obj = fields.get("reporter")
        reporter = reporter_obj.get("displayName", "") if reporter_obj else ""
        
        # Extract priority
        priority_obj = fields.get("priority")
        priority = priority_obj.get("name", "") if priority_obj else ""
        
        # Extract components
        components_raw = fields.get(settings.components_field, [])
        components = parse_jira_components(components_raw)
        
        # Extract development cycle
        cycle_raw = fields.get("customfield_10101", "")
        development_cycle = parse_development_cycle(cycle_raw)
        
        # Extract custom fields
        pdi_description = fields.get(settings.description_field, "")
        arqcor_id = fields.get(settings.arqcor_field, "")
        
        # Store ticket info in context state for later use
        tool_context.state[f"jira_ticket_{ticket_key}"] = {
            "summary": summary,
            "components": components,
            "development_cycle": development_cycle,
            "status": status
        }
        
        return {
            "ticket_id": ticket_id_internal,
            "ticket_key": ticket_key,
            "summary": summary,
            "description": description,
            "status": status,
            "status_category": status_category,
            "assignee": assignee,
            "reporter": reporter,
            "priority": priority,
            "components": components,
            "development_cycle": development_cycle,
            "pdi_description": pdi_description,
            "arqcor_id": arqcor_id
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
        pdi_description = ticket_info.get("pdi_description", "").lower()
        status = ticket_info.get("status", "")
        status_category = ticket_info.get("status_category", "")
        
        warnings = []
        components_not_in_description = []
        
        # Check if status is Done or Concluído
        if status.lower() in ["done", "concluído"] or status_category.lower() == "done":
            warnings.append(f"PDI has status '{status}' - cannot proceed with completed PDI")
        
        # Check if all components are mentioned in description
        for component in components:
            if component.lower() not in pdi_description:
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
            - ticket_key: The ticket key from Jira
            - status: ARQCOR ticket status
            - status_category: Status category name
            - jt_field: Value of JT field
            - is_valid: Boolean indicating if ARQCOR is valid for processing
            - error: Error message if retrieval failed

    Example:
        >>> result = await get_arqcor_ticket("ARQCOR-123", tool_context)
        >>> print(result)
        {
            "arqcor_id": "10002",
            "ticket_key": "ARQCOR-123",
            "status": "Open",
            "status_category": "To Do",
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
        
        response = await client.get(f"/rest/api/2/issue/{arqcor_id}", params=params)
        data = response.json()
        
        # Extract main ticket data
        ticket_id_internal = data.get("id", "")
        ticket_key = data.get("key", "")
        fields = data.get("fields", {})
        
        # Extract status information
        status_obj = fields.get("status", {})
        status = status_obj.get("name", "Unknown")
        status_category = status_obj.get("statusCategory", {}).get("name", "Unknown")
        
        # Extract JT field
        jt_field = fields.get(settings.jt_field, "")
        
        # Validate ARQCOR
        is_valid = True
        if not jt_field:
            is_valid = False
        if status.lower() in ["rejected", "rejeitado"] or status_category.lower() == "done":
            is_valid = False
        
        return {
            "arqcor_id": ticket_id_internal,
            "ticket_key": ticket_key,
            "status": status,
            "status_category": status_category,
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
        
        await client.post(f"/rest/api/2/issue/{ticket_id}/comment", json=data)
        
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

    """Processes Jira ticket data from API response.

    Helper function that extracts and normalizes ticket information
    from the Jira API response structure.

    Args:
        data: Ticket data object from Jira API response.

    Returns:
        Dictionary containing processed ticket information:
            - ticket_id: Internal ticket ID
            - ticket_key: Ticket key (e.g., PDI-12345)
            - summary: Ticket summary
            - description: Ticket description
            - status: Status name
            - status_category: Status category
            - assignee: Assignee display name
            - reporter: Reporter display name
            - priority: Priority name

    Example:
        >>> jira_data = {
        ...     "id": "10001",
        ...     "key": "PDI-12345",
        ...     "fields": {
        ...         "summary": "Deploy service",
        ...         "status": {"name": "In Progress", "statusCategory": {"name": "In Progress"}}
        ...     }
        ... }
        >>> result = _process_jira_ticket_data(jira_data)
        >>> print(result["ticket_key"])
        "PDI-12345"
    """
    fields = data.get("fields", {})
    
    # Extract status information
    status_obj = fields.get("status", {})
    status = status_obj.get("name", "Unknown")
    status_category = status_obj.get("statusCategory", {}).get("name", "Unknown")
    
    # Extract assignee and reporter
    assignee_obj = fields.get("assignee")
    assignee = assignee_obj.get("displayName", "") if assignee_obj else ""
    
    reporter_obj = fields.get("reporter")
    reporter = reporter_obj.get("displayName", "") if reporter_obj else ""
    
    # Extract priority
    priority_obj = fields.get("priority")
    priority = priority_obj.get("name", "") if priority_obj else ""
    
    return {
        "ticket_id": data.get("id", ""),
        "ticket_key": data.get("key", ""),
        "summary": fields.get("summary", ""),
        "description": fields.get("description", ""),
        "status": status,
        "status_category": status_category,
        "assignee": assignee,
        "reporter": reporter,
        "priority": priority
    }
