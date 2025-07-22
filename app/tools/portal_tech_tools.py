"""Portal Tech integration tools for Feito/Conferido agent.

Provides tools for interacting with Portal Tech to check
production versions and compare with deployment versions.
"""

from typing import Dict, List, Any, Optional
import re
from bs4 import BeautifulSoup
from google.adk.tools import ToolContext

from ..utils.http_clients import get_portal_tech_client
from ..utils.formatters import extract_version_from_string, compare_versions
from ..config.settings import get_settings


async def get_production_version(component_name: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieves the current production version of a component.

    Queries Portal Tech to find the version currently deployed
    in production environment.

    Args:
        component_name: Name of the component to query.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - component: Component name
            - production_version: Version in production (or None if not found)
            - found: Boolean indicating if component was found
            - source: Where the version was found (API or scraping)
            - error: Error message if retrieval failed

    Example:
        >>> result = await get_production_version("user-service", tool_context)
        >>> print(result)
        {
            "component": "user-service",
            "production_version": "2.0.5",
            "found": True,
            "source": "api"
        }
    """
    settings = get_settings().portal_tech
    
    try:
        client = await get_portal_tech_client()
        
        # First try API if auth token is available
        if settings.auth_token:
            try:
                response = await client.get(f"/api/v1/components/{component_name}/version")
                
                if response.status_code == 200:
                    data = response.json()
                    version = data.get("version") or data.get("current_version")
                    
                    if version:
                        # Cache in state
                        tool_context.state[f"portal_tech_version_{component_name}"] = version
                        
                        return {
                            "component": component_name,
                            "production_version": version,
                            "found": True,
                            "source": "api"
                        }
            except:
                # Fall through to scraping
                pass
        
        # Fallback to web scraping
        search_url = settings.search_endpoint
        params = {"q": component_name, "type": "component"}
        
        response = await client.get(search_url, params=params)
        html_content = response.text
        
        # Parse HTML
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Try multiple selectors
        selectors = [
            f"div[data-component='{component_name}'] .version",
            f"tr:contains('{component_name}') td.version",
            f".component-card:contains('{component_name}') .component-version",
            ".search-result .version-info"
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    # Check if this is the right component
                    parent = element.find_parent(["div", "tr"])
                    if parent and component_name.lower() in parent.text.lower():
                        version_text = element.text.strip()
                        
                        # Extract version pattern
                        version = extract_version_from_string(version_text)
                        if version:
                            # Cache in state
                            tool_context.state[f"portal_tech_version_{component_name}"] = version
                            
                            return {
                                "component": component_name,
                                "production_version": version,
                                "found": True,
                                "source": "scraping"
                            }
            except:
                continue
        
        # Component not found in production
        return {
            "component": component_name,
            "production_version": None,
            "found": False,
            "source": "not_found"
        }
        
    except Exception as e:
        return {
            "component": component_name,
            "error": f"Failed to get production version: {str(e)}"
        }


async def compare_component_versions(
    component_name: str,
    deployment_version: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Compares deployment version with production version.

    Retrieves the production version and compares it with the
    version to be deployed, identifying the type of change.

    Args:
        component_name: Name of the component.
        deployment_version: Version to be deployed.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - component: Component name
            - deployment_version: Version to be deployed
            - production_version: Current production version
            - version_change: Description of change (e.g., "1.2.3 → 2.0.0")
            - change_type: Type of change (NEW, MAJOR, MINOR, PATCH, NONE)
            - is_major_change: Boolean for major version changes
            - error: Error message if comparison failed

    Example:
        >>> result = await compare_component_versions("user-service", "2.1.0", tool_context)
        >>> print(result)
        {
            "component": "user-service",
            "deployment_version": "2.1.0",
            "production_version": "2.0.5",
            "version_change": "2.0.5 → 2.1.0",
            "change_type": "MINOR",
            "is_major_change": False
        }
    """
    try:
        # Get production version
        prod_info = await get_production_version(component_name, tool_context)
        
        if "error" in prod_info:
            return prod_info
        
        production_version = prod_info.get("production_version")
        
        # Determine change type
        if not production_version:
            change_type = "NEW"
            version_change = f"NEW → {deployment_version}"
            is_major_change = True
        else:
            # Compare versions
            comparison = compare_versions(production_version, deployment_version)
            
            if comparison == 0:
                change_type = "NONE"
                version_change = "No change"
                is_major_change = False
            else:
                version_change = f"{production_version} → {deployment_version}"
                
                # Parse versions to determine change type
                prod_parts = production_version.split('.')
                deploy_parts = deployment_version.split('.')
                
                if len(prod_parts) >= 3 and len(deploy_parts) >= 3:
                    if prod_parts[0] != deploy_parts[0]:
                        change_type = "MAJOR"
                        is_major_change = True
                    elif prod_parts[1] != deploy_parts[1]:
                        change_type = "MINOR"
                        is_major_change = False
                    else:
                        change_type = "PATCH"
                        is_major_change = False
                else:
                    change_type = "UNKNOWN"
                    is_major_change = False
        
        return {
            "component": component_name,
            "deployment_version": deployment_version,
            "production_version": production_version,
            "version_change": version_change,
            "change_type": change_type,
            "is_major_change": is_major_change
        }
        
    except Exception as e:
        return {
            "component": component_name,
            "error": f"Failed to compare versions: {str(e)}"
        }


async def check_multiple_component_versions(
    components: List[Dict[str, str]],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Checks versions for multiple components at once.

    Batch operation to check production versions and compare
    with deployment versions for a list of components.

    Args:
        components: List of dictionaries with 'name' and 'version' keys.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - total_components: Number of components checked
            - version_changes: List of version change descriptions
            - new_components: List of components not in production
            - major_changes: List of components with major version changes
            - components_with_errors: List of components that failed to check
            - summary: Overall summary of version changes

    Example:
        >>> components = [
        ...     {"name": "user-service", "version": "2.1.0"},
        ...     {"name": "auth-module", "version": "1.5.0"},
        ...     {"name": "new-service", "version": "1.0.0"}
        ... ]
        >>> result = await check_multiple_component_versions(components, tool_context)
        >>> print(result)
        {
            "total_components": 3,
            "version_changes": [
                {"component": "user-service", "change": "2.0.5 → 2.1.0", "type": "MINOR"},
                {"component": "auth-module", "change": "1.4.2 → 1.5.0", "type": "MINOR"},
                {"component": "new-service", "change": "NEW → 1.0.0", "type": "NEW"}
            ],
            "new_components": ["new-service"],
            "major_changes": [],
            "components_with_errors": [],
            "summary": "3 components: 1 new, 2 minor updates"
        }
    """
    version_changes = []
    new_components = []
    major_changes = []
    components_with_errors = []
    
    for component in components:
        name = component.get("name")
        version = component.get("version")
        
        if not name or not version:
            continue
        
        # Check version for this component
        result = await compare_component_versions(name, version, tool_context)
        
        if "error" in result:
            components_with_errors.append(name)
            continue
        
        change_info = {
            "component": name,
            "change": result["version_change"],
            "type": result["change_type"]
        }
        
        version_changes.append(change_info)
        
        if result["change_type"] == "NEW":
            new_components.append(name)
        elif result["is_major_change"]:
            major_changes.append(name)
    
    # Build summary
    total = len(components)
    new_count = len(new_components)
    major_count = len(major_changes)
    error_count = len(components_with_errors)
    
    summary_parts = [f"{total} components"]
    if new_count > 0:
        summary_parts.append(f"{new_count} new")
    if major_count > 0:
        summary_parts.append(f"{major_count} major updates")
    if error_count > 0:
        summary_parts.append(f"{error_count} errors")
    
    summary = ": ".join([summary_parts[0], ", ".join(summary_parts[1:])])
    
    # Store results in state for ARQCOR form update
    tool_context.state["version_check_results"] = {
        "version_changes": version_changes,
        "new_components": new_components,
        "major_changes": major_changes
    }
    
    return {
        "total_components": total,
        "version_changes": version_changes,
        "new_components": new_components,
        "major_changes": major_changes,
        "components_with_errors": components_with_errors,
        "summary": summary
    }


async def get_component_details(component_name: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieves detailed information about a component from Portal Tech.

    Fetches comprehensive component information including team ownership,
    repository, and deployment history.

    Args:
        component_name: Name of the component.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - component: Component name
            - version: Current production version
            - team: Team responsible for the component
            - repository: Source code repository URL
            - last_deployment: Date of last deployment
            - health_status: Current health status
            - portal_url: Direct link to Portal Tech page
            - error: Error message if retrieval failed

    Example:
        >>> result = await get_component_details("user-service", tool_context)
        >>> print(result)
        {
            "component": "user-service",
            "version": "2.0.5",
            "team": "User Experience Team",
            "repository": "https://github.com/company/user-service",
            "last_deployment": "2024-01-10T15:30:00Z",
            "health_status": "healthy",
            "portal_url": "https://portaltech.bvnet.bv/components/user-service"
        }
    """
    settings = get_settings().portal_tech
    
    try:
        # First get basic version info
        version_info = await get_production_version(component_name, tool_context)
        
        if "error" in version_info:
            return version_info
        
        details = {
            "component": component_name,
            "version": version_info.get("production_version"),
            "portal_url": f"{settings.base_url}/components/{component_name}"
        }
        
        # Try to get additional details via API if available
        if settings.auth_token:
            try:
                client = await get_portal_tech_client()
                response = await client.get(f"/api/v1/components/{component_name}")
                
                if response.status_code == 200:
                    data = response.json()
                    details.update({
                        "team": data.get("team", "Unknown"),
                        "repository": data.get("repository", ""),
                        "last_deployment": data.get("last_deployment", ""),
                        "health_status": data.get("health_status", "unknown")
                    })
            except:
                # Additional details not available
                pass
        
        return details
        
    except Exception as e:
        return {
            "component": component_name,
            "error": f"Failed to get component details: {str(e)}"
        }