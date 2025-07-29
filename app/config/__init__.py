"""Configuration module for Feito/Conferido ADK Agent.

This module provides a clean interface for accessing all application 
configuration settings through a singleton pattern with proper type inference.
"""

from .settings import (
    Settings,
    JiraSettings,
    VTSettings, 
    PortalTechSettings,
    ARQCORSettings,
    get_settings,
    reset_settings
)


__all__ = [
    # Main settings interface
    "get_settings",
    "reset_settings",
    
    # Settings classes for type hints
    "Settings",
    "JiraSettings", 
    "VTSettings",
    "PortalTechSettings",
    "ARQCORSettings",
]
