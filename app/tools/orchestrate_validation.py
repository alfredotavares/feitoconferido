from google.adk.tools import ToolContext
from typing import Dict, Any, Optional

from app.sub_agents import (
    component_validation_agent,
    arqcor_form_agent,
    version_check_agent,
    code_validation_agent
)


async def orchestrate_validation(
    ticket_id: str,
    evaluator_name: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Orchestrates the complete Feito/Conferido validation using subagents.

    Coordinates all four validation stages through specialized subagents,
    each handling their specific domain of expertise.

    Args:
        ticket_id: Jira ticket identifier (PDI or JT).
        evaluator_name: Name of the architect performing validation.
        tool_context: ADK tool context for state management.

    Returns:
        Dictionary containing complete validation results from all stages.

    Example:
        >>> result = await orchestrate_validation("PDI-12345", "João Silva", tool_context)
        >>> print(result["overall_status"])
        "APPROVED"
    """
    # Initialize tracking
    stages_completed = []
    errors = []
    warnings = []
    manual_actions = []
    overall_status = "APPROVED"
    arqcor_form_id = None
    
    # Store validation context
    tool_context.state[f"validation_{ticket_id}"] = {
        "started_at": "now",
        "evaluator": evaluator_name
    }
    
    # Stage 1: Component Validation
    try:
        component_result = await component_validation_agent.run(
            ticket_id=ticket_id,
            tool_context=tool_context
        )
        
        if component_result["status"] == "FAILED":
            errors.append(f"Stage 1: {component_result.get('error', 'Component validation failed')}")
            overall_status = "FAILED"
            return _build_orchestration_response(
                ticket_id, overall_status, stages_completed,
                errors, warnings, manual_actions, arqcor_form_id
            )
        
        if component_result["status"] == "WARNING":
            warnings.extend(component_result.get("warnings", []))
        
        components = component_result.get("components", [])
        stages_completed.append("Component Validation")
        
    except Exception as e:
        errors.append(f"Stage 1: Subagent error - {str(e)}")
        overall_status = "FAILED"
        return _build_orchestration_response(
            ticket_id, overall_status, stages_completed,
            errors, warnings, manual_actions, arqcor_form_id
        )
    
    # Stage 2: ARQCOR Form Creation
    try:
        form_result = await arqcor_form_agent.run(
            ticket_id=ticket_id,
            evaluator_name=evaluator_name,
            operation="create",
            tool_context=tool_context
        )
        
        if form_result["status"] == "FAILED":
            errors.append(f"Stage 2: {form_result.get('error', 'Form creation failed')}")
            overall_status = "FAILED"
            return _build_orchestration_response(
                ticket_id, overall_status, stages_completed,
                errors, warnings, manual_actions, arqcor_form_id
            )
        
        arqcor_form_id = form_result.get("form_id")
        stages_completed.append("ARQCOR Form Creation")
        
    except Exception as e:
        errors.append(f"Stage 2: Subagent error - {str(e)}")
        overall_status = "FAILED"
        return _build_orchestration_response(
            ticket_id, overall_status, stages_completed,
            errors, warnings, manual_actions, arqcor_form_id
        )
    
    # Stage 3: Version Check
    try:
        # Prepare components with versions (would come from ticket in production)
        components_with_versions = [
            {"name": comp, "version": "1.0.0"} for comp in components
        ]
        
        version_result = await version_check_agent.run(
            components=components_with_versions,
            tool_context=tool_context
        )
        
        if version_result["status"] in ["WARNING", "FAILED"]:
            warnings.extend(version_result.get("warnings", []))
            manual_actions.extend(version_result.get("manual_actions", []))
        
        # Update ARQCOR form with version info
        if arqcor_form_id and version_result.get("version_changes"):
            await arqcor_form_agent.run(
                ticket_id=ticket_id,
                evaluator_name=evaluator_name,
                operation="update_versions",
                form_id=arqcor_form_id,
                tool_context=tool_context
            )
        
        stages_completed.append("Version Check")
        
    except Exception as e:
        warnings.append(f"Stage 3: Subagent error - {str(e)}")
        manual_actions.append("Manual version verification required")
    
    # Stage 4: Code/Contract Validation
    try:
        code_result = await code_validation_agent.run(
            components=components,
            repository_urls=None,  # Would be populated in production
            tool_context=tool_context
        )
        
        if code_result["status"] == "FAILED":
            errors.append(f"Stage 4: Code validation failed")
            overall_status = "FAILED"
        elif code_result["status"] == "WARNING":
            warnings.extend(code_result.get("warnings", []))
        
        manual_actions.extend(code_result.get("manual_actions", []))
        
        # Add checklist to ARQCOR form
        if arqcor_form_id and code_result.get("checklist_items"):
            await arqcor_form_agent.run(
                ticket_id=ticket_id,
                evaluator_name=evaluator_name,
                operation="add_checklist",
                form_id=arqcor_form_id,
                update_data={"checklist_items": code_result["checklist_items"]},
                tool_context=tool_context
            )
        
        stages_completed.append("Code/Contract Validation")
        
    except Exception as e:
        warnings.append(f"Stage 4: Subagent error - {str(e)}")
        manual_actions.append("Manual code validation required")
    
    # Determine final status
    if errors:
        overall_status = "FAILED"
    elif manual_actions:
        overall_status = "REQUIRES_MANUAL_ACTION"
    
    return _build_orchestration_response(
        ticket_id, overall_status, stages_completed,
        errors, warnings, manual_actions, arqcor_form_id
    )


def _build_orchestration_response(
    ticket_id: str,
    overall_status: str,
    stages_completed: list,
    errors: list,
    warnings: list,
    manual_actions: list,
    arqcor_form_id: Optional[str] = None
) -> Dict[str, Any]:
    """Build the final orchestration response.
    
    Formats the complete validation results from all subagents
    into a comprehensive response.
    """
    # Format summary
    summary = f"Status: {overall_status}\n"
    
    if errors:
        summary += f"\nErrors ({len(errors)}):\n"
        for error in errors:
            summary += f"- {error}\n"
    
    if warnings:
        summary += f"\nWarnings ({len(warnings)}):\n"
        for warning in warnings:
            summary += f"- {warning}\n"
    
    if manual_actions:
        summary += f"\nManual Actions Required ({len(manual_actions)}):\n"
        for action in manual_actions:
            summary += f"- {action}\n"
    
    # Add stage completion info
    total_stages = 4
    completed_count = len(stages_completed)
    
    if completed_count < total_stages:
        summary += f"\nStages completed: {completed_count}/{total_stages}\n"
        if stages_completed:
            summary += f"✓ {', '.join(stages_completed)}"
    else:
        summary += f"\nAll {total_stages} validation stages completed successfully"
    
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
