"""ARQCOR integration tools for Feito/Conferido agent.

Provides tools for creating and managing Solution Adherence
Evaluation forms in the ARQCOR system through Jira API.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from google.adk.tools import ToolContext

from ...utils.http_clients import get_jira_client
from ...utils.formatters import format_validation_scope, format_version_changes
from ...config.settings import get_settings


async def create_arqcor_form(
    ticket_id: str,
    evaluator_name: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Creates a new ARQCOR evaluation form in Jira.

    Generates a Solution Adherence Evaluation issue in Jira with initial
    data from the validation process, following the ARQCOR project schema.

    Args:
        ticket_id: Jira ticket identifier (PDI or JT).
        evaluator_name: Name of the architect/evaluator.
        tool_context: ADK tool context containing validation data.

    Returns:
        Dictionary containing:
            - form_id: Generated ARQCOR issue key (e.g., "ARQCOR-123")
            - status: Issue status (e.g., "Draft")
            - form_url: URL to access the Jira issue
            - error: Error message if creation failed

    Example:
        >>> result = await create_arqcor_form("PDI-12345", "João Silva", tool_context)
        >>> print(result)
        {
            "form_id": "ARQCOR-2024-001",
            "status": "Draft",
            "form_url": "https://jira.company.com/browse/ARQCOR-2024-001"
        }
    """
    settings = get_settings()
    
    try:
        # Get validation data from context
        jira_data = tool_context.state.get(f"jira_ticket_{ticket_id}", {})
        vt_data = tool_context.state.get(f"vt_{ticket_id}", {})
        
        if not jira_data or not vt_data:
            return {
                "error": "Missing validation data. Please run component validation first."
            }
        
        # Extract required data
        development_cycle = jira_data.get("development_cycle", "")
        components = jira_data.get("components", [])
        architecture = vt_data.get("architecture", "TO-BE")
        
        # Format validation scope according to template
        validation_scope = format_validation_scope(
            development_cycle,
            architecture,
            components
        )
        
        # Prepare Jira issue creation payload
        issue_data = {
            "fields": {
                "project": {
                    "key": settings.arqcor.project_key  # Should be "ARQCOR"
                },
                "issuetype": {
                    "name": "Formulário de Avaliação"  # Custom issue type for ARQCOR
                },
                "summary": f"Avaliação de Aderência - {ticket_id}",
                "description": f"Formulário de Avaliação de Aderência de Solução para {ticket_id}",
                # Custom fields specific to ARQCOR forms
                "customfield_arquiteto_responsavel": evaluator_name,  # Architect responsible
                "customfield_escopo_validacao": validation_scope,     # Validation scope
                "customfield_ticket_origem": ticket_id,              # Source ticket
                "customfield_data_avaliacao": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "customfield_status_formulario": "Draft"             # Form status
            }
        }
        
        # Create issue via Jira API
        client = await get_jira_client()
        response = await client.post("/rest/api/2/issue", json=issue_data)
        result = response.json()
        
        form_id = result.get("key")  # Jira issue key (e.g., "ARQCOR-123")
        
        # Store form ID in context for later operations
        tool_context.state[f"arqcor_form_{ticket_id}"] = {
            "form_id": form_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "Draft"
        }
        
        return {
            "form_id": form_id,
            "status": "Draft",
            "form_url": f"{settings.jira.base_url}/browse/{form_id}"
        }
        
    except Exception as e:
        return {
            "error": f"Failed to create ARQCOR form: {str(e)}"
        }


