"""Complete mocked tools for Feito/Conferido validation process testing.

Provides mocked implementations of all validation tools to enable
testing without dependencies on external services.
"""

from typing import Dict, List, Any, Optional
from google.adk.tools import ToolContext
from datetime import datetime, timezone
from pathlib import Path
import random
import re


BLIZZDESIGN_MOCK_EXPORTS = {
    "JT-147338": {
        "viewInfo": {
            "name": "Visão Técnica - NPS/CES/CSAT",
            "JT": "JT-147338"
        },
        "elements": [
            {
                "id": "bb502786-647f-ef11-84d2-16ffc1277435",
                "name": "caapi-hubd-base-avaliacao-v1",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "NOVO"
            },
            {
                "id": "4680d0d7-647f-ef11-84d2-16ffc1277435",
                "name": "GET /v1/evaluation/{evaluationType}",
                "type": "ArchiMate:ApplicationService",
                "stereotype": "NOVO"
            },
            {
                "id": "5e9ea4d8-2480-ef11-84d2-16ffe58a20bb",
                "name": "POST /v1/evaluation/{evaluationType}",
                "type": "ArchiMate:ApplicationService",
                "stereotype": "NOVO"
            },
            {
                "id": "fc413269-0081-ef11-84d2-16ffc926a3dd",
                "name": "caapi-hubd-base-avaliacao-gravar-v3",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "REMOVIDO"
            },
            {
                "id": "11a00ad4-3862-ee11-844a-16243b297e85",
                "name": "flutmicro-hubd-base-app-rating",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "ALTERADO"
            },
            {
                "id": "748ef25d-737f-ef11-84d2-16ffc1277435",
                "name": "ng15-hubd-base-portal-configuracao",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "ALTERADO"
            },
            {
                "id": "61dfb81a-2bcc-ee11-8469-16b943249bff",
                "name": "HUBDAvaliacaoAplicativo_APPL",
                "type": "ArchiMate:TechnologyArtifact",
                "stereotype": "ALTERADO"
            },
            {
                "id": "c7a4e14a-757f-ef11-84d2-16ffc1277435",
                "name": "springboot-hubd-base-bff-portal-configuracao",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "ALTERADO"
            },
            {
                "id": "9f9fc917-1c80-ef11-84d2-16ffe58a20bb",
                "name": "sboot-hubd-base-atom-avaliacao",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "NOVO"
            },
            {
                "id": "05aeb61f-0f7d-ef11-84d2-16ffe90bcc57",
                "name": "Avaliação e Análise pelo Cliente em Canais",
                "type": "ArchiMate:ApplicationCollaboration",
                "stereotype": "NOVO"
            },
            {
                "id": "ed9f0ad4-3862-ee11-844a-16243b297e85",
                "name": "sboot-hubd-base-atom-avaliacao-store",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "REMOVIDO"
            },
            {
                "id": "f29f0ad4-3862-ee11-844a-16243b297e85",
                "name": "sboot-hubd-base-orch-avaliacao-store",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "REMOVIDO"
            }
        ],
        "relationships": [
            {
                "id": "3da9c240-6a7f-ef11-84d2-16ffc1277435",
                "type": "ArchiMate:ApplicationServiceApplicationComponentUse",
                "stereotype": "NOVO",
                "source": {
                    "id": "1a2333f4-697f-ef11-84d2-16ffc1277435",
                    "name": "GET /v1/evaluations/{evaluationType}",
                    "type": "ArchiMate:ApplicationService"
                },
                "target": {
                    "id": "bb502786-647f-ef11-84d2-16ffc1277435",
                    "name": "caapi-hubd-base-avaliacao-v1",
                    "type": "ArchiMate:ApplicationComponent"
                }
            },
            {
                "id": "97d5a166-2480-ef11-84d2-16ffe58a20bb",
                "type": "ArchiMate:ApplicationServiceApplicationComponentUse",
                "stereotype": "NOVO",
                "source": {
                    "id": "27dbeac1-697f-ef11-84d2-16ffc1277435",
                    "name": "POST /v1/evaluations/{evaluationType}",
                    "type": "ArchiMate:ApplicationService"
                },
                "target": {
                    "id": "bb502786-647f-ef11-84d2-16ffc1277435",
                    "name": "caapi-hubd-base-avaliacao-v1",
                    "type": "ArchiMate:ApplicationComponent"
                }
            },
            {
                "id": "c72e7260-2080-ef11-84d2-16ffe58a20bb",
                "type": "ArchiMate:ApplicationComponentApplicationServiceRealisation",
                "source": {
                    "id": "bb502786-647f-ef11-84d2-16ffc1277435",
                    "name": "caapi-hubd-base-avaliacao-v1",
                    "type": "ArchiMate:ApplicationComponent"
                },
                "target": {
                    "id": "4680d0d7-647f-ef11-84d2-16ffc1277435",
                    "name": "GET /v1/evaluation/{evaluationType}",
                    "type": "ArchiMate:ApplicationService"
                }
            }
        ],
        "metadata": {
            "elementCount": 33,
            "relationshipCount": 46
        }
    },
    "JT-DEFAULT": {
        "viewInfo": {
            "name": "Visão Técnica - Sistema Padrão",
            "JT": "JT-DEFAULT"
        },
        "elements": [
            {
                "id": "mock-component-1",
                "name": "sboot-exemplo-api",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "NOVO"
            },
            {
                "id": "mock-service-1",
                "name": "GET /v1/exemplo",
                "type": "ArchiMate:ApplicationService",
                "stereotype": "NOVO"
            },
            {
                "id": "mock-component-2",
                "name": "user-service",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "MANTIDO"
            },
            {
                "id": "mock-component-3",
                "name": "auth-module",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "MANTIDO"
            },
            {
                "id": "mock-component-4",
                "name": "notification-service",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "ALTERADO"
            },
            {
                "id": "mock-component-5",
                "name": "api-gateway",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "NOVO"
            }
        ],
        "relationships": [
            {
                "id": "mock-rel-1",
                "type": "ArchiMate:ApplicationComponentApplicationServiceRealisation",
                "stereotype": "NOVO",
                "source": {
                    "id": "mock-component-1",
                    "name": "sboot-exemplo-api",
                    "type": "ArchiMate:ApplicationComponent"
                },
                "target": {
                    "id": "mock-service-1",
                    "name": "GET /v1/exemplo",
                    "type": "ArchiMate:ApplicationService"
                }
            }
        ],
        "metadata": {
            "elementCount": 6,
            "relationshipCount": 1,
            "exportDate": datetime.now().isoformat()
        }
    }
}


