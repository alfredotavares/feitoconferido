"""Configuration settings for Feito/Conferido ADK Agent.

This module manages all configuration settings using pydantic-settings,
loading values from environment variables with validation.
"""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class JiraSettings(BaseSettings):
    """Jira API configuration settings.

    Manages connection parameters and authentication for Jira integration.
    """

    base_url: str = Field(
        default="https://jira.bvnet.bv",
        description="Jira instance base URL"
    )
    timeout: int = Field(default=30, description="Request timeout in seconds")
    access_token: str = Field(
        default="",
        description="Jira API access token"
    )

    # Custom fields mapping
    components_field: str = Field(default="customfield_12803", description="Components field ID")
    description_field: str = Field(default="customfield_14810", description="PDI description field")
    arqcor_field: str = Field(default="customfield_13333", description="ARQCOR registration field")
    jt_field: str = Field(default="customfield_16830", description="JT field ID")

    model_config = SettingsConfigDict(env_prefix="JIRA_")

    @field_validator("base_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensures URL doesn't end with slash.

        Args:
            v: URL to validate.

        Returns:
            Cleaned URL without trailing slash.
        """
        return v.rstrip("/") if v else v


class VTSettings(BaseSettings):
    """Technical Vision (VT) and BlizzDesign configuration.

    Manages connection to VT API and BlizzDesign integration.
    """

    base_url: str = Field(
        default="https://tenant.bizzdesign.com",
        description="VT API base URL"
    )
    api_key: str = Field(default="", description="API key for authentication")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")

    model_config = SettingsConfigDict(env_prefix="VT_")

    @field_validator("base_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensures URL doesn't end with slash.

        Args:
            v: URL to validate.

        Returns:
            Cleaned URL without trailing slash.
        """
        return v.rstrip("/") if v else v


class PortalTechSettings(BaseSettings):
    """Component (Portal Tech) configuration for version checking.

    Manages connection to Component (Portal Tech) for production version queries.
    """

    base_url: str = Field(
        default="https://portaltech.bvnet.bv",
        description="Component (Portal Tech) base URL"
    )
    auth_token: Optional[str] = Field(
        default=None,
        description="Optional bearer token for API access"
    )
    timeout: int = Field(default=20, description="Request timeout in seconds")
    search_endpoint: str = Field(
        default="/dashboard",
        description="Search endpoint path"
    )

    model_config = SettingsConfigDict(env_prefix="PORTAL_TECH_")

    @field_validator("base_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensures URL doesn't end with slash.

        Args:
            v: URL to validate.

        Returns:
            Cleaned URL without trailing slash.
        """
        return v.rstrip("/")


class ARQCORSettings(BaseSettings):
    """ARQCOR system configuration.

    Manages OAuth2 authentication and form creation in ARQCOR.
    """

    base_url: str = Field(default="", description="ARQCOR API base URL")
    client_id: str = Field(default="", description="OAuth2 client ID")
    project_key: str = Field(default="ARQCOR", description="Project key for ARQCOR")
    client_secret: str = Field(default="", description="OAuth2 client secret")
    timeout: int = Field(default=45, description="Request timeout in seconds")
    form_template_id: str = Field(
        default="FEITO_CONFERIDO_V2",
        description="Form template identifier"
    )

    model_config = SettingsConfigDict(env_prefix="ARQCOR_")

    @field_validator("base_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensures URL doesn't end with slash.

        Args:
            v: URL to validate.

        Returns:
            Cleaned URL without trailing slash.
        """
        return v.rstrip("/") if v else v


class Settings(BaseSettings):
    """Main settings aggregator for the application.

    Combines all sub-settings and provides global configuration options.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Global settings
    app_name: str = Field(default="feito-conferido-agent", description="Application name")
    environment: str = Field(default="development", description="Environment name")
    log_level: str = Field(default="INFO", description="Logging level")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validates environment name.

        Args:
            v: Environment name.

        Returns:
            Validated environment name.

        Raises:
            ValueError: If environment is not valid.
        """
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of: {valid_envs}")
        return v.lower()

    @property
    def jira(self) -> JiraSettings:
        """Gets Jira configuration settings.
        
        Returns:
            JiraSettings instance with all Jira-related configuration.
            
        Note:
            Using property ensures proper type inference and lazy loading.
        """
        if not hasattr(self, '_jira'):
            self._jira = JiraSettings()
        return self._jira

    @property
    def vt(self) -> VTSettings:
        """Gets VT configuration settings.
        
        Returns:
            VTSettings instance with all VT-related configuration.
            
        Note:
            Using property ensures proper type inference and lazy loading.
        """
        if not hasattr(self, '_vt'):
            self._vt = VTSettings()
        return self._vt

    @property
    def portal_tech(self) -> PortalTechSettings:
        """Gets Portal Tech configuration settings.
        
        Returns:
            PortalTechSettings instance with all Portal Tech configuration.
            
        Note:
            Using property ensures proper type inference and lazy loading.
        """
        if not hasattr(self, '_portal_tech'):
            self._portal_tech = PortalTechSettings()
        return self._portal_tech

    @property
    def arqcor(self) -> ARQCORSettings:
        """Gets ARQCOR configuration settings.
        
        Returns:
            ARQCORSettings instance with all ARQCOR configuration.
            
        Note:
            Using property ensures proper type inference and lazy loading.
        """
        if not hasattr(self, '_arqcor'):
            self._arqcor = ARQCORSettings()
        return self._arqcor


# Singleton instance with explicit typing
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Gets or creates the settings singleton.

    Returns:
        Settings instance with all configuration loaded.
        
    Note:
        This function ensures proper type inference by maintaining
        a strongly typed singleton pattern. Each sub-setting is
        accessed via properties with explicit return types.

    Example:
        >>> settings = get_settings()
        >>> jira_settings = settings.jira  # Type: JiraSettings
        >>> print(jira_settings.base_url)  # Full IntelliSense support
        >>> vt_settings = settings.vt      # Type: VTSettings  
        >>> print(vt_settings.api_key)     # Full IntelliSense support
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Resets the settings singleton.
    
    Useful for testing and configuration reloading scenarios.
    Forces recreation of settings on next get_settings() call.
    
    Also clears any cached sub-settings to ensure fresh configuration
    loading on the next access.
    """
    global _settings
    if _settings is not None:
        # Clear cached sub-settings
        if hasattr(_settings, '_jira'):
            delattr(_settings, '_jira')
        if hasattr(_settings, '_vt'):
            delattr(_settings, '_vt')
        if hasattr(_settings, '_portal_tech'):
            delattr(_settings, '_portal_tech')
        if hasattr(_settings, '_arqcor'):
            delattr(_settings, '_arqcor')
    _settings = None
