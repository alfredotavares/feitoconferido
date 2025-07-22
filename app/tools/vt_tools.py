"""VT/BlizzDesign integration tools for Feito/Conferido agent.

Provides tools for interacting with Technical Vision (VT) and
BlizzDesign to validate approved components and architectures.
"""

from typing import Dict, List, Any, Optional
from google.adk.tools import ToolContext

from ..utils.http_clients import get_vt_client
from ..utils.formatters import extract_blizzdesign_components
from ..config.settings import get_settings


async def get_technical_vision_by_ticket(ticket_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieves Technical Vision associated with a ticket.

    Searches for the VT linked to the specified Jira ticket.

    Args:
        ticket_id: The Jira ticket identifier.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - vt_id: Technical Vision identifier
            - name: VT name
            - architecture: Architecture type
            - approved_components: List of approved component names
            - approval_date: When VT was approved
            - error: Error message if retrieval failed

    Example:
        >>> result = await get_technical_vision_by_ticket("PDI-12345", tool_context)
        >>> print(result)
        {
            "vt_id": "VT-2024-001",
            "name": "User Management System",
            "architecture": "Microservices",
            "approved_components": ["user-service", "auth-module", "notification-service"],
            "approval_date": "2024-01-10"
        }
    """
    try:
        client = await get_vt_client()
        
        # Search for VT by ticket ID
        params = {"ticket_id": ticket_id}
        response = await client.get("/visions/search", params=params)
        results = response.json().get("results", [])
        
        if not results:
            return {
                "ticket_id": ticket_id,
                "error": "No Technical Vision found for this ticket"
            }
        
        # Get the most recent VT
        vt_data = results[0]
        vt_id = vt_data.get("vision_id")
        
        # Fetch full VT details
        response = await client.get(f"/visions/{vt_id}")
        vt_details = response.json()
        
        # Extract approved components
        components = vt_details.get("approved_components", [])
        if isinstance(components, str):
            components = [c.strip() for c in components.split(",") if c.strip()]
        
        # Store in context for later use
        tool_context.state[f"vt_{ticket_id}"] = {
            "vt_id": vt_id,
            "architecture": vt_details.get("architecture_type", ""),
            "approved_components": components
        }
        
        return {
            "vt_id": vt_id,
            "name": vt_details.get("name", ""),
            "architecture": vt_details.get("architecture_type", ""),
            "approved_components": components,
            "approval_date": vt_details.get("approval_date", ""),
            "valid_until": vt_details.get("valid_until", "")
        }
        
    except Exception as e:
        return {
            "ticket_id": ticket_id,
            "error": f"Failed to fetch Technical Vision: {str(e)}"
        }


async def validate_components_in_vt(
    ticket_id: str, 
    components: List[str], 
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Validates that all components are approved in the Technical Vision.

    Checks each component against the approved list in the VT.
    This is the critical validation that can lead to rejection.

    Args:
        ticket_id: The Jira ticket identifier.
        components: List of component names to validate.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - is_valid: Boolean indicating if all components are approved
            - unapproved_components: List of components not in VT
            - approved_components: List of approved components
            - vt_id: Technical Vision ID used for validation
            - error: Error message if validation failed

    Example:
        >>> result = await validate_components_in_vt(
        ...     "PDI-12345",
        ...     ["user-service", "auth-module", "payment-service"],
        ...     tool_context
        ... )
        >>> print(result)
        {
            "is_valid": False,
            "unapproved_components": ["payment-service"],
            "approved_components": ["user-service", "auth-module"],
            "vt_id": "VT-2024-001"
        }
    """
    try:
        # Check if we already have VT data in state
        vt_state = tool_context.state.get(f"vt_{ticket_id}")
        
        if not vt_state:
            # Fetch VT data
            vt_info = await get_technical_vision_by_ticket(ticket_id, tool_context)
            
            if "error" in vt_info:
                return vt_info
            
            vt_state = {
                "vt_id": vt_info["vt_id"],
                "approved_components": vt_info["approved_components"]
            }
        
        approved_components = vt_state["approved_components"]
        vt_id = vt_state["vt_id"]
        
        # Check each component
        unapproved_components = []
        approved_in_vt = []
        
        for component in components:
            if component in approved_components:
                approved_in_vt.append(component)
            else:
                unapproved_components.append(component)
        
        is_valid = len(unapproved_components) == 0
        
        # Store validation result
        tool_context.state[f"vt_validation_{ticket_id}"] = {
            "is_valid": is_valid,
            "unapproved_components": unapproved_components
        }
        
        return {
            "is_valid": is_valid,
            "unapproved_components": unapproved_components,
            "approved_components": approved_in_vt,
            "vt_id": vt_id
        }
        
    except Exception as e:
        return {
            "ticket_id": ticket_id,
            "error": f"Failed to validate components in VT: {str(e)}"
        }


async def get_blizzdesign_export(jt_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieves BlizzDesign export data for a JT.

    Fetches the technical architecture export from BlizzDesign
    containing detailed component and relationship information.

    Args:
        jt_id: The JT (Jornada Técnica) identifier.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - jt_id: The JT identifier
            - components: List of components with stereotypes
            - element_count: Total number of elements
            - relationship_count: Total number of relationships
            - raw_data: Complete BlizzDesign export (if needed)
            - error: Error message if retrieval failed

    Example:
        >>> result = await get_blizzdesign_export("JT-147338", tool_context)
        >>> print(result)
        {
            "jt_id": "JT-147338",
            "components": [
                {"name": "caapi-hubd-base-avaliacao-v1", "stereotype": "NOVO"},
                {"name": "flutmicro-hubd-base-app-rating", "stereotype": "ALTERADO"}
            ],
            "element_count": 33,
            "relationship_count": 46
        }
    """
    try:
        # For this implementation, we'll simulate the BlizzDesign API
        # In production, this would be an actual API call
        
        # Example of what the API call would look like:
        # client = await get_vt_client()
        # response = await client.get(f"/blizzdesign/export/{jt_id}")
        # blizzdesign_data = response.json()
        
        # For now, return a structured response based on the example data
        # This would be replaced with actual API integration
        
        return {
            "jt_id": jt_id,
            "error": "BlizzDesign integration not yet implemented. Please use manual export."
        }
        
    except Exception as e:
        return {
            "jt_id": jt_id,
            "error": f"Failed to fetch BlizzDesign export: {str(e)}"
        }


async def parse_blizzdesign_data(
    blizzdesign_json: Dict[str, Any], 
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Parses BlizzDesign export data to extract component information.

    Processes the raw BlizzDesign JSON export to extract relevant
    component details for validation.

    Args:
        blizzdesign_json: Raw BlizzDesign export data.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - view_name: Name of the technical view
            - jt_id: JT identifier from the view
            - components: List of application components
            - new_components: Components with NOVO stereotype
            - modified_components: Components with ALTERADO stereotype
            - removed_components: Components with REMOVIDO stereotype
            - maintained_components: Components with MANTIDO stereotype

    Example:
        >>> data = {
        ...     "viewInfo": {"name": "Visão Técnica - NPS", "JT": "JT-147338"},
        ...     "elements": [...],
        ...     "metadata": {"elementCount": 33}
        ... }
        >>> result = await parse_blizzdesign_data(data, tool_context)
        >>> print(result["new_components"])
        ["caapi-hubd-base-avaliacao-v1", "sboot-hubd-base-atom-avaliacao"]
    """
    try:
        view_info = blizzdesign_json.get("viewInfo", {})
        view_name = view_info.get("name", "Unknown")
        jt_id = view_info.get("JT", "")
        
        # Extract components
        components = extract_blizzdesign_components(blizzdesign_json)
        
        # Group by stereotype
        new_components = []
        modified_components = []
        removed_components = []
        maintained_components = []
        
        for comp in components:
            name = comp["name"]
            stereotype = comp["stereotype"]
            
            if stereotype == "NOVO":
                new_components.append(name)
            elif stereotype == "ALTERADO":
                modified_components.append(name)
            elif stereotype == "REMOVIDO":
                removed_components.append(name)
            elif stereotype == "MANTIDO":
                maintained_components.append(name)
        
        # Store parsed data in context
        tool_context.state[f"blizzdesign_{jt_id}"] = {
            "components": components,
            "new_components": new_components,
            "modified_components": modified_components
        }
        
        return {
            "view_name": view_name,
            "jt_id": jt_id,
            "components": components,
            "new_components": new_components,
            "modified_components": modified_components,
            "removed_components": removed_components,
            "maintained_components": maintained_components,
            "total_components": len(components)
        }
        
    except Exception as e:
        return {
            "error": f"Failed to parse BlizzDesign data: {str(e)}"
        }


async def get_openapi_contract(
    vt_id: str, 
    component_name: str, 
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Retrieves OpenAPI contract for a component from VT.

    Fetches the approved API specification for validation.

    Args:
        vt_id: Technical Vision identifier.
        component_name: Name of the component.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - component: Component name
            - has_contract: Boolean indicating if contract exists
            - contract: OpenAPI specification if found
            - error: Error message if retrieval failed

    Example:
        >>> result = await get_openapi_contract("VT-2024-001", "user-service", tool_context)
        >>> print(result)
        {
            "component": "user-service",
            "has_contract": True,
            "contract": {"openapi": "3.0.0", "info": {...}, "paths": {...}}
        }
    """
    try:
        client = await get_vt_client()
        
        response = await client.get(f"/visions/{vt_id}/contracts/{component_name}")
        
        if response.status_code == 404:
            return {
                "component": component_name,
                "has_contract": False
            }
        
        contract = response.json()
        
        return {
            "component": component_name,
            "has_contract": True,
            "contract": contract
        }
        
    except Exception as e:
        return {
            "component": component_name,
            "error": f"Failed to fetch OpenAPI contract: {str(e)}"
        }