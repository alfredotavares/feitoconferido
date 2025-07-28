"""Formatting utilities for Feito/Conferido agent.

Provides functions for formatting output, parsing input,
and standardizing data presentation.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re


def format_component_name(component_name: str) -> str:
    """Formats a component name for consistent display.

    Normalizes component names to a standard format.

    Args:
        component_name: Raw component name.

    Returns:
        Formatted component name.

    Example:
        >>> format_component_name("USER_SERVICE")
        'user-service'
        >>> format_component_name("auth.module")
        'auth-module'
    """
    
    formatted = component_name.lower()
    formatted = re.sub(r'[_.\s]+', '-', formatted)
    return formatted


def format_version_comparison(
    component: str, 
    current_version: str, 
    expected_version: str
) -> str:
    """Formats a version comparison result for display.

    Creates a readable comparison between current and expected versions.

    Args:
        component: Component name.
        current_version: Currently deployed version.
        expected_version: Expected/required version.

    Returns:
        Formatted comparison string.

    Example:
        >>> format_version_comparison("user-service", "1.2.3", "1.3.0")
        'user-service: 1.2.3 → 1.3.0 (update required)'
    """
    comparison = compare_versions(current_version, expected_version)
    
    if comparison == 0:
        status = "✓ (versions match)"
    elif comparison < 0:
        status = "⬆ (update required)"
    else:
        status = "⚠ (newer than expected)"
    
    return f"{component}: {current_version} → {expected_version} {status}"


def compare_versions(version1: str, version2: str) -> int:
    """Compares two semantic version strings.

    Performs semantic version comparison following semver rules.

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
        return tuple(int(part) for part in parts[:3])  
    
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


def parse_component_list_from_text(text: str) -> Dict[str, str]:
    """Extracts components and versions from user input text.

    Enhanced parser that supports multiple formats for component specification:
    - "component -> version"
    - "component : version"
    - "component version" (space separated)
    - JSON format
    - Comma-separated lists

    Args:
        text: User input text containing component list.

    Returns:
        Dictionary mapping component names to versions.

    Example:
        >>> text = '''
        ... caapi-hubd-base-avaliacao-v1 -> 1.3.2
        ... flutmicro-hubd-base-app-rating: 2.0.1
        ... ng15-hubd-base-portal 1.1.1
        ... user-service, auth-module: 2.0.0
        ... '''
        >>> result = parse_component_list_from_text(text)
        >>> print(result)
        {
            'caapi-hubd-base-avaliacao-v1': '1.3.2',
            'flutmicro-hubd-base-app-rating': '2.0.1',
            'ng15-hubd-base-portal': '1.1.1',
            'user-service': '',
            'auth-module': '2.0.0'
        }
    """
    components = {}
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('//'):
            continue
        
        
        if line.startswith('{') and line.endswith('}'):
            try:
                import json
                json_data = json.loads(line)
                if isinstance(json_data, dict):
                    components.update(json_data)
                    continue
            except:
                pass
        
        
        if '->' in line:
            parts = line.split('->')
            if len(parts) == 2:
                component_name = parts[0].strip()
                version = parts[1].strip()
                components[component_name] = version
        
        
        elif ':' in line and not line.startswith('{'):
            parts = line.split(':', 1)
            if len(parts) == 2:
                component_name = parts[0].strip()
                version = parts[1].strip()
                
                
                if ',' in component_name:
                    comp_names = [c.strip() for c in component_name.split(',')]
                    for comp in comp_names:
                        if comp:
                            components[comp] = version
                else:
                    components[component_name] = version
        
        
        else:
            parts = line.split()
            if len(parts) >= 2 and re.match(r'^\d+\.\d+', parts[-1]):
                version = parts[-1]
                component_name = ' '.join(parts[:-1])
                components[component_name] = version
            
            elif len(parts) == 1:
                components[parts[0]] = ""
            
            elif ',' in line:
                comp_names = [c.strip() for c in line.split(',')]
                for comp in comp_names:
                    if comp:
                        components[comp] = ""
    
    return components