def format_validation_result(
    overall_status: str,
    errors: List[str],
    warnings: List[str],
    manual_actions: List[str]
) -> str:
    """Formats validation results with emojis and structured output.
    
    Creates a structured presentation of validation results
    with visual indicators for easy readability.
    
    Args:
        overall_status: Overall validation status.
        errors: List of errors found.
        warnings: List of warnings.
        manual_actions: List of required manual actions.
    
    Returns:
        Formatted string with validation results.
    """
    summary = f"✅ Status: {overall_status}"
    
    if errors:
        summary += f"\n\n❌ Erros ({len(errors)}):"
        for error in errors:
            summary += f"\n- {error}"
    
    if warnings:
        summary += f"\n\n⚠️ Avisos ({len(warnings)}):"
        for warning in warnings:
            summary += f"\n- {warning}"
    
    if manual_actions:
        summary += f"\n\n📋 Ações Manuais Necessárias ({len(manual_actions)}):"
        for action in manual_actions:
            summary += f"\n- {action}"
    
    return summary


def extract_blizzdesign_components(blizzdesign_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extracts application components from BlizzDesign export.
    
    Filters only ApplicationComponent type elements from BlizzDesign
    export and extracts relevant information.
    
    Args:
        blizzdesign_data: BlizzDesign export data.
    
    Returns:
        List of components with extracted information.
    """
    components = []
    
    for element in blizzdesign_data.get("elements", []):
        if element.get("type") == "ArchiMate:ApplicationComponent":
            components.append({
                "name": element.get("name"),
                "stereotype": element.get("stereotype", "MANTIDO"),
                "id": element.get("id"),
                "type": element.get("type")
            })
    
    return components


def format_validation_scope(
    development_cycle: str,
    architecture: str,
    components: List[str]
) -> str:
    """Formats validation scope for ARQCOR forms.
    
    Creates a formatted text describing the validation scope
    including development cycle, architecture type and components.
    
    Args:
        development_cycle: Development cycle identifier.
        architecture: Architecture type.
        components: List of component names.
    
    Returns:
        Formatted validation scope text.
    """
    scope = f"Development Cycle: {development_cycle}\n"
    scope += f"Architecture Type: {architecture}\n"
    scope += f"Components: {', '.join(components)}"
    return scope


def format_version_changes(changes: List[Dict[str, str]]) -> str:
    """Formats version changes for display.
    
    Creates a formatted text showing version changes
    for components in a readable format.
    
    Args:
        changes: List of version change dictionaries.
    
    Returns:
        Formatted version changes text.
    """
    text = "Version Changes:\n"
    for change in changes:
        text += f"- {change['component']}: {change['from_version']} → {change['to_version']}\n"
    return text


def parse_jira_components(components_raw: Any) -> List[str]:
    """Parses Jira components field.
    
    Extracts component names from various Jira field formats.
    
    Args:
        components_raw: Raw components data from Jira.
    
    Returns:
        List of component names.
    """
    if isinstance(components_raw, list):
        return [c.get("name", "") for c in components_raw if isinstance(c, dict)]
    elif isinstance(components_raw, str):
        return [c.strip() for c in components_raw.split(",") if c.strip()]
    return []


def parse_development_cycle(cycle_raw: Any) -> str:
    """Parses development cycle from Jira field.
    
    Extracts development cycle information from various formats.
    
    Args:
        cycle_raw: Raw development cycle data.
    
    Returns:
        Parsed development cycle string.
    """
    if isinstance(cycle_raw, dict):
        return cycle_raw.get("value", "")
    return str(cycle_raw) if cycle_raw else ""


def compare_versions(v1: str, v2: str) -> int:
    """Compares two semantic version strings.
    
    Args:
        v1: First version string.
        v2: Second version string.
    
    Returns:
        -1 if v1 < v2, 0 if equal, 1 if v1 > v2.
    """
    def parse_version(v):
        return [int(x) for x in v.split('.')]
    
    try:
        parts1 = parse_version(v1)
        parts2 = parse_version(v2)
        
        for i in range(max(len(parts1), len(parts2))):
            p1 = parts1[i] if i < len(parts1) else 0
            p2 = parts2[i] if i < len(parts2) else 0
            if p1 < p2:
                return -1
            elif p1 > p2:
                return 1
        return 0
    except:
        return 0


async def get_blizzdesign_export(jt_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKED: Fetches the technical architecture export from BlizzDesign.
    
    Simulates fetching BlizzDesign export data for a specific JT.
    Uses predefined data for known JTs or returns default data.
    
    Args:
        jt_id: The JT (Journey/Template) identifier.
        tool_context: ADK tool context.
    
    Returns:
        Complete BlizzDesign export data in JSON format.
    """
    tool_context.state["use_mock"] = True
    
    if jt_id in BLIZZDESIGN_MOCK_EXPORTS:
        export_data = BLIZZDESIGN_MOCK_EXPORTS[jt_id]
    else:
        export_data = BLIZZDESIGN_MOCK_EXPORTS["JT-DEFAULT"]
        export_data["viewInfo"]["JT"] = jt_id
        export_data["viewInfo"]["name"] = f"Visão Técnica - {jt_id}"
    
    tool_context.state[f"blizzdesign_export_{jt_id}"] = export_data
    tool_context.state[f"blizzdesign_mock_{jt_id}"] = export_data
    
    return export_data


async def parse_blizzdesign_data(
    blizzdesign_json: Dict[str, Any], 
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Parses BlizzDesign export data to extract component information.
    
    Processes raw BlizzDesign JSON export to extract relevant
    component details for validation.
    
    Args:
        blizzdesign_json: Raw BlizzDesign export data.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing parsed component information.
    """
    try:
        view_info = blizzdesign_json.get("viewInfo", {})
        view_name = view_info.get("name", "Unknown")
        jt_id = view_info.get("JT", "")
        
        components = extract_blizzdesign_components(blizzdesign_json)
        
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
        
        metadata = blizzdesign_json.get("metadata", {})
        element_count = metadata.get("elementCount", 0)
        relationship_count = metadata.get("relationshipCount", 0)
        
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


async def get_jira_ticket(ticket_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKED: Retrieves a Jira ticket by its ID.
    
    Simulates different scenarios based on ticket ID for comprehensive
    testing of the validation flow.
    
    Args:
        ticket_id: The Jira ticket identifier.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing ticket information.
    """
    if "ERROR" in ticket_id:
        return {
            "ticket_id": ticket_id,
            "error": "Failed to fetch Jira ticket: Connection timeout"
        }
    
    if ticket_id == "PDI-99999":
        return {
            "ticket_id": "10099999",
            "ticket_key": "PDI-99999",
            "summary": "Deploy empty service",
            "description": "Deploy service without components for testing",
            "status": "In Progress",
            "status_category": "In Progress",
            "assignee": "Maria Santos",
            "reporter": "João Silva",
            "priority": "High",
            "components": [],
            "development_cycle": "Sprint 23",
            "pdi_description": "Deploy service without components",
            "arqcor_id": ""
        }
    
    mock_components = ["user-service", "auth-module", "notification-service"]
    if "GATEWAY" in ticket_id:
        mock_components.append("api-gateway")
    
    internal_id = f"100{ticket_id.split('-')[1]}"
    
    return {
        "ticket_id": internal_id,
        "ticket_key": ticket_id,
        "summary": f"Deploy new services for {ticket_id}",
        "description": f"This is a mock ticket for deploying {', '.join(mock_components)} to production environment.",
        "status": "In Progress",
        "status_category": "In Progress",
        "assignee": "João Silva",
        "reporter": "Ana Costa",
        "priority": "Medium",
        "components": mock_components,
        "development_cycle": "Sprint 23",
        "pdi_description": f"Deploy {', '.join(mock_components)} to production environment",
        "arqcor_id": "ARQCOR-123"
    }


async def get_ticket_components(ticket_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKED: Extracts components from a Jira ticket's Test and Homologation tab.
    
    Specifically looks for components in the custom field designated
    for Test and Homologation information.
    
    Args:
        ticket_id: The Jira ticket identifier.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing component information.
    """
    state_key = f"jira_ticket_{ticket_id}"
    if state_key in tool_context.state:
        components = tool_context.state[state_key].get("components", [])
        return {
            "ticket_id": ticket_id,
            "components": components,
            "count": len(components)
        }
    
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
    """MOCKED: Validates PDI components are properly documented.
    
    Simulates validation of components mentioned in PDI description
    versus components actually listed in the ticket.
    
    Args:
        ticket_id: The PDI ticket identifier.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing validation results.
    """
    if ticket_id == "PDI-DONE":
        return {
            "ticket_id": ticket_id,
            "is_valid": False,
            "components_not_in_description": [],
            "warnings": ["PDI has status 'Done' - cannot proceed with completed PDI"]
        }
    
    if ticket_id == "PDI-INVALID":
        return {
            "ticket_id": ticket_id,
            "is_valid": False,
            "components_not_in_description": ["notification-service"],
            "warnings": ["Component 'notification-service' not mentioned in PDI description"]
        }
    
    return {
        "ticket_id": ticket_id,
        "is_valid": True,
        "components_not_in_description": [],
        "warnings": []
    }


async def validate_components_in_vt(
    ticket_id: str, 
    components: List[str], 
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Validates that all components are approved in the Technical Vision.
    
    Simulates validation of components against Technical Vision (VT)
    to verify they are approved in the reference architecture.
    
    Args:
        ticket_id: The Jira ticket identifier.
        components: List of component names to validate.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing validation results.
    """
    tool_context.state[f"vt_{ticket_id}"] = {
        "vt_id": "VT-2024-001",
        "architecture": "Microservices",
        "approved_components": ["user-service", "auth-module", "notification-service"]
    }
    
    if ticket_id == "PDI-UNAPPROVED":
        return {
            "is_valid": False,
            "unapproved_components": ["payment-service", "billing-service"],
            "approved_components": ["user-service"],
            "vt_id": "VT-2024-001",
            "total_components": 3,
            "validation_rate": "33.3%"
        }
    
    approved = ["user-service", "auth-module", "notification-service", "api-gateway"]
    unapproved = [c for c in components if c not in approved]
    
    if unapproved:
        approved_in_vt = [c for c in components if c in approved]
        return {
            "is_valid": False,
            "unapproved_components": unapproved,
            "approved_components": approved_in_vt,
            "vt_id": "VT-2024-001",
            "total_components": len(components),
            "validation_rate": f"{(len(approved_in_vt)/len(components)*100):.1f}%"
        }
    
    return {
        "is_valid": True,
        "unapproved_components": [],
        "approved_components": components,
        "vt_id": "VT-2024-001",
        "total_components": len(components),
        "validation_rate": "100.0%"
    }


async def get_arqcor_ticket(arqcor_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKED: Retrieves an ARQCOR ticket from Jira.
    
    Fetches ARQCOR issue information including JT field and status.
    
    Args:
        arqcor_id: The ARQCOR ticket identifier.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing ARQCOR ticket information.
    """
    if "ERROR" in arqcor_id:
        return {
            "arqcor_id": arqcor_id,
            "error": "Failed to fetch ARQCOR ticket: Service unavailable"
        }
    
    if arqcor_id == "ARQCOR-INVALID":
        return {
            "arqcor_id": "10003",
            "ticket_key": "ARQCOR-INVALID",
            "status": "Rejected",
            "status_category": "Done",
            "jt_field": "",
            "is_valid": False
        }
    
    return {
        "arqcor_id": "10002",
        "ticket_key": arqcor_id,
        "status": "Open",
        "status_category": "To Do",
        "jt_field": "JT-147338",
        "is_valid": True
    }


async def update_ticket_comment(ticket_id: str, comment: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKED: Adds a comment to a Jira ticket.
    
    Posts a comment to the specified ticket, useful for recording
    validation results or manual action requirements.
    
    Args:
        ticket_id: The Jira ticket identifier.
        comment: Comment text to add.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing operation status.
    """
    if "ERROR" in ticket_id:
        return {
            "ticket_id": ticket_id,
            "success": False,
            "error": "Failed to add comment: Permission denied"
        }
    
    return {
        "ticket_id": ticket_id,
        "success": True
    }


async def create_arqcor_form(
    ticket_id: str,
    evaluator_name: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Creates a new ARQCOR evaluation form in Jira.
    
    Simulates creation of a form in ARQCOR system to document
    architectural adherence validation.
    
    Args:
        ticket_id: Jira ticket identifier.
        evaluator_name: Name of the architect/evaluator.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing form creation results.
    """
    if ticket_id == "PDI-ARQCOR-ERROR":
        return {"error": "Failed to create ARQCOR form: Service unavailable"}
    
    form_id = f"ARQCOR-2024-{random.randint(1000, 9999)}"
    
    tool_context.state[f"arqcor_form_{ticket_id}"] = {
        "form_id": form_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "Draft"
    }
    
    return {
        "form_id": form_id,
        "status": "Draft",
        "form_url": f"https://arqcor.company.com/forms/{form_id}"
    }


async def update_arqcor_form_with_versions(
    form_id: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Updates ARQCOR form with version change information.
    
    Simulates updating an ARQCOR form with version information
    of validated components.
    
    Args:
        form_id: ARQCOR issue key.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing update status.
    """
    if "ERROR" in form_id:
        return {
            "form_id": form_id,
            "error": "Failed to update ARQCOR form: Form locked"
        }
    
    return {
        "form_id": form_id,
        "updated": True
    }


async def add_validation_checklist_to_form(
    form_id: str,
    checklist_items: List[Dict[str, Any]],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Adds validation checklist results to ARQCOR form.
    
    Simulates adding validation checklist items to ARQCOR form.
    
    Args:
        form_id: ARQCOR issue key.
        checklist_items: List of checklist items.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing checklist addition status.
    """
    if "ERROR" in form_id:
        return {
            "form_id": form_id,
            "error": "Failed to add checklist: Database error"
        }
    
    total_items = len(checklist_items)
    approved_items = sum(1 for item in checklist_items if item.get("result") == "SIM")
    
    if approved_items == total_items:
        parecer_final = "Aderente"
    elif approved_items >= total_items * 0.8:
        parecer_final = "Aderente com débito"
    else:
        parecer_final = "Não Aderente"
    
    return {
        "form_id": form_id,
        "checklist_added": True,
        "parecer_final": parecer_final
    }


async def submit_arqcor_form(form_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKED: Submits an ARQCOR form for approval.
    
    Changes the issue status to trigger the approval workflow
    in the ARQCOR project.
    
    Args:
        form_id: ARQCOR issue key.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing submission status.
    """
    if "ERROR" in form_id:
        return {
            "form_id": form_id,
            "error": "Failed to submit ARQCOR form: Invalid state transition"
        }
    
    return {
        "form_id": form_id,
        "status": "Em Avaliação",
        "submitted": True
    }


async def get_arqcor_form_status(form_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKED: Retrieves the current status of an ARQCOR form.
    
    Checks the issue status and form completion state.
    
    Args:
        form_id: ARQCOR issue key.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing form status information.
    """
    if "ERROR" in form_id:
        return {
            "form_id": form_id,
            "error": "Failed to get ARQCOR form status: Form not found"
        }
    
    return {
        "form_id": form_id,
        "status": "Em Avaliação",
        "evaluator": "João Silva",
        "created_at": "2024-01-15T10:00:00Z",
        "submitted_at": "2024-01-15T10:30:00Z",
        "validation_scope": "Development Cycle: Sprint 23\nArchitecture Type: Microservices\nComponents: user-service, auth-module",
        "parecer_final": "Aderente"
    }


async def check_multiple_component_versions(
    components: List[Dict[str, str]],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Checks versions for multiple components at once.
    
    Simulates version checking for multiple components in Portal Tech,
    classifying changes by type (NEW, MAJOR, MINOR, PATCH).
    
    Args:
        components: List of dictionaries with 'name' and 'version'.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing version check results.
    """
    version_changes = []
    new_components = []
    major_changes = []
    components_with_errors = []
    
    for comp in components:
        name = comp["name"]
        version = comp["version"]
        
        if "error" in name.lower():
            components_with_errors.append(name)
            continue
        
        if "new" in name.lower():
            new_components.append(name)
            version_changes.append({
                "component": name,
                "change": f"NEW → {version}",
                "type": "NEW"
            })
        elif "major" in name.lower():
            major_changes.append(name)
            version_changes.append({
                "component": name,
                "change": f"1.5.0 → {version}",
                "type": "MAJOR"
            })
        else:
            old_version = "1.0.0"
            if version.startswith("1.0."):
                change_type = "PATCH"
            elif version.startswith("1."):
                change_type = "MINOR"
            else:
                change_type = "MAJOR"
                major_changes.append(name)
            
            version_changes.append({
                "component": name,
                "change": f"{old_version} → {version}",
                "type": change_type
            })
    
    total = len(components)
    new_count = len(new_components)
    major_count = len(major_changes)
    error_count = len(components_with_errors)
    minor_count = len([vc for vc in version_changes if vc["type"] == "MINOR"])
    patch_count = len([vc for vc in version_changes if vc["type"] == "PATCH"])
    
    summary_parts = [f"{total} components"]
    details = []
    if new_count > 0:
        details.append(f"{new_count} new")
    if major_count > 0:
        details.append(f"{major_count} major updates")
    if minor_count > 0:
        details.append(f"{minor_count} minor updates")
    if patch_count > 0:
        details.append(f"{patch_count} patch updates")
    if error_count > 0:
        details.append(f"{error_count} errors")
    
    summary = summary_parts[0]
    if details:
        summary += ": " + ", ".join(details)
    
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


async def get_repository_info(
    repository_url: str,
    access_token: Optional[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Fetches repository information from Bitbucket API.
    
    Retrieves metadata about a repository including default branch,
    size, and last update timestamp.
    
    Args:
        repository_url: Full URL of the Bitbucket repository.
        access_token: Optional Bitbucket access token.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing repository information.
    """
    if "error" in repository_url.lower():
        return {"error": "Invalid Bitbucket repository URL"}
    
    if "private" in repository_url and not access_token:
        return {"error": "Authentication failed - invalid or missing token"}
    
    repo_name = repository_url.split('/')[-1].replace('.git', '')
    
    return {
        "name": repo_name,
        "full_name": f"company/{repo_name}",
        "default_branch": "main",
        "size": 1048576,
        "updated_on": "2024-01-15T10:30:00Z",
        "is_private": True,
        "language": "Java"
    }


async def list_repository_tags(
    repository_url: str,
    access_token: Optional[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Lists all tags in a Bitbucket repository.
    
    Fetches tags with their associated commit information.
    
    Args:
        repository_url: Full URL of the Bitbucket repository.
        access_token: Optional Bitbucket access token.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing tag information.
    """
    if "error" in repository_url.lower():
        return {
            "error": "Failed to fetch tags: HTTP 404",
            "tags": [],
            "total_count": 0
        }
    
    tags = [
        {
            "name": "v1.2.3",
            "date": "2024-01-15T10:30:00Z",
            "commit": "abc123",
            "message": "Release v1.2.3"
        },
        {
            "name": "v1.2.2",
            "date": "2024-01-10T14:20:00Z",
            "commit": "def456",
            "message": "Hotfix for production issue"
        },
        {
            "name": "v1.2.1",
            "date": "2024-01-05T09:15:00Z",
            "commit": "ghi789",
            "message": "Minor bug fixes"
        }
    ]
    
    return {
        "tags": tags,
        "total_count": len(tags),
        "latest_tag": "v1.2.3"
    }


async def get_file_content(
    repository_url: str,
    file_path: str,
    branch: str,
    access_token: Optional[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Retrieves content of a specific file from Bitbucket repository.
    
    Fetches file content without cloning the entire repository.
    
    Args:
        repository_url: Full URL of the Bitbucket repository.
        file_path: Path to file within repository.
        branch: Branch name to fetch from.
        access_token: Optional Bitbucket access token.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing file content.
    """
    if "error" in repository_url.lower() or "notfound" in file_path.lower():
        return {"error": f"File not found: {file_path}"}
    
    if file_path == "pom.xml":
        content = """<?xml version='1.0' encoding='UTF-8'?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.company</groupId>
    <artifactId>user-service</artifactId>
    <version>1.2.3</version>
    <name>User Service</name>
</project>"""
    elif file_path == "openapi.yaml":
        content = """openapi: 3.0.0
info:
  title: User Service API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
  /users/{id}:
    get:
      summary: Get user by ID"""
    else:
        content = f"Mock content for file: {file_path}"
    
    return {
        "content": content,
        "size": len(content),
        "encoding": "utf-8"
    }


async def list_pull_requests(
    repository_url: str,
    state: str,
    access_token: Optional[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Lists pull requests for a Bitbucket repository.
    
    Fetches pull requests filtered by state.
    
    Args:
        repository_url: Full URL of the Bitbucket repository.
        state: PR state to filter (OPEN, MERGED, DECLINED, ALL).
        access_token: Optional Bitbucket access token.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing pull request information.
    """
    if "error" in repository_url.lower():
        return {
            "error": "Failed to fetch pull requests: HTTP 500",
            "pull_requests": [],
            "total_count": 0
        }
    
    all_prs = [
        {
            "id": 123,
            "title": "Feature: Add new endpoint",
            "state": "OPEN",
            "author": "john.doe",
            "created_on": "2024-01-15T10:30:00Z",
            "updated_on": "2024-01-15T14:20:00Z",
            "source_branch": "feature/new-endpoint",
            "destination_branch": "main",
            "reviewers": ["jane.smith", "bob.wilson"]
        },
        {
            "id": 122,
            "title": "Fix: Security vulnerability",
            "state": "MERGED",
            "author": "jane.smith",
            "created_on": "2024-01-14T09:00:00Z",
            "updated_on": "2024-01-14T16:45:00Z",
            "source_branch": "fix/security-patch",
            "destination_branch": "main",
            "reviewers": ["john.doe"]
        }
    ]
    
    if state != "ALL":
        pull_requests = [pr for pr in all_prs if pr["state"] == state]
    else:
        pull_requests = all_prs
    
    return {
        "pull_requests": pull_requests,
        "total_count": len(pull_requests)
    }


async def check_branch_protection(
    repository_url: str,
    branch: str,
    access_token: Optional[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Checks branch protection rules for a specific branch.
    
    Verifies if a branch has protection rules configured.
    
    Args:
        repository_url: Full URL of the Bitbucket repository.
        branch: Branch name to check.
        access_token: Optional Bitbucket access token.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing branch protection information.
    """
    if "error" in repository_url.lower():
        return {
            "is_protected": False,
            "restrictions": [],
            "required_approvals": 0,
            "error": "Failed to fetch branch restrictions: HTTP 403"
        }
    
    if branch == "main" or branch == "master":
        return {
            "is_protected": True,
            "restrictions": ["no-deletes", "no-force-push", "restrict-merges"],
            "required_approvals": 2
        }
    
    return {
        "is_protected": False,
        "restrictions": [],
        "required_approvals": 0
    }


async def get_technical_vision_by_ticket(ticket_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKED: Retrieves Technical Vision associated with a ticket.
    
    Searches for the VT linked to the specified Jira ticket.
    
    Args:
        ticket_id: The Jira ticket identifier.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing VT information.
    """
    if "ERROR" in ticket_id:
        return {
            "ticket_id": ticket_id,
            "error": "No Technical Vision found for this ticket"
        }
    
    components = ["user-service", "auth-module", "notification-service"]
    if "GATEWAY" in ticket_id:
        components.append("api-gateway")
    
    vt_id = "VT-2024-001"
    
    tool_context.state[f"vt_{ticket_id}"] = {
        "vt_id": vt_id,
        "architecture": "Microservices",
        "approved_components": components
    }
    
    return {
        "vt_id": vt_id,
        "name": "User Management System",
        "architecture": "Microservices",
        "approved_components": components,
        "approval_date": "2024-01-10",
        "valid_until": "2024-12-31"
    }


async def load_local_architecture_data(data_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """MOCKED: Loads architecture data from local JSON files.
    
    Provides a fallback mechanism for loading architecture data.
    
    Args:
        data_dir: Directory containing architecture JSON files.
    
    Returns:
        List of architecture data dictionaries.
    """
    return [
        {
            "_source_file": "architecture_export_2024.json",
            "elements": [
                {
                    "name": "user-service",
                    "type": "ArchiMate:ApplicationComponent",
                    "stereotype": "MANTIDO"
                },
                {
                    "name": "auth-module",
                    "type": "ArchiMate:ApplicationComponent",
                    "stereotype": "MANTIDO"
                },
                {
                    "name": "notification-service",
                    "type": "ArchiMate:ApplicationComponent",
                    "stereotype": "ALTERADO"
                }
            ]
        }
    ]


def parse_component_list_from_text(text: str) -> Dict[str, str]:
    """Extracts components and versions from user input text.
    
    Supports multiple formats for component specification.
    
    Args:
        text: User input text containing component list.
    
    Returns:
        Dictionary mapping component names to versions.
    """
    components = {}
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
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
                components[component_name] = version
        
        else:
            parts = line.split()
            if len(parts) >= 2 and re.match(r'^\d+\.\d+', parts[-1]):
                version = parts[-1]
                component_name = ' '.join(parts[:-1])
                components[component_name] = version
    
    return components


async def validate_components_vs_architecture(
    components: Dict[str, str],
    tool_context: ToolContext,
    use_local_data: bool = False
) -> Dict[str, Any]:
    """MOCKED: Validates components against architecture data with detailed status.
    
    Enhanced validation that checks components against architecture data.
    
    Args:
        components: Dictionary of component names to versions.
        tool_context: ADK tool context.
        use_local_data: Whether to use local JSON files.
    
    Returns:
        Dictionary containing validation results.
    """
    arch_data = await load_local_architecture_data()
    
    found_components = {}
    missing_components = []
    status_breakdown = {
        "NOVO": [],
        "ALTERADO": [],
        "REMOVIDO": [],
        "MANTIDO": [],
        "INDEFINIDO": []
    }
    
    approved_components = ["user-service", "auth-module", "notification-service", "api-gateway"]
    
    for comp_name, expected_version in components.items():
        if comp_name in approved_components:
            stereotype = "MANTIDO"
            if "new" in comp_name.lower():
                stereotype = "NOVO"
            elif "notification" in comp_name:
                stereotype = "ALTERADO"
            
            found_components[comp_name] = {
                "version": expected_version,
                "status": stereotype,
                "element_name": comp_name,
                "source": "architecture_export_2024.json"
            }
            
            status_breakdown[stereotype].append(comp_name)
        else:
            missing_components.append(comp_name)
    
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


async def search_component_by_name(
    component_name: str,
    tool_context: ToolContext,
    use_local_data: bool = False
) -> Dict[str, Any]:
    """MOCKED: Searches for a specific component in architecture data.
    
    Performs case-insensitive search for components by name.
    
    Args:
        component_name: Name or partial name of component.
        tool_context: ADK tool context.
        use_local_data: Whether to use local JSON files.
    
    Returns:
        Dictionary containing search results.
    """
    all_components = [
        {"name": "user-service", "type": "ApplicationComponent", "stereotype": "MANTIDO"},
        {"name": "auth-module", "type": "ApplicationComponent", "stereotype": "MANTIDO"},
        {"name": "notification-service", "type": "ApplicationComponent", "stereotype": "ALTERADO"},
        {"name": "api-gateway", "type": "ApplicationComponent", "stereotype": "NOVO"},
        {"name": "user-management-bff", "type": "ApplicationComponent", "stereotype": "NOVO"}
    ]
    
    search_term = component_name.lower()
    matches = []
    
    for comp in all_components:
        if search_term in comp["name"].lower():
            matches.append({
                "name": comp["name"],
                "type": comp["type"],
                "stereotype": comp["stereotype"],
                "source": "architecture_export_2024.json",
                "properties": {}
            })
    
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


async def list_all_components_by_status(
    tool_context: ToolContext,
    status_filter: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """MOCKED: Lists all components grouped by their status.
    
    Provides a comprehensive view of all components grouped by stereotype.
    
    Args:
        tool_context: ADK tool context.
        status_filter: Optional filter for specific status.
        limit: Maximum components per status group.
    
    Returns:
        Dictionary containing components grouped by status.
    """
    all_components = [
        {"name": "user-service", "version": "1.2.3", "stereotype": "MANTIDO"},
        {"name": "auth-module", "version": "2.0.1", "stereotype": "MANTIDO"},
        {"name": "notification-service", "version": "1.5.0", "stereotype": "ALTERADO"},
        {"name": "payment-service", "version": "1.0.0", "stereotype": "ALTERADO"},
        {"name": "api-gateway", "version": "1.0.0", "stereotype": "NOVO"},
        {"name": "analytics-service", "version": "1.0.0", "stereotype": "NOVO"},
        {"name": "legacy-auth", "version": "0.9.0", "stereotype": "REMOVIDO"},
        {"name": "old-payment", "version": "0.5.0", "stereotype": "REMOVIDO"}
    ]
    
    components_by_status = {
        "NOVO": [],
        "ALTERADO": [],
        "REMOVIDO": [],
        "MANTIDO": [],
        "INDEFINIDO": []
    }
    
    for comp in all_components:
        stereotype = comp["stereotype"]
        
        if not status_filter or status_filter == stereotype:
            components_by_status[stereotype].append({
                "name": comp["name"],
                "version": comp["version"],
                "type": "ApplicationComponent"
            })
    
    for status in components_by_status:
        if len(components_by_status[status]) > limit:
            components_by_status[status] = components_by_status[status][:limit]
    
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


async def get_openapi_contract(
    vt_id: str, 
    component_name: str, 
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Retrieves OpenAPI contract for a component from VT.
    
    Fetches the API contract specification associated with a component.
    
    Args:
        vt_id: Technical Vision identifier.
        component_name: Name of the component.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing contract information.
    """
    if "error" in component_name.lower():
        return {
            "component_name": component_name,
            "error": "No OpenAPI contract found for this component"
        }
    
    if component_name in ["user-service", "auth-module", "api-gateway"]:
        endpoints = ["/users", "/users/{id}", "/auth/login", "/auth/logout"]
        
        tool_context.state[f"contract_{component_name}"] = {
            "has_contract": True,
            "version": "3.0.0",
            "endpoints": endpoints
        }
        
        return {
            "component_name": component_name,
            "has_contract": True,
            "contract_version": "3.0.0",
            "endpoints": endpoints[:10],
            "total_endpoints": len(endpoints),
            "contract_url": f"https://api.example.com/contracts/{component_name}/openapi.yaml"
        }
    
    return {
        "component_name": component_name,
        "has_contract": False,
        "error": "No OpenAPI contract found for this component"
    }


async def clone_repository(
    repository_url: str,
    tool_context: ToolContext,
    branch: str = "main",
) -> Dict[str, Any]:
    """MOCKED: Clones a Git repository to a temporary directory for analysis.
    
    Simulates repository cloning for testing purposes.
    
    Args:
        repository_url: Full URL of the Git repository.
        branch: Branch to clone.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing clone status.
    """
    if "error" in repository_url.lower():
        return {
            "success": False,
            "error": "Git clone failed: Authentication failed"
        }
    
    if "notfound" in repository_url.lower():
        return {
            "success": False,
            "error": "Git clone failed: Repository not found"
        }
    
    repo_name = repository_url.split('/')[-1].replace('.git', '')
    temp_path = f"/tmp/mock_{repo_name}_{random.randint(1000, 9999)}"
    
    return {
        "success": True,
        "path": temp_path
    }


async def analyze_project_structure(
    repo_path: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Analyzes the structure of a cloned repository.
    
    Identifies project type, build system, and validates structure.
    
    Args:
        repo_path: Path to the cloned repository.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing project analysis.
    """
    if "error" in repo_path.lower():
        return {
            "project_type": "unknown",
            "build_system": "unknown",
            "structure_valid": False,
            "missing_directories": [],
            "detected_files": [],
            "error": "Failed to analyze structure: Permission denied"
        }
    
    if "maven" in repo_path.lower() or "java" in repo_path.lower():
        return {
            "project_type": "java",
            "build_system": "maven",
            "structure_valid": True,
            "missing_directories": [],
            "detected_files": ["pom.xml", "src/main/java", "src/test/java", "src/main/resources/openapi.yaml"]
        }
    
    if "node" in repo_path.lower() or "npm" in repo_path.lower():
        return {
            "project_type": "node",
            "build_system": "npm",
            "structure_valid": True,
            "missing_directories": [],
            "detected_files": ["package.json", "src", "test", "docs/openapi.yaml"]
        }
    
    return {
        "project_type": "java",
        "build_system": "maven",
        "structure_valid": False,
        "missing_directories": ["src/main/resources"],
        "detected_files": ["pom.xml", "src/main/java"]
    }


async def validate_dependencies(
    repo_path: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Validates project dependencies for vulnerabilities and deprecations.
    
    Checks dependency files for deprecated libraries and security issues.
    
    Args:
        repo_path: Path to the cloned repository.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing dependency validation results.
    """
    if "error" in repo_path.lower():
        return {
            "dependencies_valid": False,
            "deprecated_dependencies": [],
            "security_issues": [],
            "total_dependencies": 0,
            "error": "Failed to validate dependencies: File not found"
        }
    
    if "vulnerable" in repo_path.lower():
        return {
            "dependencies_valid": False,
            "deprecated_dependencies": ["commons-lang:commons-lang:2.6 - Use commons-lang3 instead"],
            "security_issues": ["Log4j version vulnerable to CVE-2021-44228"],
            "total_dependencies": 15
        }
    
    return {
        "dependencies_valid": True,
        "deprecated_dependencies": [],
        "security_issues": [],
        "total_dependencies": 25
    }


async def find_openapi_spec(
    repo_path: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Searches for OpenAPI/Swagger specification files in repository.
    
    Looks for OpenAPI specs in common locations.
    
    Args:
        repo_path: Path to the cloned repository.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing OpenAPI spec information.
    """
    if "error" in repo_path.lower():
        return {
            "has_openapi": False,
            "spec_locations": [],
            "spec_version": None,
            "validation_errors": [],
            "error": "Failed to find OpenAPI spec: Permission denied"
        }
    
    if "noapi" in repo_path.lower():
        return {
            "has_openapi": False,
            "spec_locations": [],
            "spec_version": None,
            "validation_errors": []
        }
    
    return {
        "has_openapi": True,
        "spec_locations": ["src/main/resources/openapi.yaml", "docs/api-spec.yaml"],
        "spec_version": "3.0",
        "validation_errors": []
    }


async def cleanup_repository(
    repo_path: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Cleans up a cloned repository directory.
    
    Removes the temporary directory created during repository analysis.
    
    Args:
        repo_path: Path to the cloned repository.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing cleanup status.
    """
    if "error" in repo_path.lower():
        return {
            "success": False,
            "error": "Failed to cleanup: Directory not found"
        }
    
    return {"success": True}


async def detect_project_type(repo_root: Path) -> Dict[str, str]:
    """Detects project type and build system from repository files.
    
    Args:
        repo_root: Path to repository root.
    
    Returns:
        Dictionary with project_type and build_system.
    """
    if str(repo_root).endswith("java"):
        return {
            "project_type": "java",
            "build_system": "maven"
        }
    elif str(repo_root).endswith("node"):
        return {
            "project_type": "node",
            "build_system": "npm"
        }
    
    return {
        "project_type": "unknown",
        "build_system": "unknown"
    }


def get_required_directories(project_type: str, build_system: str) -> List[str]:
    """Gets list of required directories based on project type.
    
    Args:
        project_type: Type of project.
        build_system: Build system in use.
    
    Returns:
        List of required directory paths.
    """
    if project_type == "java":
        if build_system == "maven":
            return ["src/main/java", "src/main/resources"]
        elif build_system == "gradle":
            return ["src/main/java"]
    elif project_type == "node":
        return ["src"]
    
    return []


async def get_production_version(component_name: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKED: Retrieves the current production version of a component.
    
    Queries Component (Portal Tech) API to find the production version.
    
    Args:
        component_name: Name of the component to query.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing version information.
    """
    if "error" in component_name.lower():
        return {
            "component": component_name,
            "error": "API returned status code 500"
        }
    
    if "notfound" in component_name.lower():
        return {
            "component": component_name,
            "production_version": None,
            "found": False,
            "source": "api"
        }
    
    version_map = {
        "user-service": "2.0.5",
        "auth-module": "1.4.2",
        "notification-service": "1.3.0",
        "api-gateway": None
    }
    
    production_version = version_map.get(component_name, "1.0.0")
    
    if production_version:
        tool_context.state[f"portal_tech_version_{component_name}"] = production_version
    
    return {
        "component": component_name,
        "production_version": production_version,
        "found": production_version is not None,
        "source": "api"
    }


async def get_component_versions(component_name: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKED: Retrieves component versions across different environments.
    
    Queries Component (Portal Tech) API to find versions in all environments.
    
    Args:
        component_name: Name of the component to query.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing environment versions.
    """
    if "error" in component_name.lower():
        return {
            "component": component_name,
            "error": "API returned status code 500"
        }
    
    if "notfound" in component_name.lower():
        return {
            "component": component_name,
            "current_prd_version": None,
            "current_uat_version": None,
            "current_des_version": None,
            "found": False
        }
    
    versions = {
        "PRD": "2.0.5",
        "UAT": "2.0.6",
        "DES": "2.1.0-dev"
    }
    
    tool_context.state[f"portal_tech_versions_{component_name}"] = versions
    
    return {
        "component": component_name,
        "current_prd_version": versions["PRD"],
        "current_uat_version": versions["UAT"],
        "current_des_version": versions["DES"],
        "found": True
    }


async def compare_component_versions(
    component_name: str,
    deployment_version: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Compares deployment version with production version.
    
    Retrieves production version and compares with deployment version.
    
    Args:
        component_name: Name of the component.
        deployment_version: Version to be deployed.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing version comparison.
    """
    prod_info = await get_production_version(component_name, tool_context)
    
    if "error" in prod_info:
        return prod_info
    
    production_version = prod_info.get("production_version")
    
    if not production_version:
        change_type = "NEW"
        version_change = f"NEW → {deployment_version}"
        is_major_change = True
    else:
        version_change = f"{production_version} → {deployment_version}"
        
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


async def get_component_details(component_name: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKED: Retrieves detailed information about a component.
    
    Fetches comprehensive component information from Portal Tech.
    
    Args:
        component_name: Name of the component.
        tool_context: ADK tool context.
    
    Returns:
        Dictionary containing component details.
    """
    if "error" in component_name.lower():
        return {
            "component": component_name,
            "error": "API returned status code 500"
        }
    
    if "notfound" in component_name.lower():
        return {
            "component": component_name,
            "error": "Component not found"
        }
    
    return {
        "component": component_name,
        "description": "User management service",
        "production_version": "2.0.5",
        "team": "User Experience Team",
        "repository": f"https://github.com/company/{component_name}",
        "technology": {"name": "Java", "version": "17"},
        "last_deployment": "2024-01-10T15:30:00Z",
        "portal_url": f"https://portaltech.bvnet.bv/components/{component_name}"
    }


def _extract_environment_versions(env_versions: List[Dict[str, Any]]) -> Dict[str, Optional[str]]:
    """Extracts versions for each environment from API response.
    
    Args:
        env_versions: List of environment version objects.
    
    Returns:
        Dictionary mapping environment names to versions.
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
    
    Args:
        component_data: Component data object from API.
    
    Returns:
        Dictionary containing processed component information.
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