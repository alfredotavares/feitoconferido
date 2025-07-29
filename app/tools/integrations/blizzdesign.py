"""VT/BlizzDesign integration tools for Feito/Conferido agent.

Provides tools for interacting with Technical Vision (VT) and
BlizzDesign to validate approved components and architectures.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import re
from google.adk.tools import ToolContext

from ...utils.http_clients import get_vt_client
from ...utils.formatters import extract_blizzdesign_components
from ...config.settings import get_settings


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


async def load_local_architecture_data(data_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Loads architecture data from local JSON files.

    Provides a fallback mechanism for loading architecture data from
    local files when API is unavailable or for offline validation.

    Args:
        data_dir: Directory containing architecture JSON files.
                 Defaults to 'data/' in project root.

    Returns:
        List of architecture data dictionaries with source file info.

    Example:
        >>> data = await load_local_architecture_data()
        >>> print(len(data))
        3
        >>> print(data[0]["_source_file"])
        "architecture_export_2024.json"
    """
    if data_dir is None:
        data_dir = Path("data")
    
    architecture_data = []
    
    if not data_dir.exists():
        return architecture_data
    
    for json_file in data_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['_source_file'] = json_file.name
                architecture_data.append(data)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
    
    return architecture_data


def parse_component_list_from_text(text: str) -> Dict[str, str]:
    """Extracts components and versions from user input text.

    Supports multiple formats for component specification:
    - "component -> version"
    - "component : version"
    - "component version" (space separated)

    Args:
        text: User input text containing component list.

    Returns:
        Dictionary mapping component names to versions.

    Example:
        >>> text = '''
        ... caapi-hubd-base-avaliacao-v1 -> 1.3.2
        ... flutmicro-hubd-base-app-rating: 2.0.1
        ... ng15-hubd-base-portal 1.1.1
        ... '''
        >>> result = parse_component_list_from_text(text)
        >>> print(result)
        {
            'caapi-hubd-base-avaliacao-v1': '1.3.2',
            'flutmicro-hubd-base-app-rating': '2.0.1',
            'ng15-hubd-base-portal': '1.1.1'
        }
    """
    components = {}
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Pattern: "component -> version"
        if '->' in line:
            parts = line.split('->')
            if len(parts) == 2:
                component_name = parts[0].strip()
                version = parts[1].strip()
                components[component_name] = version
        
        # Pattern: "component: version"
        elif ':' in line and not line.startswith('{'):
            parts = line.split(':', 1)
            if len(parts) == 2:
                component_name = parts[0].strip()
                version = parts[1].strip()
                components[component_name] = version
        
        # Pattern: "component version" (last word is version)
        else:
            parts = line.split()
            if len(parts) >= 2 and re.match(r'^\d+\.\d+', parts[-1]):
                version = parts[-1]
                component_name = ' '.join(parts[:-1])
                components[component_name] = version
    
    return components


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
            "vt_id": vt_id,
            "total_components": len(components),
            "validation_rate": f"{(len(approved_in_vt)/len(components)*100):.1f}%" if components else "0%"
        }
        
    except Exception as e:
        return {
            "ticket_id": ticket_id,
            "error": f"Failed to validate components in VT: {str(e)}"
        }