def extract_blizzdesign_components(blizzdesign_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extracts component information from BlizzDesign export.

    Enhanced extraction that handles various BlizzDesign export formats
    and provides additional metadata.

    Args:
        blizzdesign_data: Raw BlizzDesign export data.

    Returns:
        List of component dictionaries with name, stereotype, and metadata.

    Example:
        >>> data = {
        ...     "elements": [
        ...         {
        ...             "name": "user-service",
        ...             "type": "ArchiMate:ApplicationComponent",
        ...             "stereotype": "NOVO",
        ...             "properties": {"version": "1.0.0"}
        ...         }
        ...     ]
        ... }
        >>> extract_blizzdesign_components(data)
        [{'name': 'user-service', 'stereotype': 'NOVO', 'version': '1.0.0'}]
    """
    components = []
    
    elements = blizzdesign_data.get("elements", [])
    for element in elements:
        element_type = element.get("type", "")
        
        
        if any(comp_type in element_type for comp_type in 
               ["ApplicationComponent", "Component", "Service"]):
            
            component_info = {
                "name": element.get("name", ""),
                "stereotype": element.get("stereotype", "INDEFINIDO"),
                "type": element_type.split(":")[-1] if ":" in element_type else element_type
            }
            
            
            properties = element.get("properties", {})
            if "version" in properties:
                component_info["version"] = properties["version"]
            
            
            if "description" in element:
                component_info["description"] = element["description"]
            
            if "id" in element:
                component_info["id"] = element["id"]
            
            components.append(component_info)
    
    return components


def format_component_status_summary(components_by_status: Dict[str, List[str]]) -> str:
    """Formats a summary of components grouped by status.

    Creates a readable summary of component statuses with counts
    and visual indicators.

    Args:
        components_by_status: Dictionary mapping status to component lists.

    Returns:
        Formatted summary string.

    Example:
        >>> status_data = {
        ...     "NOVO": ["service-a", "service-b"],
        ...     "ALTERADO": ["service-c"],
        ...     "REMOVIDO": []
        ... }
        >>> print(format_component_status_summary(status_data))
        📊 Component Status Summary:
        
        🆕 NOVO (2):
          • service-a
          • service-b
        
        🔄 ALTERADO (1):
          • service-c
        
        ❌ REMOVIDO (0):
          None
    """
    status_icons = {
        "NOVO": "🆕",
        "ALTERADO": "🔄",
        "REMOVIDO": "❌",
        "MANTIDO": "✅",
        "INDEFINIDO": "❓"
    }
    
    result = ["📊 Component Status Summary:"]
    result.append("")
    
    for status, components in components_by_status.items():
        icon = status_icons.get(status, "•")
        count = len(components)
        
        result.append(f"{icon} {status} ({count}):")
        
        if components:
            
            for comp in components[:5]:
                result.append(f"  • {comp}")
            if len(components) > 5:
                result.append(f"  ... and {len(components) - 5} more")
        else:
            result.append("  None")
        
        result.append("")
    
    return "\n".join(result).strip()


def format_architecture_validation_report(
    validation_result: Dict[str, Any],
    include_details: bool = True
) -> str:
    """Formats a comprehensive architecture validation report.

    Creates a detailed report of architecture validation results
    with statistics and actionable information.

    Args:
        validation_result: Validation result from validate_components_vs_architecture.
        include_details: Whether to include detailed component lists.

    Returns:
        Formatted report string.

    Example:
        >>> result = {
        ...     "validation_summary": {"total": 10, "found": 8, "missing": 2, "success_rate": "80.0%"},
        ...     "status_breakdown": {"NOVO": ["service-a"], "ALTERADO": ["service-b"]},
        ...     "missing_components": ["service-x", "service-y"]
        ... }
        >>> print(format_architecture_validation_report(result))
        
    """
    lines = ["📋 Architecture Validation Report", "=" * 40]
    
    
    if "validation_summary" in validation_result:
        summary = validation_result["validation_summary"]
        lines.extend([
            "",
            "📊 Summary:",
            f"  Total Components: {summary.get('total', 0)}",
            f"  Found: {summary.get('found', 0)}",
            f"  Missing: {summary.get('missing', 0)}",
            f"  Success Rate: {summary.get('success_rate', '0%')}",
            ""
        ])
    
    
    if "status_breakdown" in validation_result and include_details:
        lines.append(format_component_status_summary(
            validation_result["status_breakdown"]
        ))
        lines.append("")
    
    
    if "missing_components" in validation_result:
        missing = validation_result["missing_components"]
        if missing:
            lines.extend([
                "❌ Missing Components:",
                *[f"  • {comp}" for comp in missing],
                ""
            ])
    
    
    if "found_components" in validation_result and include_details:
        found = validation_result["found_components"]
        if found:
            lines.append("✅ Found Components:")
            for comp_name, details in list(found.items())[:10]:
                lines.append(f"  • {comp_name}")
                lines.append(f"    Status: {details.get('status', 'Unknown')}")
                lines.append(f"    Version: {details.get('version', 'N/A')}")
            if len(found) > 10:
                lines.append(f"  ... and {len(found) - 10} more")
            lines.append("")
    
    
    lines.extend([
        "",
        f"Generated: {format_timestamp()}",
        "=" * 40
    ])
    
    return "\n".join(lines)


def parse_jira_components(components_data: List[Dict[str, Any]]) -> List[str]:
    """Extracts component names from Jira's component field data.

    Jira's API often returns components as a list of objects.
    This function extracts just the 'name' from each object.

    Args:
        components_data: The raw component data from Jira API,
                         typically a list of dictionaries.

    Returns:
        A list of component name strings.

    Example:
        >>> data = [{'id': '1', 'name': 'user-service'}, {'id': '2', 'name': 'auth-module'}]
        >>> parse_jira_components(data)
        ['user-service', 'auth-module']
        >>> parse_jira_components(None)
        []
    """
    if not isinstance(components_data, list):
        return []
    
    return [
        name for comp in components_data
        if isinstance(comp, dict) and (name := comp.get("name")) is not None
    ]


def parse_development_cycle(cycle_data: Any) -> str:
    """Parses the development cycle from a Jira custom field.

    Handles different data structures that a custom field might have
    (e.g., a string or a dictionary with a 'value' key).

    Args:
        cycle_data: The raw data from Jira's custom field.

    Returns:
        The development cycle as a string, or an empty string if not found.

    Example:
        >>> parse_development_cycle({'value': 'Sprint 23'})
        'Sprint 23'
        >>> parse_development_cycle('Sprint 24')
        'Sprint 24'
        >>> parse_development_cycle(None)
        ''
    """
    if isinstance(cycle_data, dict):
        
        return cycle_data.get("value", "")
    
    if isinstance(cycle_data, str):
        return cycle_data
        
    return ""

def format_validation_scope(
    development_cycle: str, 
    architecture: str, 
    components: List[str]
) -> str:
    lines = [
        "h2. Escopo da Validação de Aderência",
        f"*Ciclo de Desenvolvimento:* {development_cycle or 'Não informado'}",
        f"*Arquitetura de Referência:* {architecture or 'Não informada'}",
        "",
        "h3. Componentes no Escopo:"
    ]
    
    if components:
        for component in components:
            lines.append(f"* {component}")
    else:
        lines.append("_Nenhum componente informado._")
        
    return "\n".join(lines)


def format_version_changes(version_changes: List[Dict[str, str]]) -> str:
    if not version_changes:
        return "h3. Alterações de Versão\n_Nenhuma alteração de versão detectada._"

    lines = [
        "h2. Alterações de Versão dos Componentes",
        "||Componente||Versão Anterior||Nova Versão||"
    ]
    
    for change in version_changes:
        component = change.get("component", "N/A")
        from_version = change.get("from_version", "N/A")
        to_version = change.get("to_version", "N/A")
        lines.append(f"|{component}|{from_version}|{to_version}|")
        
    return "\n".join(lines)