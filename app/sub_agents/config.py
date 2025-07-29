"""Configuration module for FEITO CONFERIDO subagents.

Defines model selections, rate limits, and operational parameters
for each specialized subagent in the validation workflow.
"""

from typing import Dict, Any


class SubagentConfig:
    """Configuration settings for all subagents in the system.
    
    This class centralizes configuration for model selection,
    performance tuning, and operational limits for each subagent.
    """
    
    # Model configurations optimized for each task
    MODELS = {
        "component_validation": "claude-3-5-sonnet-20241022",  # Complex VT analysis
        "arqcor_form": "gemini-2.0-flash",                    # Fast form operations  
        "version_check": "gemini-2.0-flash",                   # Quick comparisons
        "code_validation": "claude-3-5-sonnet-20241022"       # Code analysis
    }
    
    # Rate limiting per subagent (requests per minute)
    RATE_LIMITS = {
        "component_validation": 30,
        "arqcor_form": 60,
        "version_check": 60,
        "code_validation": 20
    }
    
    # Timeout settings (seconds)
    TIMEOUTS = {
        "component_validation": 30,
        "arqcor_form": 15,
        "version_check": 20,
        "code_validation": 45
    }
    
    # Retry configurations
    RETRY_SETTINGS = {
        "max_retries": 3,
        "retry_delay": 2,  # seconds
        "exponential_backoff": True
    }
    
    # Cache settings for subagent results
    CACHE_CONFIG = {
        "enable_caching": True,
        "cache_ttl": 300,  # 5 minutes
        "cache_size": 1000  # max entries
    }
    
    @classmethod
    def get_subagent_config(cls, subagent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific subagent.
        
        Args:
            subagent_name: Name of the subagent.
            
        Returns:
            Dictionary containing subagent-specific configuration.
        """
        return {
            "model": cls.MODELS.get(subagent_name, "gemini-2.0-flash"),
            "rate_limit": cls.RATE_LIMITS.get(subagent_name, 30),
            "timeout": cls.TIMEOUTS.get(subagent_name, 30),
            "retry": cls.RETRY_SETTINGS,
            "cache": cls.CACHE_CONFIG
        }
    
    @classmethod
    def get_orchestrator_config(cls) -> Dict[str, Any]:
        """Get configuration for the main orchestrator.
        
        Returns:
            Dictionary containing orchestrator configuration.
        """
        return {
            "model": "gemini-2.0-flash",  # Fast coordination
            "max_concurrent_stages": 1,    # Sequential processing
            "stage_timeout": 120,          # 2 minutes per stage
            "enable_partial_results": True,
            "audit_logging": True
        }


# Subagent capabilities and constraints
SUBAGENT_CAPABILITIES = {
    "component_validation": {
        "capabilities": [
            "jira_ticket_analysis",
            "vt_compliance_check",
            "pdi_status_validation",
            "component_extraction"
        ],
        "constraints": [
            "requires_jira_access",
            "requires_vt_access",
            "no_code_execution"
        ]
    },
    "arqcor_form": {
        "capabilities": [
            "form_creation",
            "form_updates",
            "checklist_management",
            "audit_trail"
        ],
        "constraints": [
            "requires_arqcor_api",
            "form_template_dependency",
            "no_form_deletion"
        ]
    },
    "version_check": {
        "capabilities": [
            "version_comparison",
            "breaking_change_detection",
            "dependency_analysis",
            "production_baseline"
        ],
        "constraints": [
            "requires_portal_tech_api",
            "semver_compliance",
            "no_version_modification"
        ]
    },
    "code_validation": {
        "capabilities": [
            "repository_analysis",
            "dependency_validation",
            "api_contract_check",
            "security_scanning"
        ],
        "constraints": [
            "read_only_access",
            "no_code_execution",
            "requires_git_access"
        ]
    }
}


# Integration endpoints for each subagent
INTEGRATION_ENDPOINTS = {
    "jira": {
        "base_url": "https://jira.company.com",
        "api_version": "v3",
        "auth_type": "oauth2"
    },
    "vt": {
        "base_url": "https://vt.company.com", 
        "api_version": "v1",
        "auth_type": "api_key"
    },
    "arqcor": {
        "base_url": "https://arqcor.company.com",
        "api_version": "v1", 
        "auth_type": "bearer"
    },
    "portal_tech": {
        "base_url": "https://portal-tech.company.com",
        "api_version": "v2",
        "auth_type": "oauth2"
    },
    "git": {
        "base_url": "https://github.company.com",
        "api_version": "v3",
        "auth_type": "token"
    }
}
