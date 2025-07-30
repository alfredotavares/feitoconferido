"""HTTP client utilities with retry and error handling.

Provides configured HTTP clients for each external service with
appropriate authentication, timeouts and retry strategies.
"""

from datetime import datetime, timedelta, timezone
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
    """Base HTTP client with common retry logic and error handling.

    Provides a foundation for service-specific HTTP clients with
    integrated retry logic and proper error handling.
    """

    def __init__(self, base_url: str, timeout: int = 30, headers: Optional[Dict[str, str]] = None):
        """Initializes the HTTP client.

        Args:
            base_url: Base URL for the service.
            timeout: Request timeout in seconds.
            headers: Default headers for all requests.

        Example:
            >>> client = BaseHTTPClient("https://api.example.com", timeout=60)
            >>> # Client configured with 60 seconds timeout
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
        """Async context manager entry.
        
        Returns:
            Client instance itself for use in async with context.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit.
        
        Ensures HTTP client is properly closed even in case of exceptions.
        
        Args:
            exc_type: Exception type (if any).
            exc_val: Exception value (if any).
            exc_tb: Exception traceback (if any).
        """
        await self.client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(httpx.HTTPError)
    )
    async def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Makes an HTTP request with retry logic.

        Implements exponential backoff retry strategy with up to 3 attempts
        for requests that fail with HTTPError.

        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint path.
            **kwargs: Additional arguments for httpx request.

        Returns:
            HTTP response object.

        Raises:
            httpx.HTTPError: If request fails after all retry attempts.

        Example:
            >>> response = await client.request("GET", "/users/1")
            >>> print(response.status_code)
            200
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

        Example:
            >>> response = await client.get("/users", params={"page": 1})
        """
        return await self.request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs) -> httpx.Response:
        """Makes a POST request.

        Args:
            endpoint: API endpoint path.
            **kwargs: Additional arguments for the request.

        Returns:
            HTTP response object.

        Example:
            >>> response = await client.post("/users", json={"name": "John"})
        """
        return await self.request("POST", endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs) -> httpx.Response:
        """Makes a PUT request.

        Args:
            endpoint: API endpoint path.
            **kwargs: Additional arguments for the request.

        Returns:
            HTTP response object.

        Example:
            >>> response = await client.put("/users/1", json={"name": "John Silva"})
        """
        return await self.request("PUT", endpoint, **kwargs)

    async def patch(self, endpoint: str, **kwargs) -> httpx.Response:
        """Makes a PATCH request.

        Args:
            endpoint: API endpoint path.
            **kwargs: Additional arguments for the request.

        Returns:
            HTTP response object.

        Example:
            >>> response = await client.patch("/users/1", json={"email": "new@email.com"})
        """
        return await self.request("PATCH", endpoint, **kwargs)


class JiraClient(BaseHTTPClient):
    """HTTP client configured for Jira API access.

    Handles Jira-specific authentication and request formatting.
    Uses Bearer token for authentication.
    """

    def __init__(self):
        """Initializes Jira client with configuration file settings.
        
        Obtains Jira settings (base URL, access token, timeout)
        from configuration system and sets up appropriate headers.
        
        Raises:
            ConfigurationError: If Jira configuration is not valid.
        """
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
    Used to query architecture and component data.
    """

    def __init__(self):
        """Initializes VT client with configuration file settings.
        
        Configures authentication via Bearer token and appropriate
        headers for VT/BlizzDesign API communication.
        
        Raises:
            ConfigurationError: If VT configuration is not valid.
        """
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

    Handles both API access (with token) and fallback via web scraping.
    Used to obtain component information and versions.
    """

    def __init__(self):
        """Initializes Component (Portal Tech) client with configuration file settings.
        
        Configures headers to simulate web browser (useful for web scraping)
        and adds authentication token if available in settings.
        
        Raises:
            ConfigurationError: If Portal Tech configuration is not valid.
        """
        settings = get_settings().portal_tech
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
        }
        
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
    Implements automatic token renewal when expired.
    """

    def __init__(self):
        """Initializes ARQCOR client with configuration file settings.
        
        Configures OAuth2 credentials and initializes token control
        variables for automatic authentication management.
        
        Raises:
            ConfigurationError: If ARQCOR configuration is not valid.
        """
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
        """Ensures a valid OAuth2 token is available.

        Checks if current token is still valid and renews
        if expired or not present.
        
        Raises:
            httpx.HTTPError: If token renewal fails.
        """
        if self._access_token and self._token_expires_at:
            if datetime.now(timezone.utc) < self._token_expires_at:
                return
        
        await self._authenticate()

    async def _authenticate(self) -> None:
        """Authenticates with ARQCOR using OAuth2 client credentials.
        
        Implements OAuth2 Client Credentials Grant flow to obtain
        a valid access token for subsequent requests.
        
        Raises:
            httpx.HTTPError: If authentication fails.
            ValueError: If response doesn't contain valid token.
        """
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
        
        self._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 60)

    async def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Makes an authenticated request to ARQCOR.

        Ensures request has a valid token in authorization header,
        automatically renewing if necessary.

        Args:
            method: HTTP method.
            endpoint: API endpoint.
            **kwargs: Additional request arguments.

        Returns:
            HTTP response object.

        Raises:
            httpx.HTTPError: If authentication or request fails.

        Example:
            >>> response = await arqcor_client.request("GET", "/forms")
            >>> # Token is managed automatically
        """
        await self._ensure_authenticated()
        
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = f"Bearer {self._access_token}"
        
        return await super().request(method, endpoint, **kwargs)


_clients: Dict[str, Any] = {}


async def get_jira_client() -> JiraClient:
    """Gets or creates singleton instance of Jira client.

    Implements singleton pattern to reuse the same Jira client
    instance throughout the application, avoiding multiple connections.

    Returns:
        Configured JiraClient instance.

    Example:
        >>> jira = await get_jira_client()
        >>> response = await jira.get("/rest/api/2/issue/PROJECT-123")
    """
    if "jira" not in _clients:
        _clients["jira"] = JiraClient()
    return _clients["jira"]


async def get_vt_client() -> VTClient:
    """Gets or creates singleton instance of VT client.

    Implements singleton pattern to reuse the same VT client
    instance throughout the application.

    Returns:
        Configured VTClient instance.

    Example:
        >>> vt = await get_vt_client()
        >>> response = await vt.get("/api/architecture/components")
    """
    if "vt" not in _clients:
        _clients["vt"] = VTClient()
    return _clients["vt"]


async def get_portal_tech_client() -> PortalTechClient:
    """Gets or creates singleton instance of Component (Portal Tech) client.

    Implements singleton pattern to reuse the same Portal Tech client
    instance throughout the application.

    Returns:
        Configured PortalTechClient instance.

    Example:
        >>> portal = await get_portal_tech_client()
        >>> response = await portal.get("/components/user-service")
    """
    if "portal_tech" not in _clients:
        _clients["portal_tech"] = PortalTechClient()
    return _clients["portal_tech"]


async def get_arqcor_client() -> ARQCORClient:
    """Gets or creates singleton instance of ARQCOR client.

    Implements singleton pattern to reuse the same ARQCOR client
    instance throughout the application, maintaining OAuth2 token
    in memory for efficiency.

    Returns:
        Configured ARQCORClient instance.

    Example:
        >>> arqcor = await get_arqcor_client()
        >>> response = await arqcor.get("/api/forms/validation")
    """
    if "arqcor" not in _clients:
        _clients["arqcor"] = ARQCORClient()
    return _clients["arqcor"]
