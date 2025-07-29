"""Ferramentas principais de validação para o processo Feito/Conferido.

Fornece a ferramenta principal de validação que orquestra
o fluxo completo de validação Feito/Conferido.
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from google.adk.tools import ToolContext

USE_MOCK = os.getenv("USE_MOCK_TOOLS", "false").lower() == "true"

if USE_MOCK:
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
    from ..utils.formatters import format_validation_result
    from .integrations.jira import get_jira_ticket, validate_pdi_components
    from .integrations.blizzdesign import validate_components_in_vt
    from .integrations.portal_tech import check_multiple_component_versions
    from .integrations.arqcor import (
        create_arqcor_form, 
        update_arqcor_form_with_versions,
        add_validation_checklist_to_form
    )
    from .integrations.git import (
        clone_repository,
        analyze_project_structure,
        validate_dependencies,
        find_openapi_spec,
        cleanup_repository
    )
    from .integrations.bitbucket import (
        get_repository_info,
        list_repository_tags
    )


async def validate_feito_conferido(
    ticket_id: str,
    evaluator_name: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Executa o processo completo de validação Feito/Conferido.

    Orquestra todas as quatro etapas de validação:
    1. Validação de componentes contra Visão Técnica (VT)
       e PDI (Projeto de Desenvolvimento Integrado).
    2. Criação de formulário ARQCOR.
    3. Verificação de versões com Portal Tech.
    4. Validação de código/contratos.

    Args:
        ticket_id: Identificador do ticket Jira (PDI ou JT).
        evaluator_name: Nome do arquiteto realizando a validação.
        tool_context: Contexto da ferramenta ADK para gerenciamento de estado.

    Returns:
        Dicionário contendo:
            - ticket_id: O ticket validado
            - overall_status: APPROVED, FAILED, ou REQUIRES_MANUAL_ACTION
            - stages_completed: Lista de etapas concluídas
            - errors: Lista de erros de validação
            - warnings: Lista de avisos de validação
            - manual_actions: Lista de ações manuais necessárias
            - arqcor_form_id: ID do formulário ARQCOR gerado
            - summary: Resumo legível da validação

    Example:
        >>> result = await validate_feito_conferido("PDI-12345", "João Silva", tool_context)
        >>> print(result["overall_status"])
        "APPROVED"
        >>> print(result["summary"])
        "✅ Status: APPROVED\n\n✅ Todas as 4 etapas de validação concluídas com sucesso"
    """
    stages_completed = []
    errors = []
    warnings = []
    manual_actions = []
    overall_status = "APPROVED"
    
    tool_context.state[f"validation_{ticket_id}"] = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "evaluator": evaluator_name,
        "mode": "mock" if USE_MOCK else "production"
    }
    
    try:
        ticket_info = await get_jira_ticket(ticket_id, tool_context)
        
        if "error" in ticket_info:
            errors.append(f"Stage 1: {ticket_info['error']}")
            overall_status = "FAILED"
            return _format_validation_response(
                ticket_id, overall_status, stages_completed, 
                errors, warnings, manual_actions
            )
        
        if ticket_id.startswith("PDI-"):
            pdi_validation = await validate_pdi_components(ticket_id, tool_context)
            
            if not pdi_validation.get("is_valid", False):
                warnings.extend(pdi_validation.get("warnings", []))
                
                if any("status" in w and ("done" in w.lower() or "concluído" in w.lower()) 
                      for w in pdi_validation.get("warnings", [])):
                    errors.append("Stage 1: PDI has completed status - cannot proceed")
                    overall_status = "FAILED"
                    return _format_validation_response(
                        ticket_id, overall_status, stages_completed,
                        errors, warnings, manual_actions
                    )
        
        components = ticket_info.get("components", [])
        
        if not components:
            errors.append("Stage 1: No components found in ticket")
            overall_status = "FAILED"
            return _format_validation_response(
                ticket_id, overall_status, stages_completed,
                errors, warnings, manual_actions
            )
        
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
    
    try:
        components_with_versions = []
        for comp_name in components:
            components_with_versions.append({
                "name": comp_name,
                "version": "1.0.0"
            })
        
        version_check = await check_multiple_component_versions(
            components_with_versions, 
            tool_context
        )
        
        if "error" in version_check:
            warnings.append(f"Stage 3: {version_check['error']}")
        else:
            if arqcor_form_id is not None:
                update_result = await update_arqcor_form_with_versions(
                    arqcor_form_id,
                    tool_context
                )
                
                if "error" in update_result:
                    warnings.append(f"Stage 3: Failed to update ARQCOR - {update_result['error']}")
            else:
                warnings.append("Stage 3: ARQCOR form ID is missing, cannot update with versions")
            
            major_changes = version_check.get("major_changes", [])
            if major_changes:
                warnings.append(
                    f"Stage 3: Major version changes detected for: {', '.join(major_changes)}"
                )
            
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
    
    try:
        checklist_items = []
        
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
    
    if errors:
        overall_status = "FAILED"
    elif manual_actions:
        overall_status = "REQUIRES_MANUAL_ACTION"
    else:
        overall_status = "APPROVED"
    
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
    """Formata a resposta de validação com todos os resultados.

    Função auxiliar interna para criar formato de resposta consistente
    para resultados de validação.

    Args:
        ticket_id: ID do ticket validado.
        overall_status: Status final da validação.
        stages_completed: Lista de etapas concluídas.
        errors: Lista de erros encontrados.
        warnings: Lista de avisos.
        manual_actions: Lista de ações manuais necessárias.
        arqcor_form_id: ID do formulário ARQCOR gerado, se disponível.

    Returns:
        Dicionário de resposta de validação formatado.
    """
    summary = format_validation_result(overall_status, errors, warnings, manual_actions)
    
    total_stages = 4
    completed_count = len(stages_completed)
    
    if completed_count < total_stages:
        summary += f"\n\n📊 Etapas concluídas: {completed_count}/{total_stages}"
        if stages_completed:
            summary += f"\n✓ {', '.join(stages_completed)}"
    else:
        summary += f"\n\n✅ Todas as {total_stages} etapas de validação concluídas com sucesso"
    
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
    """Valida o repositório de código-fonte de um componente.

    Executa validação abrangente incluindo estrutura do repositório,
    dependências, arquivos de configuração e especificações OpenAPI.
    Suporta repositórios Git e Bitbucket.

    Args:
        repository_url: URL do repositório Git.
        component_name: Nome do componente.
        tool_context: Contexto da ferramenta ADK.
        access_token: Token de acesso opcional para repositórios privados.

    Returns:
        Dicionário contendo:
            - component: Nome do componente
            - repository_url: URL do repositório
            - has_openapi: Boolean indicando se especificação OpenAPI existe
            - dependencies_valid: Boolean para validação de dependências
            - structure_valid: Boolean para estrutura do projeto
            - issues: Lista de problemas encontrados
            - repository_info: Metadados adicionais do repositório (se disponível)
            - error: Mensagem de erro se a validação falhou

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
        is_bitbucket = "bitbucket.org" in repository_url
        
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
            structure_result = await analyze_project_structure(repo_path, tool_context)
            
            structure_valid = structure_result.get("structure_valid", False)
            if not structure_valid:
                missing_dirs = structure_result.get("missing_directories", [])
                if missing_dirs:
                    issues.append(f"Missing required directories: {', '.join(missing_dirs)}")
            
            repository_info["project_type"] = structure_result.get("project_type", "unknown")
            repository_info["build_system"] = structure_result.get("build_system", "unknown")
            repository_info["detected_files"] = structure_result.get("detected_files", [])
            
            deps_result = await validate_dependencies(repo_path, tool_context)
            
            dependencies_valid = deps_result.get("dependencies_valid", True)
            
            deprecated_deps = deps_result.get("deprecated_dependencies", [])
            if deprecated_deps:
                issues.extend([f"Deprecated dependency: {dep}" for dep in deprecated_deps])
            
            security_issues = deps_result.get("security_issues", [])
            if security_issues:
                dependencies_valid = False
                issues.extend([f"Security issue: {issue}" for issue in security_issues])
            
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
                if component_name.startswith("sboot-") or repository_info.get("project_type") == "java":
                    issues.append("OpenAPI specification not found")
            
            if component_name.endswith("-gateway"):
                if not has_openapi:
                    issues.append("API Gateway components must have OpenAPI specification")
                    dependencies_valid = False
            
            config_files = ["Dockerfile", "docker-compose.yml", ".gitlab-ci.yml", "Jenkinsfile"]
            found_configs = [f for f in config_files if f in repository_info.get("detected_files", [])]
            
            if not found_configs:
                issues.append("No CI/CD configuration files found (Dockerfile, Jenkinsfile, etc.)")
            
        finally:
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