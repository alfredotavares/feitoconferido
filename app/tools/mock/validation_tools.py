"""Main validation tools for Feito/Conferido process with MOCKED responses.

Provides the primary validation tool that orchestrates
the complete Feito/Conferido validation workflow.

THIS VERSION CONTAINS MOCKED RESPONSES FOR TESTING!
"""

from typing import Dict, List, Any, Optional
from google.adk.tools import ToolContext
from datetime import datetime
import random

# Note: These imports would be used in production
# from ..utils.formatters import format_validation_result
# from .jira_tools import get_jira_ticket, validate_pdi_components
# from .vt_tools import validate_components_in_vt
# from .portal_tech_tools import check_multiple_component_versions
# from .arqcor_tools import (
#     create_arqcor_form, 
#     update_arqcor_form_with_versions,
#     add_validation_checklist_to_form
# )


# MOCK: Format validation result
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


# MOCK: Get Jira ticket
async def get_jira_ticket(ticket_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKED: Returns mock Jira ticket data."""
    # Simulate different scenarios based on ticket ID
    if "ERROR" in ticket_id:
        return {"error": "Failed to fetch Jira ticket: Connection timeout"}
    
    if ticket_id == "PDI-99999":
        # Mock ticket with no components
        return {
            "ticket_id": ticket_id,
            "summary": "Deploy empty service",
            "status": "In Progress",
            "components": [],
            "development_cycle": "Sprint 23",
            "description": "Deploy service without components",
            "arqcor_id": ""
        }
    
    # Default mock response
    mock_components = ["user-service", "auth-module", "notification-service"]
    if "GATEWAY" in ticket_id:
        mock_components.append("api-gateway")
    
    return {
        "ticket_id": ticket_id,
        "summary": f"Deploy new services for {ticket_id}",
        "status": "In Progress",
        "components": mock_components,
        "development_cycle": "Sprint 23",
        "description": f"Deploy {', '.join(mock_components)} to production environment",
        "arqcor_id": "ARQCOR-123"
    }


# MOCK: Validate PDI components
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


# MOCK: Validate components in VT
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


# MOCK: Create ARQCOR form
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


# MOCK: Check multiple component versions
async def check_multiple_component_versions(
    components: List[Dict[str, str]],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKED: Returns mock version check result."""
    version_changes = []
    new_components = []
    major_changes = []
    
    for comp in components:
        name = comp["name"]
        version = comp["version"]
        
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
                "change": "1.5.0 → 2.0.0",
                "type": "MAJOR"
            })
        else:
            # Simulate minor version change
            version_changes.append({
                "component": name,
                "change": "1.0.0 → 1.1.0",
                "type": "MINOR"
            })
    
    # Store in context
    tool_context.state["version_check_results"] = {
        "version_changes": version_changes,
        "new_components": new_components,
        "major_changes": major_changes
    }
    
    return {
        "total_components": len(components),
        "version_changes": version_changes,
        "new_components": new_components,
        "major_changes": major_changes,
        "components_with_errors": [],
        "summary": f"{len(components)} components: {len(new_components)} new, {len(major_changes)} major updates"
    }


# MOCK: Update ARQCOR form with versions
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


# MOCK: Add validation checklist to form
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


# Main validation functions for Feito/Conferido process

