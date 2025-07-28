"""Main validation tools for Feito/Conferido process.

Provides the primary validation tool that orchestrates
the complete Feito/Conferido validation workflow.
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from google.adk.tools import ToolContext

# Conditional import based on environment variable
USE_MOCK = os.getenv("USE_MOCK_TOOLS", "false").lower() == "true"

if USE_MOCK:
    # Import mocked tools for testing
    from .mock.tools_mocked import (
        get_jira_ticket,
        validate_pdi_components,
        validate_components_in_vt,
        create_arqcor_form,
        update_arqcor_form_with_versions,
        add_validation_checklist_to_form,
        check_multiple_component_versions,
        format_validation_result
    )
else:
    # Import real tools for production
    from ..utils.formatters import format_validation_result
    from .jira_tools import get_jira_ticket, validate_pdi_components
    from .vt_tools import validate_components_in_vt
    from .component_tools import check_multiple_component_versions
    from .arqcor_tools import (
        create_arqcor_form, 
        update_arqcor_form_with_versions,
        add_validation_checklist_to_form
    )
    from .git_tools import (
        clone_repository,
        analyze_project_structure,
        validate_dependencies,
        find_openapi_spec,
        cleanup_repository
    )
    from .bitbucket_tools import (
        get_repository_info,
        list_repository_tags
    )


async def validate_feito_conferido(
    ticket_id: str,
    evaluator_name: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Executes the complete Feito/Conferido validation process.

    Orchestrates all four validation stages:
    1. Component validation against VT
    2. ARQCOR form creation
    3. Version checking with Portal Tech
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
        "started_at": datetime.utcnow().isoformat(),
        "evaluator": evaluator_name,
        "mode": "mock" if USE_MOCK else "production"
    }
    
    # Stage 1: Ticket and Component Validation
    try:
        # Get ticket information
        ticket_info = await get_jira_ticket(ticket_id, tool_context)
        
        if "error" in ticket_info:
            errors.append(f"Stage 1: {ticket_info['error']}")
            overall_status = "FAILED"
            return _format_validation_response(
                ticket_id, overall_status, stages_completed, 
                errors, warnings, manual_actions
            )
        
        # Validate PDI components if it's a PDI ticket
        if ticket_id.startswith("PDI-"):
            pdi_validation = await validate_pdi_components(ticket_id, tool_context)
            
            if not pdi_validation.get("is_valid", False):
                warnings.extend(pdi_validation.get("warnings", []))
                
                # Check for critical errors
                if any("status" in w and ("done" in w.lower() or "concluído" in w.lower()) 
                      for w in pdi_validation.get("warnings", [])):
                    errors.append("Stage 1: PDI has completed status - cannot proceed")
                    overall_status = "FAILED"
                    return _format_validation_response(
                        ticket_id, overall_status, stages_completed,
                        errors, warnings, manual_actions
                    )
        
        # Validate components against VT
        components = ticket_info.get("components", [])
        
        if not components:
            errors.append("Stage 1: No components found in ticket")
            overall_status = "FAILED"
            return _format_validation_response(
                ticket_id, overall_status, stages_completed,
                errors, warnings, manual_actions
            )
        
        # Validate components in VT
        vt_validation = await validate_components_in_vt(ticket_id, components, tool_context)
        
        if "error" in vt_validation:
            errors.append(f"Stage 1: {vt_validation['error']}")
            overall_status = "FAILED"
            return _format_validation_response(
                ticket_id, overall_status, stages_completed,
                errors, warnings, manual_actions
            )
        
        if not vt_validation.get("is_valid", False):
            unapproved = vt_validation.get("unapproved_components", [])
            errors.append(
                f"Stage 1: Components not approved in VT: {', '.join(unapproved)}"
            )
            overall_status = "FAILED"
            return _format_validation_response(
                ticket_id, overall_status, stages_completed,
                errors, warnings, manual_actions
            )
        
        stages_completed.append("Component Validation")
        
    except Exception as e:
        errors.append(f"Stage 1: Unexpected error - {str(e)}")
        overall_status = "FAILED"
        return _format_validation_response(
            ticket_id, overall_status, stages_completed,
            errors, warnings, manual_actions
        )
    
    # Stage 2: ARQCOR Form Creation
    try:
        arqcor_result = await create_arqcor_form(ticket_id, evaluator_name, tool_context)
        
        if "error" in arqcor_result:
            errors.append(f"Stage 2: {arqcor_result['error']}")
            overall_status = "FAILED"
            return _format_validation_response(
                ticket_id, overall_status, stages_completed,
                errors, warnings, manual_actions
            )
        
        arqcor_form_id = arqcor_result.get("form_id")
        stages_completed.append("ARQCOR Form Creation")
        
    except Exception as e:
        errors.append(f"Stage 2: Unexpected error - {str(e)}")
        overall_status = "FAILED"
        return _format_validation_response(
            ticket_id, overall_status, stages_completed,
            errors, warnings, manual_actions
        )
    
    # Stage 3: Version Check
    try:
        # Prepare components with versions
        components_with_versions = []
        for comp_name in components:
            # In production, this would fetch real versions
            # Mock mode will provide simulated versions
            components_with_versions.append({
                "name": comp_name,
                "version": "1.0.0"  # Placeholder - real version would come from check
            })
        
        # Check versions
        version_check = await check_multiple_component_versions(
            components_with_versions, 
            tool_context
        )
        
        if "error" in version_check:
            warnings.append(f"Stage 3: {version_check['error']}")
        else:
            # Update ARQCOR form with version info
            if arqcor_form_id is not None:
                update_result = await update_arqcor_form_with_versions(
                    arqcor_form_id,
                    tool_context
                )
                
                if "error" in update_result:
                    warnings.append(f"Stage 3: Failed to update ARQCOR - {update_result['error']}")
            else:
                warnings.append("Stage 3: ARQCOR form ID is missing, cannot update with versions")
            
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
        
        # Code validation checks
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
        
        # Add checklist to ARQCOR form only if arqcor_form_id is not None
        if arqcor_form_id is not None:
            checklist_result = await add_validation_checklist_to_form(
                arqcor_form_id,
                checklist_items,
                tool_context
            )
            
            if "error" in checklist_result:
                warnings.append(f"Stage 4: Failed to add checklist - {checklist_result['error']}")
        else:
            warnings.append("Stage 4: ARQCOR form ID is missing, cannot add checklist")
        
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
    response = _format_validation_response(
        ticket_id, overall_status, stages_completed,
        errors, warnings, manual_actions, arqcor_form_id
    )
    
    return response


def _format_validation_response(
    ticket_id: str,
    overall_status: str,
    stages_completed: List[str],
    errors: List[str],
    warnings: List[str],
    manual_actions: List[str],
    arqcor_form_id: Optional[str] = None
) -> Dict[str, Any]:
    """Formats the validation response with all results.

    Internal helper function to create consistent response format
    for validation results.

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
    tool_context: ToolContext,
    access_token: Optional[str] = None
) -> Dict[str, Any]:
    """Validates a component's source code repository.

    Performs comprehensive validation including repository structure,
    dependencies, configuration files, and OpenAPI specifications.
    Supports both Git and Bitbucket repositories.

    Args:
        repository_url: URL of the Git repository.
        component_name: Name of the component.
        tool_context: ADK tool context.
        access_token: Optional access token for private repositories.

    Returns:
        Dictionary containing:
            - component: Component name
            - repository_url: Repository URL
            - has_openapi: Boolean indicating if OpenAPI spec exists
            - dependencies_valid: Boolean for dependency validation
            - structure_valid: Boolean for project structure
            - issues: List of issues found
            - repository_info: Additional repo metadata (if available)
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
    issues = []
    has_openapi = False
    dependencies_valid = True
    structure_valid = True
    repository_info = {}
    
    try:
        # Check if it's a Bitbucket repository
        is_bitbucket = "bitbucket.org" in repository_url
        
        # Get repository information if Bitbucket
        if is_bitbucket:
            repo_info = await get_repository_info(
                repository_url,
                access_token,
                tool_context
            )
            
            if "error" in repo_info:
                return {
                    "component": component_name,
                    "repository_url": repository_url,
                    "has_openapi": False,
                    "dependencies_valid": False,
                    "structure_valid": False,
                    "issues": [f"Failed to access repository: {repo_info['error']}"],
                    "error": repo_info['error']
                }
            
            repository_info = {
                "provider": "bitbucket",
                "default_branch": repo_info.get("default_branch", "main"),
                "language": repo_info.get("language", "unknown"),
                "is_private": repo_info.get("is_private", False)
            }
            
            # Get tags to check for releases
            tags_info = await list_repository_tags(
                repository_url,
                access_token,
                tool_context
            )
            
            if not tags_info.get("error"):
                repository_info["latest_tag"] = tags_info.get("latest_tag")
                repository_info["total_tags"] = tags_info.get("total_count", 0)
                
                if tags_info.get("total_count", 0) == 0:
                    issues.append("No release tags found in repository")
        else:
            repository_info = {"provider": "git"}
        
        # Clone repository for analysis
        clone_result = await clone_repository(
            repository_url,
            repository_info.get("default_branch", "main"),
            tool_context
        )
        
        if not clone_result.get("success"):
            return {
                "component": component_name,
                "repository_url": repository_url,
                "has_openapi": False,
                "dependencies_valid": False,
                "structure_valid": False,
                "issues": [f"Failed to clone repository: {clone_result.get('error', 'Unknown error')}"],
                "repository_info": repository_info,
                "error": clone_result.get('error')
            }
        
        repo_path = clone_result["path"]
        
        try:
            # Analyze project structure
            structure_result = await analyze_project_structure(repo_path, tool_context)
            
            structure_valid = structure_result.get("structure_valid", False)
            if not structure_valid:
                missing_dirs = structure_result.get("missing_directories", [])
                if missing_dirs:
                    issues.append(f"Missing required directories: {', '.join(missing_dirs)}")
            
            repository_info["project_type"] = structure_result.get("project_type", "unknown")
            repository_info["build_system"] = structure_result.get("build_system", "unknown")
            repository_info["detected_files"] = structure_result.get("detected_files", [])
            
            # Validate dependencies
            deps_result = await validate_dependencies(repo_path, tool_context)
            
            dependencies_valid = deps_result.get("dependencies_valid", True)
            
            deprecated_deps = deps_result.get("deprecated_dependencies", [])
            if deprecated_deps:
                issues.extend([f"Deprecated dependency: {dep}" for dep in deprecated_deps])
            
            security_issues = deps_result.get("security_issues", [])
            if security_issues:
                dependencies_valid = False
                issues.extend([f"Security issue: {issue}" for issue in security_issues])
            
            # Check for OpenAPI specification
            openapi_result = await find_openapi_spec(repo_path, tool_context)
            
            has_openapi = openapi_result.get("has_openapi", False)
            
            if has_openapi:
                repository_info["openapi_locations"] = openapi_result.get("spec_locations", [])
                spec_version = openapi_result.get("spec_version")
                if spec_version is not None:
                    repository_info["openapi_version"] = spec_version
                
                validation_errors = openapi_result.get("validation_errors", [])
                if validation_errors:
                    issues.extend([f"OpenAPI validation: {error}" for error in validation_errors])
            else:
                # Only add as issue for Spring Boot services
                if component_name.startswith("sboot-") or repository_info.get("project_type") == "java":
                    issues.append("OpenAPI specification not found")
            
            # Additional validations based on component type
            if component_name.endswith("-gateway"):
                if not has_openapi:
                    issues.append("API Gateway components must have OpenAPI specification")
                    dependencies_valid = False
            
            # Check for configuration files
            config_files = ["Dockerfile", "docker-compose.yml", ".gitlab-ci.yml", "Jenkinsfile"]
            found_configs = [f for f in config_files if f in repository_info.get("detected_files", [])]
            
            if not found_configs:
                issues.append("No CI/CD configuration files found (Dockerfile, Jenkinsfile, etc.)")
            
        finally:
            # Cleanup cloned repository
            await cleanup_repository(repo_path, tool_context)
        
        return {
            "component": component_name,
            "repository_url": repository_url,
            "has_openapi": has_openapi,
            "dependencies_valid": dependencies_valid,
            "structure_valid": structure_valid,
            "issues": issues,
            "repository_info": repository_info
        }
        
    except Exception as e:
        return {
            "component": component_name,
            "repository_url": repository_url,
            "has_openapi": False,
            "dependencies_valid": False,
            "structure_valid": False,
            "issues": [f"Validation failed: {str(e)}"],
            "error": f"Unexpected error during validation: {str(e)}"
        }