async def validate_components_vs_architecture(
    components: Dict[str, str],
    tool_context: ToolContext,
    use_local_data: bool = False
) -> Dict[str, Any]:
    """Validates components against architecture data with detailed status.

    Enhanced validation that checks components against architecture
    data and provides detailed status information (NOVO, ALTERADO, REMOVIDO).

    Args:
        components: Dictionary of component names to versions.
        tool_context: ADK tool context for state management.
        use_local_data: Whether to use local JSON files instead of API.

    Returns:
        Dictionary containing:
            - found_components: Components found in architecture
            - missing_components: Components not found
            - status_breakdown: Breakdown by status type
            - validation_summary: Summary statistics

    Example:
        >>> components = {
        ...     "caapi-hubd-base-avaliacao-v1": "1.3.2",
        ...     "flutmicro-hubd-base-app-rating": "2.0.1"
        ... }
        >>> result = await validate_components_vs_architecture(components, tool_context)
        >>> print(result["validation_summary"])
        {
            "total": 2,
            "found": 2,
            "missing": 0,
            "success_rate": "100.0%"
        }
    """
    try:
        # Load architecture data
        if use_local_data:
            arch_data = await load_local_architecture_data()
        else:
            # Use API to get architecture data
            client = await get_vt_client()
            response = await client.get("/architecture/current")
            arch_data = response.json().get("data", [])
        
        if not arch_data:
            return {"error": "No architecture data available"}
        
        # Validation process
        found_components = {}
        missing_components = []
        status_breakdown = {
            "NOVO": [],
            "ALTERADO": [],
            "REMOVIDO": [],
            "MANTIDO": [],
            "INDEFINIDO": []
        }
        
        for comp_name, expected_version in components.items():
            found = False
            
            for arch_file in arch_data:
                elements = arch_file.get("elements", [])
                
                for element in elements:
                    element_name = element.get("name", "")
                    element_type = element.get("type", "")
                    
                    if comp_name.lower() in element_name.lower() and \
                       element_type.endswith("ApplicationComponent"):
                        found = True
                        stereotype = element.get("stereotype", "INDEFINIDO")
                        
                        found_components[comp_name] = {
                            "version": expected_version,
                            "status": stereotype,
                            "element_name": element_name,
                            "source": arch_file.get("_source_file", "API")
                        }
                        
                        status_breakdown[stereotype].append(comp_name)
                        break
                
                if found:
                    break
            
            if not found:
                missing_components.append(comp_name)
        
        # Calculate summary
        total = len(components)
        found = len(found_components)
        missing = len(missing_components)
        
        return {
            "found_components": found_components,
            "missing_components": missing_components,
            "status_breakdown": status_breakdown,
            "validation_summary": {
                "total": total,
                "found": found,
                "missing": missing,
                "success_rate": f"{(found/total*100):.1f}%" if total > 0 else "0%"
            }
        }
        
    except Exception as e:
        return {
            "error": f"Failed to validate components against architecture: {str(e)}"
        }


async def search_component_by_name(
    component_name: str,
    tool_context: ToolContext,
    use_local_data: bool = False
) -> Dict[str, Any]:
    """Searches for a specific component in architecture data.

    Performs case-insensitive search for components by name
    and returns detailed information about matches.

    Args:
        component_name: Name or partial name of component to search.
        tool_context: ADK tool context for state management.
        use_local_data: Whether to use local JSON files instead of API.

    Returns:
        Dictionary containing:
            - matches: List of matching components with details
            - total_matches: Number of matches found

    Example:
        >>> result = await search_component_by_name("user", tool_context)
        >>> print(result["total_matches"])
        3
        >>> print(result["matches"][0])
        {
            "name": "user-service",
            "type": "ApplicationComponent",
            "stereotype": "NOVO",
            "source": "architecture_2024.json"
        }
    """
    try:
        # Load architecture data
        if use_local_data:
            arch_data = await load_local_architecture_data()
        else:
            client = await get_vt_client()
            response = await client.get("/architecture/search", 
                                      params={"query": component_name})
            arch_data = response.json().get("data", [])
        
        matches = []
        search_term = component_name.lower()
        
        for arch_file in arch_data:
            elements = arch_file.get("elements", [])
            
            for element in elements:
                element_name = element.get("name", "")
                element_type = element.get("type", "")
                
                if search_term in element_name.lower() and \
                   element_type.endswith("ApplicationComponent"):
                    matches.append({
                        "name": element_name,
                        "type": element_type.split(":")[-1],
                        "stereotype": element.get("stereotype", ""),
                        "source": arch_file.get("_source_file", "API"),
                        "properties": element.get("properties", {})
                    })
        
        # Sort by relevance (exact matches first)
        matches.sort(key=lambda x: (
            not x["name"].lower() == search_term,
            not x["name"].lower().startswith(search_term),
            x["name"].lower()
        ))
        
        return {
            "query": component_name,
            "matches": matches,
            "total_matches": len(matches)
        }
        
    except Exception as e:
        return {
            "query": component_name,
            "error": f"Failed to search component: {str(e)}"
        }


