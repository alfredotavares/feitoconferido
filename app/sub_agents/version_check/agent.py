"""Version Check Subagent for component version validation.

This subagent compares deployment versions with production versions
using Component (Portal Tech) to identify major changes or new components.
"""

import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from typing import Dict, List, Any

from . import prompt

USE_MOCK_TOOLS = os.getenv("USE_MOCK_TOOLS", "true").lower() == "true"

if USE_MOCK_TOOLS:
    from ...tools.mock.tools_mocked import check_multiple_component_versions
else:
    from ...tools.integrations.portal_tech import (
        check_multiple_component_versions
    )


async def check_component_versions(
    components: List[Dict[str, str]],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Execute version checking for components.
    
    Compares proposed deployment versions against current production
    versions to identify major changes, new components, or version conflicts.
    
    Args:
        components: List of components with names and versions.
        tool_context: ADK tool context for state management.
        
    Returns:
        Dictionary containing version analysis results.
    """
    try:
    
        version_check = await check_multiple_component_versions(
            components, 
            tool_context
        )
        
        if "error" in version_check:
            return {
                "status": "WARNING",
                "warning": f"Version check encountered issues: {version_check['error']}",
                "components_checked": [],
                "requires_manual": True
            }
        
    
        major_changes = version_check.get("major_changes", [])
        new_components = version_check.get("new_components", [])
        error_components = version_check.get("components_with_errors", [])
        version_changes = version_check.get("version_changes", [])
        
    
        status = "SUCCESS"
        warnings = []
        manual_actions = []
        
        if major_changes:
            warnings.append(f"Major version changes detected: {', '.join(major_changes)}")
            status = "WARNING"
        
        if new_components:
            warnings.append(f"New components detected: {', '.join(new_components)}")
        
        if error_components:
            manual_actions.append(f"Manual version verification required for: {', '.join(error_components)}")
            status = "WARNING"
        
        return {
            "status": status,
            "components_checked": len(components),
            "version_changes": version_changes,
            "major_changes": major_changes,
            "new_components": new_components,
            "components_with_errors": error_components,
            "warnings": warnings,
            "manual_actions": manual_actions,
            "requires_manual": len(manual_actions) > 0
        }
        
    except Exception as e:
        return {
            "status": "FAILED",
            "error": f"Unexpected error during version check: {str(e)}",
            "components_checked": 0,
            "requires_manual": True
        }


version_check_agent = Agent(
    name="version_check_subagent",
    model="gemini-2.5-flash",
    description="Subagente especializado para validação e comparação de versões de componentes.",
    instruction=prompt.VERSION_CHECK_PROMPT,
    tools=[check_component_versions]
)
