"""HTTP client utilities with retry and error handling.

Provides configured HTTP clients for each external service with
appropriate authentication, timeouts, and retry strategies.
"""

import base64
from datetime import datetime, timedelta
import os
from typing import Optional, Dict, Any
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from ..config.settings import get_settings


class BaseHTTPClient:
    """Base HTTP client with common retry and error handling logic.

    Provides a foundation for service-specific HTTP clients with
    built-in retry logic and proper error handling.
    """

    def __init__(self, base_url: str, timeout: int = 30, headers: Optional[Dict[str, str]] = None):
        """Initializes the HTTP client.

        Args:
            base_url: Base URL for the service.
            timeout: Request timeout in seconds.
            headers: Default headers for all requests.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = headers or {}
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers=self.headers,
            follow_redirects=True
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(httpx.HTTPError)
    )
    async def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Makes an HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint path.
            **kwargs: Additional arguments for httpx request.

        Returns:
            HTTP response object.

        Raises:
            httpx.HTTPError: If request fails after retries.
        """
        response = await self.client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return response

    async def get(self, endpoint: str, **kwargs) -> httpx.Response:
        """Makes a GET request.

        Args:
            endpoint: API endpoint path.
            **kwargs: Additional arguments for the request.

        Returns:
            HTTP response object.
        """
        return await self.request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs) -> httpx.Response:
        """Makes a POST request.

        Args:
            endpoint: API endpoint path.
            **kwargs: Additional arguments for the request.

        Returns:
            HTTP response object.
        """
        return await self.request("POST", endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs) -> httpx.Response:
        """Makes a PUT request.

        Args:
            endpoint: API endpoint path.
            **kwargs: Additional arguments for the request.

        Returns:
            HTTP response object.
        """
        return await self.request("PUT", endpoint, **kwargs)

    async def patch(self, endpoint: str, **kwargs) -> httpx.Response:
        """Makes a PATCH request.

        Args:
            endpoint: API endpoint path.
            **kwargs: Additional arguments for the request.

        Returns:
            HTTP response object.
        """
        return await self.request("PATCH", endpoint, **kwargs)


class JiraClient(BaseHTTPClient):
    """HTTP client configured for Jira API access.

    Handles Jira-specific authentication and request formatting.
    """

    def __init__(self):
        """Initializes Jira client with settings from configuration."""
        settings = get_settings().jira
        
        headers = {
            "Authorization": f"Bearer {settings.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        super().__init__(
            base_url=f"{settings.base_url}",
            timeout=settings.timeout,
            headers=headers
        )


class VTClient(BaseHTTPClient):
    """HTTP client configured for VT/BlizzDesign API access.

    Handles VT-specific authentication using Bearer token.
    """

    def __init__(self):
        """Initializes VT client with settings from configuration."""
        settings = get_settings().vt
        
        headers = {
            "Authorization": f"Bearer {settings.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        super().__init__(
            base_url=settings.base_url,
            timeout=settings.timeout,
            headers=headers
        )


class PortalTechClient(BaseHTTPClient):
    """HTTP client configured for Component (Portal Tech) access.

    Handles both API access (with token) and web scraping fallback.
    """

    def __init__(self):
        """Initializes Component (Portal Tech) client with settings from configuration."""
        settings = get_settings().portal_tech
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
        }
        
        # Add auth token if configured
        if settings.auth_token:
            headers["Authorization"] = f"Bearer {settings.auth_token}"
        
        super().__init__(
            base_url=settings.base_url,
            timeout=settings.timeout,
            headers=headers
        )


class ARQCORClient(BaseHTTPClient):
    """HTTP client configured for ARQCOR API access.

    Handles OAuth2 authentication flow and token management.
    """

    def __init__(self):
        """Initializes ARQCOR client with settings from configuration."""
        settings = get_settings().arqcor
        
        super().__init__(
            base_url=settings.base_url,
            timeout=settings.timeout
        )
        
        self.client_id = settings.client_id
        self.client_secret = settings.client_secret
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    async def _ensure_authenticated(self) -> None:
        """Ensures valid OAuth2 token is available.

        Refreshes token if expired or not present.
        """
        if self._access_token and self._token_expires_at:
            if datetime.utcnow() < self._token_expires_at:
                return
        
        await self._authenticate()

    async def _authenticate(self) -> None:
        """Authenticates with ARQCOR using OAuth2 client credentials."""
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "forms.write forms.read"
        }
        
        response = await self.client.post(
            "/oauth/token",
            data=auth_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        
        token_data = response.json()
        self._access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in", 3600)
        
        # Set expiration with 60 second buffer
        self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)

    async def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Makes an authenticated request to ARQCOR.

        Args:
            method: HTTP method.
            endpoint: API endpoint.
            **kwargs: Additional request arguments.

        Returns:
            HTTP response object.
        """
        await self._ensure_authenticated()
        
        # Add auth header
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = f"Bearer {self._access_token}"
        
        return await super().request(method, endpoint, **kwargs)


# Singleton instances
_clients: Dict[str, Any] = {}


async def get_jira_client() -> JiraClient:
    """Gets or creates Jira client singleton.

    Returns:
        Configured JiraClient instance.
    """
    if "jira" not in _clients:
        _clients["jira"] = JiraClient()
    return _clients["jira"]


async def get_vt_client() -> VTClient:
    """Gets or creates VT client singleton.

    Returns:
        Configured VTClient instance.
    """
    if "vt" not in _clients:
        _clients["vt"] = VTClient()
    return _clients["vt"]


async def get_portal_tech_client() -> PortalTechClient:
    """Gets or creates Component (Portal Tech) client singleton.

    Returns:
        Configured PortalTechClient instance.
    """
    if "portal_tech" not in _clients:
        _clients["portal_tech"] = PortalTechClient()
    return _clients["portal_tech"]


async def get_arqcor_client() -> ARQCORClient:
    """Gets or creates ARQCOR client singleton.

    Returns:
        Configured ARQCORClient instance.
    """
    if "arqcor" not in _clients:
        _clients["arqcor"] = ARQCORClient()
    return _clients["arqcor"]