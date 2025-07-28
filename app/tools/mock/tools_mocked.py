"""Main validation tools for Feito/Conferido process with MOCKED responses.

Provides the primary validation tool that orchestrates
the complete Feito/Conferido validation workflow.

THIS VERSION CONTAINS MOCKED RESPONSES FOR TESTING!
"""

from typing import Dict, List, Any, Optional
from google.adk.tools import ToolContext
from datetime import datetime
import random


# ===== BLIZZDESIGN MOCK DATA =====
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


# ===== MOCK HELPER FUNCTIONS =====

def format_validation_result(
    overall_status: str,
    errors: List[str],
    warnings: List[str],
    manual_actions: List[str]
) -> str:
    """Mock formatter for validation results."""
    summary = f"✅ Status: {overall_status}"
    
    if errors:
        summary += f"\n\n❌ Errors ({len(errors)}):"
        for error in errors:
            summary += f"\n- {error}"
    
    if warnings:
        summary += f"\n\n⚠️ Warnings ({len(warnings)}):"
        for warning in warnings:
            summary += f"\n- {warning}"
    
    if manual_actions:
        summary += f"\n\n📋 Manual Actions Required ({len(manual_actions)}):"
        for action in manual_actions:
            summary += f"\n- {action}"
    
    return summary


def extract_blizzdesign_components(blizzdesign_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extracts application components from BlizzDesign export."""
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


# ===== MOCK VT/BLIZZDESIGN FUNCTIONS =====

async def get_blizzdesign_export(jt_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKED: Returns mock BlizzDesign export data."""
    # Store mock flag in context
    tool_context.state["use_mock"] = True
    
    # Check if we have specific mock data for this JT
    if jt_id in BLIZZDESIGN_MOCK_EXPORTS:
        export_data = BLIZZDESIGN_MOCK_EXPORTS[jt_id]
    else:
        # Return default mock data
        export_data = BLIZZDESIGN_MOCK_EXPORTS["JT-DEFAULT"]
        # Update JT ID to match request
        export_data["viewInfo"]["JT"] = jt_id
        export_data["viewInfo"]["name"] = f"Visão Técnica - {jt_id}"
    
    # Store in context for reuse
    tool_context.state[f"blizzdesign_export_{jt_id}"] = export_data
    tool_context.state[f"blizzdesign_mock_{jt_id}"] = export_data
    
    return export_data


async def parse_blizzdesign_data(
    blizzdesign_json: Dict[str, Any], 
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Parses BlizzDesign export data."""
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


# ===== MOCK JIRA FUNCTIONS =====

async def get_jira_ticket(ticket_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKED: Returns mock Jira ticket data matching real API structure."""
    # Simulate different scenarios based on ticket ID
    if "ERROR" in ticket_id:
        return {
            "ticket_id": ticket_id,
            "error": "Failed to fetch Jira ticket: Connection timeout"
        }
    
    if ticket_id == "PDI-99999":
        # Mock ticket with no components
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
    
    # Default mock response with full structure
    mock_components = ["user-service", "auth-module", "notification-service"]
    if "GATEWAY" in ticket_id:
        mock_components.append("api-gateway")
    
    # Generate internal ID from ticket ID
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


async def validate_pdi_components(ticket_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKED: Returns mock PDI validation result."""
    # Simulate different scenarios
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
    
    # Default: valid PDI
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
    """MOCKED: Returns mock VT validation result."""
    # Store in context for later use
    tool_context.state[f"vt_{ticket_id}"] = {
        "vt_id": "VT-2024-001",
        "architecture": "Microservices",
        "approved_components": ["user-service", "auth-module", "notification-service"]
    }
    
    # Simulate unapproved components
    if ticket_id == "PDI-UNAPPROVED":
        return {
            "is_valid": False,
            "unapproved_components": ["payment-service", "billing-service"],
            "approved_components": ["user-service"],
            "vt_id": "VT-2024-001"
        }
    
    # Check if any component is not in the approved list
    approved = ["user-service", "auth-module", "notification-service", "api-gateway"]
    unapproved = [c for c in components if c not in approved]
    
    if unapproved:
        return {
            "is_valid": False,
            "unapproved_components": unapproved,
            "approved_components": [c for c in components if c in approved],
            "vt_id": "VT-2024-001"
        }
    
    # Default: all components approved
    return {
        "is_valid": True,
        "unapproved_components": [],
        "approved_components": components,
        "vt_id": "VT-2024-001"
    }


# ===== MOCK ARQCOR FUNCTIONS =====

async def create_arqcor_form(
    ticket_id: str,
    evaluator_name: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Returns mock ARQCOR form creation result."""
    # Simulate error scenario
    if ticket_id == "PDI-ARQCOR-ERROR":
        return {"error": "Failed to create ARQCOR form: Service unavailable"}
    
    # Generate mock form ID
    form_id = f"ARQCOR-2024-{random.randint(1000, 9999)}"
    
    # Store in context
    tool_context.state[f"arqcor_form_{ticket_id}"] = {
        "form_id": form_id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    return {
        "form_id": form_id,
        "status": "draft",
        "form_url": f"https://arqcor.company.com/forms/{form_id}"
    }


async def update_arqcor_form_with_versions(
    form_id: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Returns mock ARQCOR update result."""
    # Simulate error scenario
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
    """MOCKED: Returns mock checklist addition result."""
    # Simulate error scenario
    if "ERROR" in form_id:
        return {
            "form_id": form_id,
            "error": "Failed to add checklist: Database error"
        }
    
    return {
        "form_id": form_id,
        "checklist_added": True
    }


# ===== MOCK PORTAL TECH FUNCTIONS =====

async def check_multiple_component_versions(
    components: List[Dict[str, str]],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Returns mock version check result matching real API structure."""
    version_changes = []
    new_components = []
    major_changes = []
    components_with_errors = []
    
    for comp in components:
        name = comp["name"]
        version = comp["version"]
        
        # Simulate error for specific component names
        if "error" in name.lower():
            components_with_errors.append(name)
            continue
        
        # Simulate different scenarios
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
            # Simulate minor version change
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
    
    # Build summary
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
    
    # Store in context
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
