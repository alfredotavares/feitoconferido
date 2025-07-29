"""Feito/Conferido ADK tools package.

This package exports all tools used by the Feito/Conferido agent
for validating architectural adherence.
"""

# Jira tools
from .integrations.jira import (
    get_jira_ticket,
    get_ticket_components,
    validate_pdi_components,
    get_arqcor_ticket,
    update_ticket_comment
)

# VT/BlizzDesign tools
from .integrations.blizzdesign import (
    get_technical_vision_by_ticket,
    validate_components_in_vt,
    get_blizzdesign_export,
    parse_blizzdesign_data,
    get_openapi_contract,
    load_local_architecture_data,
    parse_component_list_from_text,
    validate_components_vs_architecture,
    search_component_by_name,
    list_all_components_by_status
)

# Component (Portal Tech) tools
from .integrations.portal_tech import (
    get_production_version,
    compare_component_versions,
    check_multiple_component_versions,
    get_component_details
)

# ARQCOR tools
from .integrations.arqcor import (
    create_arqcor_form,
    update_arqcor_form_with_versions,
    submit_arqcor_form,
    get_arqcor_form_status,
    add_validation_checklist_to_form
)

# Main validation tools
from .validation_tools import (
    validate_feito_conferido,
    validate_code_repository
)

# Git tools
from .integrations.git import (
    clone_repository,
    analyze_project_structure,
    validate_dependencies,
    find_openapi_spec,
    cleanup_repository,
    detect_project_type,
    get_required_directories
)

# Bitbucket tools
from .integrations.bitbucket import (
    get_repository_info,
    list_repository_tags,
    get_file_content,
    list_pull_requests,
    check_branch_protection
)

__all__ = [
    # Jira tools
    "get_jira_ticket",
    "get_ticket_components",
    "validate_pdi_components",
    "get_arqcor_ticket",
    "update_ticket_comment",
    
    # VT tools
    "get_technical_vision_by_ticket",
    "validate_components_in_vt",
    "get_blizzdesign_export",
    "parse_blizzdesign_data",
    "get_openapi_contract",
    "load_local_architecture_data",
    "parse_component_list_from_text",
    "validate_components_vs_architecture",
    "search_component_by_name",
    "list_all_components_by_status",
    
    # Component (Portal Tech) tools
    "get_production_version",
    "compare_component_versions",
    "check_multiple_component_versions",
    "get_component_details",
    
    # ARQCOR tools
    "create_arqcor_form",
    "update_arqcor_form_with_versions",
    "submit_arqcor_form",
    "get_arqcor_form_status",
    "add_validation_checklist_to_form",
    
    # Main validation tools
    "validate_feito_conferido",
    "validate_code_repository",
    
    # Git tools
    "clone_repository",
    "analyze_project_structure",
    "validate_dependencies",
    "find_openapi_spec",
    "cleanup_repository",
    "detect_project_type",
    "get_required_directories",
    
    # Bitbucket tools
    "get_repository_info",
    "list_repository_tags",
    "get_file_content",
    "list_pull_requests",
    "check_branch_protection"
]
