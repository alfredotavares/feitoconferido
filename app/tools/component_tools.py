"""Component (Portal Tech) integration tools for Feito/Conferido agent.

Provides tools for interacting with Component (Portal Tech) to check
production versions and compare with deployment versions.
"""

from typing import Dict, List, Any, Optional
from google.adk.tools import ToolContext

from ..utils.http_clients import get_portal_tech_client
from ..utils.formatters import compare_versions
from ..config.settings import get_settings


async def get_production_version(component_name: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieves the current production version of a component.

    Queries Component (Portal Tech) API to find the version currently deployed
    in production environment.

    Args:
        component_name: Name of the component to query.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - component: Component name
            - production_version: Version in production (or None if not found)
            - found: Boolean indicating if component was found
            - source: Where the version was found (always "api")
            - error: Error message if retrieval failed

    Raises:
        Exception: When API call fails or authentication is missing.

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
    
    if not settings.auth_token:
        return {
            "component": component_name,
            "error": "Authentication token not configured in Component (Portal Tech) settings"
        }
    
    try:
        client = await get_portal_tech_client()
        
        headers = {"Authorization": f"Bearer {settings.auth_token}"}
        response = await client.get(
            f"/v2/components?relationship=envVersion&name={component_name}",
            headers=headers
        )
        
        if response.status_code != 200:
            return {
                "component": component_name,
                "error": f"API returned status code {response.status_code}"
            }
        
        data = response.json()
        component_data = data.get("data", {})
        
        if not component_data:
            return {
                "component": component_name,
                "production_version": None,
                "found": False,
                "source": "api"
            }
        
        # Process component data
        processed_data = _process_component_data(component_data)
        production_version = processed_data["environment_versions"]["PRD"]
        
        # Cache result in state
        if production_version:
            tool_context.state[f"portal_tech_version_{component_name}"] = production_version
        
        return {
            "component": component_name,
            "production_version": production_version,
            "found": production_version is not None,
            "source": "api"
        }
        
    except Exception as e:
        return {
            "component": component_name,
            "error": f"Failed to get production version: {str(e)}"
        }


async def get_component_versions(component_name: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieves component versions across different environments.

    Queries Component (Portal Tech) API to find versions currently deployed
    in PRD, UAT, and DES environments for the specified component.

    Args:
        component_name: Name of the component to query.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - component: Component name
            - current_prd_version: Version in PRD environment (or None)
            - current_uat_version: Version in UAT environment (or None)  
            - current_des_version: Version in DES environment (or None)
            - found: Boolean indicating if component was found
            - error: Error message if retrieval failed

    Raises:
        Exception: When API call fails or authentication is missing.

    Example:
        >>> result = await get_component_versions("user-service", tool_context)
        >>> print(result)
        {
            "component": "user-service",
            "current_prd_version": "2.0.5",
            "current_uat_version": "2.0.6",
            "current_des_version": "2.1.0-dev",
            "found": True
        }
    """
    settings = get_settings().portal_tech
    
    if not settings.auth_token:
        return {
            "component": component_name,
            "error": "Authentication token not configured in Component (Portal Tech) settings"
        }
    
    try:
        client = await get_portal_tech_client()
        
        headers = {"Authorization": f"Bearer {settings.auth_token}"}
        response = await client.get(
            f"/v2/components?relationship=envVersion&name={component_name}",
            headers=headers
        )
        
        if response.status_code != 200:
            return {
                "component": component_name,
                "error": f"API returned status code {response.status_code}"
            }
        
        data = response.json()
        component_data = data.get("data", {})
        
        if not component_data:
            return {
                "component": component_name,
                "current_prd_version": None,
                "current_uat_version": None,
                "current_des_version": None,
                "found": False
            }
        
        # Process component data
        processed_data = _process_component_data(component_data)
        versions = processed_data["environment_versions"]
        
        # Cache results in state
        cache_key = f"portal_tech_versions_{component_name}"
        tool_context.state[cache_key] = versions
        
        return {
            "component": component_name,
            "current_prd_version": versions["PRD"],
            "current_uat_version": versions["UAT"],
            "current_des_version": versions["DES"],
            "found": True
        }
        
    except Exception as e:
        return {
            "component": component_name,
            "error": f"Failed to get component versions: {str(e)}"
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
    """Retrieves detailed information about a component from Component (Portal Tech).

    Fetches comprehensive component information including team ownership,
    repository, technology stack, and deployment history.

    Args:
        component_name: Name of the component.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - component: Component name
            - description: Component description
            - production_version: Current production version
            - team: Team responsible for the component
            - repository: Source code repository URL
            - technology: Technology information
            - last_deployment: Most recent deployment date
            - portal_url: Direct link to Component (Portal Tech) page
            - error: Error message if retrieval failed

    Example:
        >>> result = await get_component_details("user-service", tool_context)
        >>> print(result)
        {
            "component": "user-service",
            "description": "User management service",
            "production_version": "2.0.5",
            "team": "User Experience Team",
            "repository": "https://github.com/company/user-service",
            "technology": {"name": "Java", "version": "17"},
            "last_deployment": "2024-01-10T15:30:00Z",
            "portal_url": "https://portaltech.bvnet.bv/components/user-service"
        }
    """
    settings = get_settings().portal_tech
    
    if not settings.auth_token:
        return {
            "component": component_name,
            "error": "Authentication token not configured in Component (Portal Tech) settings"
        }
    
    try:
        client = await get_portal_tech_client()
        
        headers = {"Authorization": f"Bearer {settings.auth_token}"}
        response = await client.get(
            f"/v2/components?relationship=envVersion&name={component_name}",
            headers=headers
        )
        
        if response.status_code != 200:
            return {
                "component": component_name,
                "error": f"API returned status code {response.status_code}"
            }
        
        data = response.json()
        component_data = data.get("data", {})
        
        if not component_data:
            return {
                "component": component_name,
                "error": "Component not found"
            }
        
        # Process component data
        processed_data = _process_component_data(component_data)
        
        # Find production deployment info
        production_version = processed_data["environment_versions"]["prd"]
        last_deployment = None
        
        for env_version in processed_data["env_versions"]:
            if env_version.get("environment", "").upper() == "PRD":
                last_deployment = env_version.get("created")
                break
        
        # Build component details
        details = {
            "component": processed_data["name"] or component_name,
            "description": processed_data["description"],
            "production_version": production_version,
            "team": processed_data["team"],
            "repository": processed_data["repository"],
            "technology": processed_data["technology"],
            "last_deployment": last_deployment,
            "portal_url": f"{settings.base_url}/components/{component_name}"
        }
        
        return details
        
    except Exception as e:
        return {
            "component": component_name,
            "error": f"Failed to get component details: {str(e)}"
        }


def _extract_environment_versions(env_versions: List[Dict[str, Any]]) -> Dict[str, Optional[str]]:
    """Extracts versions for each environment from API response.

    Helper function that processes the envVersions array to extract
    version information for PRD, UAT, and DES environments.

    Args:
        env_versions: List of environment version objects from API response.

    Returns:
        Dictionary mapping environment names to their versions:
            - prd: Production version or None
            - uat: UAT version or None  
            - des: Development version or None

    Example:
        >>> env_data = [
        ...     {"environment": "PRD", "version": "1.0.0"},
        ...     {"environment": "UAT", "version": "1.1.0"}
        ... ]
        >>> result = _extract_environment_versions(env_data)
        >>> print(result)
        {"prd": "1.0.0", "uat": "1.1.0", "des": None}
    """
    versions: Dict[str, Optional[str]] = {"prd": None, "uat": None, "des": None}
    
    for env_version in env_versions:
        environment = env_version.get("environment", "").upper()
        version = env_version.get("version")
        
        if not version:
            continue
            
        if environment == "PRD":
            versions["prd"] = version
        elif environment == "UAT":
            versions["uat"] = version
        elif environment == "DES":
            versions["des"] = version
    
    return versions


def _process_component_data(component_data: Dict[str, Any]) -> Dict[str, Any]:
    """Processes component data from Component (Portal Tech) API response.

    Helper function that extracts and normalizes component information
    from the API response structure.

    Args:
        component_data: Component data object from API response.

    Returns:
        Dictionary containing processed component information:
            - name: Component name
            - description: Component description
            - team: Team responsible for the component
            - repository: Source code repository URL
            - technology: Technology information
            - env_versions: List of environment versions
            - environment_versions: Processed environment versions dict

    Example:
        >>> component_data = {
        ...     "name": "user-service",
        ...     "description": "User management service",
        ...     "team": "Backend Team",
        ...     "envVersions": [{"environment": "PRD", "version": "1.0.0"}]
        ... }
        >>> result = _process_component_data(component_data)
        >>> print(result["environment_versions"])
        {"prd": "1.0.0", "uat": None, "des": None}
    """
    env_versions = component_data.get("envVersions", [])
    environment_versions = _extract_environment_versions(env_versions)
    
    return {
        "name": component_data.get("name", ""),
        "description": component_data.get("description", ""),
        "team": component_data.get("team", "Unknown"),
        "repository": component_data.get("repository", ""),
        "technology": component_data.get("technology", {}),
        "env_versions": env_versions,
        "environment_versions": environment_versions
    }