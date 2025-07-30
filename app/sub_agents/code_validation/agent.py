"""Code Validation Subagent for repository and contract validation.

This subagent validates repository structure, dependencies, and OpenAPI
contracts, identifying manual actions needed for API Gateway components.
"""

import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from typing import Dict, List, Any, Optional

from . import prompt

USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"

if USE_MOCK:
    from ...tools.mock.tools_mocked import (
        get_repository_info,
        list_repository_tags,
        clone_repository,
        analyze_project_structure,
        validate_dependencies,
        find_openapi_spec,
        cleanup_repository
    )
else:
    from ...tools.integrations.git import (
        clone_repository,
        analyze_project_structure,
        validate_dependencies,
        find_openapi_spec,
        cleanup_repository
    )

from ...tools.integrations.bitbucket import (
        get_repository_info,
        list_repository_tags
    )


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
            tool_context,
            repository_info.get("default_branch", "main")
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


async def validate_code_and_contracts(
    components: List[str],
    repository_urls: Optional[Dict[str, str]],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Execute code and contract validation stage.
    
    Validates repository structure, dependencies, and API contracts
    for all components, with special handling for API Gateway components.
    
    Args:
        components: List of component names to validate.
        repository_urls: Optional mapping of component names to repository URLs.
        tool_context: ADK tool context for state management.
        
    Returns:
        Dictionary containing code validation results and required actions.
    """
    try:
        validation_results = []
        checklist_items = []
        manual_actions = []
        warnings = []
        
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
        
        # Validate each component's repository
        for component in components:
            repo_url = repository_urls.get(component) if repository_urls else None
            
            if repo_url:
                result = await validate_code_repository(
                    repo_url,
                    component,
                    tool_context
                )
                
                validation_results.append({
                    "component": component,
                    "repository": repo_url,
                    "validation": result
                })
                
                # Process validation results
                if not result.get("structure_valid", False):
                    warnings.append(f"{component}: Invalid repository structure")
                
                if not result.get("dependencies_valid", False):
                    warnings.append(f"{component}: Dependency validation failed")
                
                if not result.get("has_openapi", False) and component.endswith("-api"):
                    warnings.append(f"{component}: Missing OpenAPI specification")
                
                issues = result.get("issues", [])
                if issues:
                    for issue in issues:
                        warnings.append(f"{component}: {issue}")
            else:
                manual_actions.append(f"Manual code validation required for {component} (no repository URL)")
        
        # Build validation checklist
        checklist_items.extend([
            {
                "item": "Dependencies validation",
                "result": "PASS" if all(r["validation"].get("dependencies_valid", False) 
                                      for r in validation_results) else "FAIL",
                "notes": "All dependencies checked against approved list"
            },
            {
                "item": "Repository structure",
                "result": "PASS" if all(r["validation"].get("structure_valid", False) 
                                      for r in validation_results) else "FAIL",
                "notes": "Standard project structure verified"
            },
            {
                "item": "OpenAPI contracts",
                "result": "PASS" if all(r["validation"].get("has_openapi", True) 
                                      for r in validation_results 
                                      if r["component"].endswith("-api")) else "WARN",
                "notes": "API contracts validated where applicable"
            }
        ])
        
        # Determine overall status
        has_failures = any(item["result"] == "FAIL" for item in checklist_items)
        has_warnings = len(warnings) > 0 or any(item["result"] == "WARN" for item in checklist_items)
        
        status = "FAILED" if has_failures else ("WARNING" if has_warnings else "SUCCESS")
        
        return {
            "status": status,
            "components_validated": len(validation_results),
            "validation_results": validation_results,
            "checklist_items": checklist_items,
            "warnings": warnings,
            "manual_actions": manual_actions,
            "requires_manual": len(manual_actions) > 0
        }
        
    except Exception as e:
        return {
            "status": "FAILED",
            "error": f"Unexpected error during code validation: {str(e)}",
            "components_validated": 0,
            "requires_manual": True
        }


# Code Validation Subagent Configuration  
code_validation_agent = Agent(
    name="code_validation_subagent",
    model="gemini-2.5-flash",
    description="Subagente especializado para validação de código-fonte e contratos de API.",
    instruction=prompt.CODE_VALIDATION_PROMPT,
    tools=[validate_code_and_contracts]
)