async def list_all_components_by_status(
    tool_context: ToolContext,
    status_filter: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """Lists all components grouped by their status.

    Provides a comprehensive view of all components in the architecture
    grouped by their stereotype status (NOVO, ALTERADO, REMOVIDO, etc).

    Args:
        tool_context: ADK tool context for state management.
        status_filter: Optional filter for specific status.
        limit: Maximum components per status group.

    Returns:
        Dictionary containing:
            - components_by_status: Components grouped by status
            - statistics: Summary statistics per status
            - total_components: Total count across all statuses

    Example:
        >>> result = await list_all_components_by_status(tool_context, status_filter="NOVO")
        >>> print(result["statistics"])
        {
            "NOVO": {"count": 15, "percentage": "45.5%"},
            "ALTERADO": {"count": 10, "percentage": "30.3%"},
            "REMOVIDO": {"count": 8, "percentage": "24.2%"}
        }
    """
    try:
        # Get architecture data
        client = await get_vt_client()
        response = await client.get("/architecture/components/all")
        components_data = response.json().get("components", [])
        
        # Group by status
        components_by_status = {
            "NOVO": [],
            "ALTERADO": [],
            "REMOVIDO": [],
            "MANTIDO": [],
            "INDEFINIDO": []
        }
        
        for component in components_data:
            stereotype = component.get("stereotype", "INDEFINIDO")
            if stereotype not in components_by_status:
                stereotype = "INDEFINIDO"
            
            if not status_filter or status_filter == stereotype:
                components_by_status[stereotype].append({
                    "name": component.get("name"),
                    "version": component.get("version", ""),
                    "type": component.get("type", "ApplicationComponent")
                })
        
        # Apply limit
        for status in components_by_status:
            if len(components_by_status[status]) > limit:
                components_by_status[status] = components_by_status[status][:limit]
        
        # Calculate statistics
        total_components = sum(len(comps) for comps in components_by_status.values())
        statistics = {}
        
        for status, comps in components_by_status.items():
            count = len(comps)
            percentage = (count / total_components * 100) if total_components > 0 else 0
            statistics[status] = {
                "count": count,
                "percentage": f"{percentage:.1f}%"
            }
        
        return {
            "components_by_status": components_by_status,
            "statistics": statistics,
            "total_components": total_components,
            "limit_applied": limit
        }
        
    except Exception as e:
        return {
            "error": f"Failed to list components by status: {str(e)}"
        }


async def get_blizzdesign_export(jt_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Fetches the technical architecture export from BlizzDesign.
    
    BlizzDesign is an enterprise architecture modeling tool that uses
    ArchiMate notation. It exports architecture diagrams as JSON containing
    elements (components, services, artifacts) and their relationships.

    Args:
        jt_id: The JT (Jornada Técnica) identifier.
        tool_context: ADK tool context for state management.

    Returns:
        Complete BlizzDesign export data in JSON format containing:
            - viewInfo: View information with name and JT
            - elements: Array of ArchiMate elements
            - relationships: Array of element relationships
            - metadata: Export metadata with counts
        
        Or error dictionary if retrieval failed:
            - jt_id: The requested JT identifier
            - error: Error message describing the failure

    Example:
        >>> result = await get_blizzdesign_export("JT-147338", tool_context)
        >>> print(result["viewInfo"]["name"])
        "Visão Técnica - NPS/CES/CSAT"
        >>> print(result["metadata"]["elementCount"])
        33
    """
    try:
        client = await get_vt_client()
        response = await client.get(f"/blizzdesign/export/{jt_id}")
        
        if response.status_code != 200:
            return {
                "jt_id": jt_id,
                "error": f"BlizzDesign API returned status {response.status_code}"
            }
        
        blizzdesign_data = response.json()
        
        # Store in context for reuse
        tool_context.state[f"blizzdesign_export_{jt_id}"] = blizzdesign_data
        
        return blizzdesign_data
        
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
            - element_count: Total elements in the diagram
            - relationship_count: Total relationships in the diagram

    Example:
        >>> data = await get_blizzdesign_export("JT-147338", tool_context)
        >>> result = await parse_blizzdesign_data(data, tool_context)
        >>> print(result["new_components"])
        ["caapi-hubd-base-avaliacao-v1", "sboot-hubd-base-atom-avaliacao"]
    """
    try:
        view_info = blizzdesign_json.get("viewInfo", {})
        view_name = view_info.get("name", "Unknown")
        jt_id = view_info.get("JT", "")
        
        # Extract components using utility function
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
        
        # Get metadata
        metadata = blizzdesign_json.get("metadata", {})
        element_count = metadata.get("elementCount", 0)
        relationship_count = metadata.get("relationshipCount", 0)
        
        # Store parsed data in context
        tool_context.state[f"blizzdesign_{jt_id}"] = {
            "components": components,
            "new_components": new_components,
            "modified_components": modified_components,
            "removed_components": removed_components,
            "maintained_components": maintained_components
        }
        
        return {
            "view_name": view_name,
            "jt_id": jt_id,
            "components": components,
            "new_components": new_components,
            "modified_components": modified_components,
            "removed_components": removed_components,
            "maintained_components": maintained_components,
            "total_components": len(components),
            "element_count": element_count,
            "relationship_count": relationship_count
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

    Fetches the API contract specification associated with
    a component in the Technical Vision.

    Args:
        vt_id: Technical Vision identifier.
        component_name: Name of the component.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - component_name: Component name
            - has_contract: Whether contract exists
            - contract_version: OpenAPI version
            - endpoints: List of available endpoints
            - contract_url: URL to full contract
            - error: Error message if retrieval failed

    Example:
        >>> result = await get_openapi_contract("VT-2024-001", "user-service", tool_context)
        >>> print(result)
        {
            "component_name": "user-service",
            "has_contract": True,
            "contract_version": "3.0.0",
            "endpoints": ["/users", "/users/{id}", "/auth"],
            "contract_url": "https://api.example.com/contracts/user-service/openapi.yaml"
        }
    """
    try:
        client = await get_vt_client()
        
        # Get contract from VT
        params = {
            "vt_id": vt_id,
            "component": component_name
        }
        response = await client.get("/contracts/openapi", params=params)
        contract_data = response.json()
        
        if not contract_data:
            return {
                "component_name": component_name,
                "has_contract": False,
                "error": "No OpenAPI contract found for this component"
            }
        
        # Extract endpoint information
        endpoints = []
        if "paths" in contract_data:
            endpoints = list(contract_data["paths"].keys())
        
        # Store in context
        tool_context.state[f"contract_{component_name}"] = {
            "has_contract": True,
            "version": contract_data.get("openapi", ""),
            "endpoints": endpoints
        }
        
        return {
            "component_name": component_name,
            "has_contract": True,
            "contract_version": contract_data.get("openapi", "3.0.0"),
            "endpoints": endpoints[:10],  # Return first 10 endpoints
            "total_endpoints": len(endpoints),
            "contract_url": f"{get_settings().vt.base_url}/contracts/{component_name}/openapi.yaml"
        }
        
    except Exception as e:
        return {
            "component_name": component_name,
            "error": f"Failed to fetch OpenAPI contract: {str(e)}"
        }