async def validate_feito_conferido(
    ticket_id: str,
    evaluator_name: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Executes the complete Feito/Conferido validation process.

    Orchestrates all four validation stages:
    1. Component validation against VT
    2. ARQCOR form creation
    3. Version checking with Component (Portal Tech)
    4. Code/contract validation

    Args:
        ticket_id: Jira ticket identifier (PDI or JT).
        evaluator_name: Name of the architect performing validation.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing:
            - ticket_id: The validated ticket
            - overall_status: APPROVED, FAILED, or REQUIRES_MANUAL_ACTION
            - stages_completed: List of completed stages
            - errors: List of validation errors
            - warnings: List of validation warnings
            - manual_actions: List of required manual actions
            - arqcor_form_id: Generated ARQCOR form ID
            - summary: Human-readable validation summary

    Example:
        >>> result = await validate_feito_conferido("PDI-12345", "João Silva", tool_context)
        >>> print(result["overall_status"])
        "APPROVED"
        >>> print(result["summary"])
        "✅ Status: APPROVED\n\n✅ All 4 validation stages completed successfully"
    """
    stages_completed = []
    errors = []
    warnings = []
    manual_actions = []
    overall_status = "APPROVED"
    
    # Initialize validation tracking
    tool_context.state[f"validation_{ticket_id}"] = {
        "started_at": "now",
        "evaluator": evaluator_name
    }
    
    # Stage 1: Ticket and Component Validation
    try:
        # PRODUCTION CODE COMMENTED:
        # ticket_info = await get_jira_ticket(ticket_id, tool_context)
        
        # MOCK: Get ticket information
        ticket_info = await get_jira_ticket(ticket_id, tool_context)
        
        if "error" in ticket_info:
            errors.append(f"Stage 1: {ticket_info['error']}")
            overall_status = "FAILED"
            return _build_validation_response(
                ticket_id, overall_status, stages_completed, 
                errors, warnings, manual_actions
            )
        
        # Validate PDI components if it's a PDI ticket
        if ticket_id.startswith("PDI-"):
            # PRODUCTION CODE COMMENTED:
            # pdi_validation = await validate_pdi_components(ticket_id, tool_context)
            
            # MOCK: Validate PDI
            pdi_validation = await validate_pdi_components(ticket_id, tool_context)
            
            if not pdi_validation.get("is_valid", False):
                warnings.extend(pdi_validation.get("warnings", []))
                
                # Check for critical errors
                if any("status" in w and ("done" in w.lower() or "concluído" in w.lower()) 
                      for w in pdi_validation.get("warnings", [])):
                    errors.append("Stage 1: PDI has completed status - cannot proceed")
                    overall_status = "FAILED"
                    return _build_validation_response(
                        ticket_id, overall_status, stages_completed,
                        errors, warnings, manual_actions
                    )
        
        # Validate components against VT
        components = ticket_info.get("components", [])
        
        if not components:
            errors.append("Stage 1: No components found in ticket")
            overall_status = "FAILED"
            return _build_validation_response(
                ticket_id, overall_status, stages_completed,
                errors, warnings, manual_actions
            )
        
        # PRODUCTION CODE COMMENTED:
        # vt_validation = await validate_components_in_vt(ticket_id, components, tool_context)
        
        # MOCK: Validate components in VT
        vt_validation = await validate_components_in_vt(ticket_id, components, tool_context)
        
        if "error" in vt_validation:
            errors.append(f"Stage 1: {vt_validation['error']}")
            overall_status = "FAILED"
            return _build_validation_response(
                ticket_id, overall_status, stages_completed,
                errors, warnings, manual_actions
            )
        
        if not vt_validation.get("is_valid", False):
            unapproved = vt_validation.get("unapproved_components", [])
            errors.append(
                f"Stage 1: Components not approved in VT: {', '.join(unapproved)}"
            )
            overall_status = "FAILED"
            return _build_validation_response(
                ticket_id, overall_status, stages_completed,
                errors, warnings, manual_actions
            )
        
        stages_completed.append("Component Validation")
        
    except Exception as e:
        errors.append(f"Stage 1: Unexpected error - {str(e)}")
        overall_status = "FAILED"
        return _build_validation_response(
            ticket_id, overall_status, stages_completed,
            errors, warnings, manual_actions
        )
    
    # Stage 2: ARQCOR Form Creation
    try:
        # PRODUCTION CODE COMMENTED:
        # arqcor_result = await create_arqcor_form(ticket_id, evaluator_name, tool_context)
        
        # MOCK: Create ARQCOR form
        arqcor_result = await create_arqcor_form(ticket_id, evaluator_name, tool_context)
        
        if "error" in arqcor_result:
            errors.append(f"Stage 2: {arqcor_result['error']}")
            overall_status = "FAILED"
            return _build_validation_response(
                ticket_id, overall_status, stages_completed,
                errors, warnings, manual_actions
            )
        
        arqcor_form_id = arqcor_result.get("form_id")
        stages_completed.append("ARQCOR Form Creation")
        
    except Exception as e:
        errors.append(f"Stage 2: Unexpected error - {str(e)}")
        overall_status = "FAILED"
        return _build_validation_response(
            ticket_id, overall_status, stages_completed,
            errors, warnings, manual_actions
        )
    
    # Stage 3: Version Check
    try:
        # Prepare components with versions
        components_with_versions = []
        for comp_name in components:
            # MOCK: Add some variety to versions
            if "new" in comp_name.lower():
                version = "1.0.0"
            elif "major" in comp_name.lower():
                version = "2.0.0"
            else:
                version = "1.1.0"
            
            components_with_versions.append({
                "name": comp_name,
                "version": version
            })
        
        # PRODUCTION CODE COMMENTED:
        # version_check = await check_multiple_component_versions(
        #     components_with_versions, 
        #     tool_context
        # )
        
        # MOCK: Check versions
        version_check = await check_multiple_component_versions(
            components_with_versions, 
            tool_context
        )
        
        if "error" in version_check:
            warnings.append(f"Stage 3: {version_check['error']}")
        else:
            # Update ARQCOR form with version info
            # PRODUCTION CODE COMMENTED:
            # update_result = await update_arqcor_form_with_versions(
            #     arqcor_form_id,
            #     tool_context
            # )
            
            # MOCK: Update ARQCOR
            update_result = await update_arqcor_form_with_versions(
                arqcor_form_id, # type: ignore
                tool_context
            )
            
            if "error" in update_result:
                warnings.append(f"Stage 3: Failed to update ARQCOR - {update_result['error']}")
            
            # Check for major version changes
            major_changes = version_check.get("major_changes", [])
            if major_changes:
                warnings.append(
                    f"Stage 3: Major version changes detected for: {', '.join(major_changes)}"
                )
            
            # Check for components with errors
            error_components = version_check.get("components_with_errors", [])
            if error_components:
                warnings.append(
                    f"Stage 3: Could not check versions for: {', '.join(error_components)}"
                )
                manual_actions.append(
                    f"Manually verify versions for: {', '.join(error_components)}"
                )
        
        stages_completed.append("Version Check")
        
    except Exception as e:
        warnings.append(f"Stage 3: Unexpected error - {str(e)}")
        manual_actions.append("Manual version verification required")
    
    # Stage 4: Code/Contract Validation
    try:
        # Prepare validation checklist
        checklist_items = []
        
        # Check for API Gateway components
        api_gateway_components = [c for c in components if c.endswith("-gateway")]
        
        if api_gateway_components:
            manual_actions.append(
                f"API Gateway components detected ({', '.join(api_gateway_components)}): "
                "Update BizzDesign and Confluence DAP if endpoints differ from VT"
            )
            checklist_items.append({
                "item": "API Gateway endpoint validation",
                "result": "MANUAL",
                "notes": "Manual verification required for API Gateway endpoints"
            })
        
        # Simulate code validation checks
        checklist_items.extend([
            {
                "item": "Dependencies validation",
                "result": "PASS",
                "notes": "All dependencies are in approved list"
            },
            {
                "item": "Security vulnerabilities scan",
                "result": "PASS",
                "notes": "No critical vulnerabilities found"
            },
            {
                "item": "OpenAPI contract validation",
                "result": "PASS" if not api_gateway_components else "MANUAL",
                "notes": "Contracts match VT specifications" if not api_gateway_components 
                        else "API Gateway contracts may differ - manual check required"
            }
        ])
        
        # Add checklist to ARQCOR form
        # PRODUCTION CODE COMMENTED:
        # checklist_result = await add_validation_checklist_to_form(
        #     arqcor_form_id,
        #     checklist_items,
        #     tool_context
        # )
        
        # MOCK: Add checklist
        checklist_result = await add_validation_checklist_to_form(
            arqcor_form_id, # type: ignore
            checklist_items,
            tool_context
        )
        
        if "error" in checklist_result:
            warnings.append(f"Stage 4: Failed to add checklist - {checklist_result['error']}")
        
        stages_completed.append("Code/Contract Validation")
        
    except Exception as e:
        warnings.append(f"Stage 4: Unexpected error - {str(e)}")
        manual_actions.append("Manual code and contract validation required")
    
    # Determine final status
    if errors:
        overall_status = "FAILED"
    elif manual_actions:
        overall_status = "REQUIRES_MANUAL_ACTION"
    else:
        overall_status = "APPROVED"
    
    # Build final response
    response = _build_validation_response(
        ticket_id, overall_status, stages_completed,
        errors, warnings, manual_actions, arqcor_form_id
    )
    
    return response


def _build_validation_response(
    ticket_id: str,
    overall_status: str,
    stages_completed: List[str],
    errors: List[str],
    warnings: List[str],
    manual_actions: List[str],
    arqcor_form_id: Optional[str] = None
) -> Dict[str, Any]:
    """Builds the validation response dictionary.

    Args:
        ticket_id: Validated ticket ID.
        overall_status: Final validation status.
        stages_completed: List of completed stages.
        errors: List of errors encountered.
        warnings: List of warnings.
        manual_actions: List of manual actions required.
        arqcor_form_id: Generated ARQCOR form ID if available.

    Returns:
        Formatted validation response dictionary.
    """
    # Format summary
    summary = format_validation_result(overall_status, errors, warnings, manual_actions)
    
    # Add stage completion info
    total_stages = 4
    completed_count = len(stages_completed)
    
    if completed_count < total_stages:
        summary += f"\n\n📊 Stages completed: {completed_count}/{total_stages}"
        if stages_completed:
            summary += f"\n✓ {', '.join(stages_completed)}"
    else:
        summary += f"\n\n✅ All {total_stages} validation stages completed successfully"
    
    response = {
        "ticket_id": ticket_id,
        "overall_status": overall_status,
        "stages_completed": stages_completed,
        "stages_total": total_stages,
        "errors": errors,
        "warnings": warnings,
        "manual_actions": manual_actions,
        "summary": summary
    }
    
    if arqcor_form_id:
        response["arqcor_form_id"] = arqcor_form_id
        response["arqcor_form_url"] = f"https://arqcor.company.com/forms/{arqcor_form_id}"
    
    return response


async def validate_code_repository(
    repository_url: str,
    component_name: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Validates a component's source code repository.

    Checks repository structure, dependencies, and configuration files.

    Args:
        repository_url: URL of the Git repository.
        component_name: Name of the component.
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - component: Component name
            - repository_url: Repository URL
            - has_openapi: Boolean indicating if OpenAPI spec exists
            - dependencies_valid: Boolean for dependency validation
            - structure_valid: Boolean for project structure
            - issues: List of issues found
            - error: Error message if validation failed

    Example:
        >>> result = await validate_code_repository(
        ...     "https://github.com/company/user-service",
        ...     "user-service",
        ...     tool_context
        ... )
        >>> print(result)
        {
            "component": "user-service",
            "repository_url": "https://github.com/company/user-service",
            "has_openapi": True,
            "dependencies_valid": True,
            "structure_valid": True,
            "issues": []
        }
    """
    # MOCK: Simulate different scenarios based on component name
    issues = []
    has_openapi = True
    dependencies_valid = True
    structure_valid = True
    
    if "legacy" in component_name.lower():
        has_openapi = False
        issues.append("OpenAPI specification not found")
    
    if "deprecated" in component_name.lower():
        dependencies_valid = False
        issues.append("Using deprecated dependencies: commons-lang:2.6")
    
    if "broken" in component_name.lower():
        structure_valid = False
        issues.append("Missing required directory: src/main/resources")
    
    return {
        "component": component_name,
        "repository_url": repository_url,
        "has_openapi": has_openapi,
        "dependencies_valid": dependencies_valid,
        "structure_valid": structure_valid,
        "issues": issues,
        "note": "MOCKED validation - for testing purposes"
    }