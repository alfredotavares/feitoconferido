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

    base_url: str = Field(..., description="Jira instance base URL")
    username: str = Field(..., description="Jira username for authentication")
    api_token: str = Field(..., description="Jira API token")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    
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

    base_url: str = Field(..., description="VT API base URL")
    api_key: str = Field(..., description="API key for authentication")
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
    """Portal Tech configuration for version checking.

    Manages connection to Portal Tech for production version queries.
    """

    base_url: str = Field(
        default="https://portaltech.bvnet.bv",
        description="Portal Tech base URL"
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

    base_url: str = Field(..., description="ARQCOR API base URL")
    client_id: str = Field(..., description="OAuth2 client ID")
    client_secret: str = Field(..., description="OAuth2 client secret")
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
    
    # Sub-settings
    jira: JiraSettings = Field(default_factory=JiraSettings) # type: ignore
    vt: VTSettings = Field(default_factory=VTSettings) # type: ignore
    portal_tech: PortalTechSettings = Field(default_factory=PortalTechSettings) # type: ignore
    arqcor: ARQCORSettings = Field(default_factory=ARQCORSettings) # type: ignore

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


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Gets or creates the settings singleton.

    Returns:
        Settings instance with all configuration loaded.

    Example:
        >>> settings = get_settings()
        >>> print(settings.jira.base_url)
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings