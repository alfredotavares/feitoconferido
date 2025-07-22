"""Data formatters for Feito/Conferido process.

Provides formatting utilities for various data structures used
throughout the validation process.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


def format_validation_scope(development_cycle: str, 
                          architecture: str, 
                          components: List[str]) -> str:
    """Formats the validation scope according to ARQCOR template.

    Args:
        development_cycle: Development cycle(s) from JT.
        architecture: Architecture type from VT.
        components: List of component names.

    Returns:
        Formatted validation scope string.

    Example:
        >>> scope = format_validation_scope(
        ...     "Sprint 23; Sprint 24",
        ...     "Microservices",
        ...     ["user-service", "auth-module"]
        ... )
        >>> print(scope)
        Ciclo de desenvolvimento: Sprint 23; Sprint 24
        Arquitetura: Microservices
        Componentes:
        - user-service
        - auth-module
    """
    # Handle multiple cycles with semicolon
    cycles = development_cycle.strip()
    
    # Format components list
    components_list = "\n".join(f"- {comp}" for comp in components)
    
    # Build the scope according to template
    scope = f"""Ciclo de desenvolvimento: {cycles}
Arquitetura: {architecture}
Componentes:
{components_list}"""
    
    return scope


def format_version_changes(changes: List[Dict[str, str]]) -> str:
    """Formats version changes for ARQCOR form.

    Args:
        changes: List of version change dictionaries containing:
            - component: Component name
            - from_version: Current production version (or "NEW")
            - to_version: Version to be deployed

    Returns:
        Formatted string to append to validation scope.

    Example:
        >>> changes = [
        ...     {"component": "user-service", "from_version": "1.2.3", "to_version": "2.0.0"},
        ...     {"component": "auth-module", "from_version": "NEW", "to_version": "1.0.0"}
        ... ]
        >>> print(format_version_changes(changes))
        
        Mudanças de Versão (DE-PARA):
        user-service: 1.2.3 → 2.0.0
        auth-module: NEW → 1.0.0
    """
    if not changes:
        return ""
    
    formatted = "\n\nMudanças de Versão (DE-PARA):"
    for change in changes:
        component = change.get("component", "unknown")
        from_version = change.get("from_version", "unknown")
        to_version = change.get("to_version", "unknown")
        formatted += f"\n{component}: {from_version} → {to_version}"
    
    return formatted


def parse_jira_components(components_field: Any) -> List[str]:
    """Parses components from Jira custom field.

    Args:
        components_field: Raw components field from Jira (can be list or string).

    Returns:
        List of component names.

    Example:
        >>> parse_jira_components(["comp1", "comp2"])
        ['comp1', 'comp2']
        >>> parse_jira_components("comp1, comp2, comp3")
        ['comp1', 'comp2', 'comp3']
    """
    components = []
    
    if isinstance(components_field, list):
        components = [str(comp).strip() for comp in components_field if comp]
    elif isinstance(components_field, str):
        # Handle comma-separated string format
        components = [comp.strip() for comp in components_field.split(",") if comp.strip()]
    
    return components


def parse_development_cycle(cycle_field: Any) -> str:
    """Parses and formats development cycle from Jira.

    Args:
        cycle_field: Raw development cycle field from Jira.

    Returns:
        Formatted development cycle string.

    Example:
        >>> parse_development_cycle("Sprint 23")
        'Sprint 23'
        >>> parse_development_cycle(["Sprint 23", "Sprint 24"])
        'Sprint 23; Sprint 24'
    """
    if not cycle_field:
        return ""
    
    if isinstance(cycle_field, list):
        # Join multiple cycles with semicolon
        return "; ".join(str(cycle).strip() for cycle in cycle_field if cycle)
    
    return str(cycle_field).strip()


def extract_version_from_string(version_string: str) -> Optional[str]:
    """Extracts semantic version from a string.

    Args:
        version_string: String potentially containing a version.

    Returns:
        Extracted version in format X.Y.Z or None if not found.

    Example:
        >>> extract_version_from_string("user-service v2.1.0")
        '2.1.0'
        >>> extract_version_from_string("Version: 1.2.3-beta")
        '1.2.3'
    """
    import re
    
    # Match semantic version pattern
    pattern = r'\d+\.\d+\.\d+'
    match = re.search(pattern, version_string)
    
    return match.group() if match else None


def compare_versions(version1: str, version2: str) -> int:
    """Compares two semantic versions.

    Args:
        version1: First version string.
        version2: Second version string.

    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2

    Example:
        >>> compare_versions("1.2.3", "1.2.4")
        -1
        >>> compare_versions("2.0.0", "1.9.9")
        1
    """
    def parse_version(v: str) -> tuple:
        parts = v.split('.')
        return tuple(int(part) for part in parts[:3])  # major, minor, patch
    
    try:
        v1 = parse_version(version1)
        v2 = parse_version(version2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    except (ValueError, AttributeError):
        # If parsing fails, do string comparison
        return -1 if version1 < version2 else (1 if version1 > version2 else 0)


def format_validation_result(status: str, 
                           errors: List[str], 
                           warnings: List[str],
                           manual_actions: List[str]) -> str:
    """Formats a validation result for display.

    Args:
        status: Overall status (APPROVED, FAILED, REQUIRES_MANUAL_ACTION).
        errors: List of error messages.
        warnings: List of warning messages.
        manual_actions: List of required manual actions.

    Returns:
        Formatted result string.
    """
    status_emoji = {
        "APPROVED": "✅",
        "FAILED": "❌",
        "REQUIRES_MANUAL_ACTION": "⚠️"
    }.get(status, "❓")
    
    result = f"{status_emoji} Status: {status}\n"
    
    if errors:
        result += "\n❌ Errors:\n"
        for error in errors:
            result += f"  • {error}\n"
    
    if warnings:
        result += "\n⚠️ Warnings:\n"
        for warning in warnings:
            result += f"  • {warning}\n"
    
    if manual_actions:
        result += "\n📋 Manual Actions Required:\n"
        for action in manual_actions:
            result += f"  • {action}\n"
    
    return result.strip()


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Formats a datetime for display.

    Args:
        dt: Datetime to format. Uses current time if None.

    Returns:
        Formatted timestamp string.

    Example:
        >>> format_timestamp(datetime(2024, 1, 15, 10, 30, 0))
        '2024-01-15 10:30:00'
    """
    if dt is None:
        dt = datetime.utcnow()
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def extract_blizzdesign_components(blizzdesign_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extracts component information from BlizzDesign export.

    Args:
        blizzdesign_data: Raw BlizzDesign export data.

    Returns:
        List of component dictionaries with name and stereotype.

    Example:
        >>> data = {
        ...     "elements": [
        ...         {"name": "user-service", "stereotype": "NOVO"},
        ...         {"name": "auth-module", "stereotype": "ALTERADO"}
        ...     ]
        ... }
        >>> extract_blizzdesign_components(data)
        [{'name': 'user-service', 'stereotype': 'NOVO'}, {'name': 'auth-module', 'stereotype': 'ALTERADO'}]
    """
    components = []
    
    elements = blizzdesign_data.get("elements", [])
    for element in elements:
        if element.get("type", "").endswith("ApplicationComponent"):
            components.append({
                "name": element.get("name", ""),
                "stereotype": element.get("stereotype", "")
            })
    
    return components