async def update_arqcor_form_with_versions(
    form_id: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Updates ARQCOR form with version change information.

    Adds the version comparison results to the validation scope
    field in the ARQCOR Jira issue.

    Args:
        form_id: ARQCOR issue key (e.g., "ARQCOR-123").
        tool_context: ADK tool context containing version check results.

    Returns:
        Dictionary containing:
            - form_id: ARQCOR issue key
            - updated: Boolean indicating if update was successful
            - error: Error message if update failed

    Example:
        >>> result = await update_arqcor_form_with_versions("ARQCOR-2024-001", tool_context)
        >>> print(result)
        {"form_id": "ARQCOR-2024-001", "updated": True}
    """
    try:
        # Get version check results from context
        version_results = tool_context.state.get("version_check_results", {})
        
        if not version_results:
            return {
                "form_id": form_id,
                "error": "No version check results found. Please run version check first."
            }
        
        # Format version changes according to ARQCOR template
        version_changes = version_results.get("version_changes", [])
        changes_formatted = []
        
        for change in version_changes:
            if " → " in change["change"]:
                from_version = change["change"].split(" → ")[0]
                to_version = change["change"].split(" → ")[1]
            else:
                from_version = "NEW"
                to_version = change["change"].replace("NEW → ", "")
                
            changes_formatted.append({
                "component": change["component"],
                "from_version": from_version,
                "to_version": to_version
            })
        
        version_text = format_version_changes(changes_formatted)
        
        # Get current form data from Jira
        client = await get_jira_client()
        response = await client.get(f"/rest/api/2/issue/{form_id}")
        current_issue = response.json()
        
        # Update validation scope with version information
        current_scope = current_issue["fields"].get("customfield_escopo_validacao", "")
        updated_scope = current_scope + "\n\n" + version_text
        
        # Update issue via Jira API
        update_data = {
            "fields": {
                "customfield_escopo_validacao": updated_scope
            }
        }
        
        await client.put(f"/rest/api/2/issue/{form_id}", json=update_data)
        
        # Store update info in context
        tool_context.state[f"arqcor_form_versions_updated_{form_id}"] = True
        
        return {
            "form_id": form_id,
            "updated": True
        }
        
    except Exception as e:
        return {
            "form_id": form_id,
            "error": f"Failed to update ARQCOR form: {str(e)}"
        }


async def add_validation_checklist_to_form(
    form_id: str,
    checklist_items: List[Dict[str, Any]],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Adds validation checklist results to ARQCOR form.

    Updates the form with detailed validation checklist items
    for code and contract validation results, following the
    ARQCOR criteria structure.

    Args:
        form_id: ARQCOR issue key.
        checklist_items: List of checklist items with 'criteria', 'result', and 'notes'.
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - form_id: ARQCOR issue key
            - checklist_added: Boolean indicating if checklist was added
            - error: Error message if update failed

    Example:
        >>> checklist = [
        ...     {
        ...         "criteria": "Componentes implementados conforme VT",
        ...         "result": "SIM",
        ...         "notes": "Todos os componentes estão presentes"
        ...     },
        ...     {
        ...         "criteria": "Contratos OpenAPI implementados",
        ...         "result": "NÃO",
        ...         "notes": "Faltando contrato para user-service"
        ...     }
        ... ]
        >>> result = await add_validation_checklist_to_form("ARQCOR-2024-001", checklist, tool_context)
        >>> print(result)
        {"form_id": "ARQCOR-2024-001", "checklist_added": True}
    """
    try:
        # Format checklist according to ARQCOR criteria structure
        checklist_text = "\n\nChecklist de Validação de Aderência:\n"
        
        for i, item in enumerate(checklist_items, 1):
            status_emoji = "✅" if item["result"] == "SIM" else "❌"
            checklist_text += f"\n{i}. {item['criteria']}"
            checklist_text += f"\n   Resposta: {item['result']} {status_emoji}"
            if item.get("notes"):
                checklist_text += f"\n   Observação: {item['notes']}"
            checklist_text += "\n"
        
        # Get current issue from Jira
        client = await get_jira_client()
        response = await client.get(f"/rest/api/2/issue/{form_id}")
        current_issue = response.json()
        
        # Update validation scope with checklist
        current_scope = current_issue["fields"].get("customfield_escopo_validacao", "")
        updated_scope = current_scope + checklist_text
        
        # Calculate overall result
        total_items = len(checklist_items)
        approved_items = sum(1 for item in checklist_items if item["result"] == "SIM")
        
        # Determine final opinion based on checklist results
        if approved_items == total_items:
            parecer_final = "Aderente"
        elif approved_items >= total_items * 0.8:  # 80% threshold
            parecer_final = "Aderente com débito"
        else:
            parecer_final = "Não Aderente"
        
        # Update issue with checklist and final opinion
        update_data = {
            "fields": {
                "customfield_escopo_validacao": updated_scope,
                "customfield_parecer_final": parecer_final,
                "customfield_checklist_completo": True
            }
        }
        
        await client.put(f"/rest/api/2/issue/{form_id}", json=update_data)
        
        return {
            "form_id": form_id,
            "checklist_added": True,
            "parecer_final": parecer_final
        }
        
    except Exception as e:
        return {
            "form_id": form_id,
            "error": f"Failed to add checklist to ARQCOR form: {str(e)}"
        }


async def submit_arqcor_form(form_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Submits an ARQCOR form for approval.

    Changes the issue status to trigger the approval workflow
    in the ARQCOR project.

    Args:
        form_id: ARQCOR issue key.
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - form_id: ARQCOR issue key
            - status: New issue status
            - submitted: Boolean indicating if submission was successful
            - error: Error message if submission failed

    Example:
        >>> result = await submit_arqcor_form("ARQCOR-2024-001", tool_context)
        >>> print(result)
        {"form_id": "ARQCOR-2024-001", "status": "Em Avaliação", "submitted": True}
    """
    try:
        client = await get_jira_client()
        
        # Transition issue to "Em Avaliação" status
        transition_data = {
            "transition": {
                "id": "41"  # Transition ID for "Submit for Review" (needs to be configured)
            }
        }
        
        await client.post(f"/rest/api/2/issue/{form_id}/transitions", json=transition_data)
        
        # Update form status field
        update_data = {
            "fields": {
                "customfield_status_formulario": "Em Avaliação",
                "customfield_data_submissao": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        await client.put(f"/rest/api/2/issue/{form_id}", json=update_data)
        
        return {
            "form_id": form_id,
            "status": "Em Avaliação",
            "submitted": True
        }
        
    except Exception as e:
        return {
            "form_id": form_id,
            "error": f"Failed to submit ARQCOR form: {str(e)}"
        }


async def get_arqcor_form_status(form_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieves the current status of an ARQCOR form.

    Checks the issue status and form completion state.

    Args:
        form_id: ARQCOR issue key.
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - form_id: ARQCOR issue key
            - status: Current issue status
            - evaluator: Name of evaluator
            - created_at: Issue creation date
            - submitted_at: Form submission date (if submitted)
            - validation_scope: Current validation scope content
            - parecer_final: Final evaluation result
            - error: Error message if retrieval failed

    Example:
        >>> result = await get_arqcor_form_status("ARQCOR-2024-001", tool_context)
        >>> print(result)
        {
            "form_id": "ARQCOR-2024-001",
            "status": "Em Avaliação",
            "evaluator": "João Silva",
            "created_at": "2024-01-15T10:00:00Z",
            "submitted_at": "2024-01-15T10:30:00Z",
            "validation_scope": "...",
            "parecer_final": "Aderente"
        }
    """
    try:
        client = await get_jira_client()
        
        response = await client.get(f"/rest/api/2/issue/{form_id}")
        issue_data = response.json()
        
        fields = issue_data.get("fields", {})
        
        return {
            "form_id": form_id,
            "status": fields.get("status", {}).get("name", "Unknown"),
            "evaluator": fields.get("customfield_arquiteto_responsavel", ""),
            "created_at": fields.get("created", ""),
            "submitted_at": fields.get("customfield_data_submissao", ""),
            "validation_scope": fields.get("customfield_escopo_validacao", ""),
            "parecer_final": fields.get("customfield_parecer_final", "")
        }
        
    except Exception as e:
        return {
            "form_id": form_id,
            "error": f"Failed to get ARQCOR form status: {str(e)}"
        }
