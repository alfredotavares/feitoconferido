"""Authentication utilities for external service integrations.

Provides authentication helpers for OAuth2, API tokens, and other
authentication mechanisms used by the Feito/Conferido agent.
"""

import asyncio
import base64
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import httpx

from ..config.settings import get_settings


class TokenCache:
    """Simple in-memory token cache for OAuth2 tokens.

    Stores tokens with expiration times to avoid unnecessary
    authentication requests.
    """

    def __init__(self):
        """Initializes the token cache."""
        self._cache: Dict[str, Tuple[str, datetime]] = {}

    def get(self, key: str) -> Optional[str]:
        """Retrieves a token from cache if not expired.

        Args:
            key: Cache key for the token.

        Returns:
            Token string if valid, None if expired or not found.
        """
        if key not in self._cache:
            return None
        
        token, expires_at = self._cache[key]
        if datetime.utcnow() >= expires_at:
            del self._cache[key]
            return None
        
        return token

    def set(self, key: str, token: str, expires_in: int) -> None:
        """Stores a token in cache with expiration.

        Args:
            key: Cache key for the token.
            token: Token string to store.
            expires_in: Token lifetime in seconds.
        """
        # Store with 60 second buffer before expiration
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)
        self._cache[key] = (token, expires_at)

    def clear(self) -> None:
        """Clears all cached tokens."""
        self._cache.clear()


# Global token cache instance
_token_cache = TokenCache()


def get_basic_auth_header(username: str, password: str) -> str:
    """Creates a Basic Authentication header value.

    Args:
        username: Username for authentication.
        password: Password or API token.

    Returns:
        Basic auth header value.

    Example:
        >>> header = get_basic_auth_header("user@example.com", "api_token")
        >>> print(header)
        "Basic dXNlckBleGFtcGxlLmNvbTphcGlfdG9rZW4="
    """
    auth_string = f"{username}:{password}"
    auth_bytes = auth_string.encode("utf-8")
    auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")
    return f"Basic {auth_b64}"


def get_bearer_auth_header(token: str) -> str:
    """Creates a Bearer token authentication header value.

    Args:
        token: Bearer token for authentication.

    Returns:
        Bearer auth header value.

    Example:
        >>> header = get_bearer_auth_header("my_api_token")
        >>> print(header)
        "Bearer my_api_token"
    """
    return f"Bearer {token}"


async def get_oauth2_token(
    token_url: str,
    client_id: str,
    client_secret: str,
    scope: Optional[str] = None,
    additional_params: Optional[Dict[str, str]] = None
) -> Tuple[str, int]:
    """Obtains an OAuth2 access token using client credentials flow.

    Args:
        token_url: OAuth2 token endpoint URL.
        client_id: OAuth2 client ID.
        client_secret: OAuth2 client secret.
        scope: Optional scope for the token request.
        additional_params: Optional additional parameters for the request.

    Returns:
        Tuple of (access_token, expires_in_seconds).

    Raises:
        httpx.HTTPError: If token request fails.

    Example:
        >>> token, expires_in = await get_oauth2_token(
        ...     "https://auth.example.com/oauth/token",
        ...     "client_id",
        ...     "client_secret",
        ...     scope="read write"
        ... )
    """
    # Check cache first
    cache_key = f"{token_url}:{client_id}"
    cached_token = _token_cache.get(cache_key)
    if cached_token:
        return cached_token, 3600  # Return with default expiry
    
    # Prepare token request
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    if scope:
        data["scope"] = scope
    
    if additional_params:
        data.update(additional_params)
    
    # Make token request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            token_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)
        
        # Cache the token
        _token_cache.set(cache_key, access_token, expires_in)
        
        return access_token, expires_in


def generate_api_signature(
    secret_key: str,
    method: str,
    url: str,
    timestamp: Optional[int] = None,
    body: Optional[str] = None
) -> str:
    """Generates HMAC signature for API request authentication.

    Some APIs require request signing for authentication.

    Args:
        secret_key: Secret key for HMAC signing.
        method: HTTP method (GET, POST, etc.).
        url: Request URL.
        timestamp: Unix timestamp (defaults to current time).
        body: Request body for POST/PUT requests.

    Returns:
        Base64 encoded HMAC signature.

    Example:
        >>> signature = generate_api_signature(
        ...     "secret_key",
        ...     "POST",
        ...     "https://api.example.com/v1/data",
        ...     body='{"key": "value"}'
        ... )
    """
    if timestamp is None:
        timestamp = int(time.time())
    
    # Build string to sign
    parts = [
        method.upper(),
        url,
        str(timestamp)
    ]
    
    if body:
        parts.append(body)
    
    string_to_sign = "\n".join(parts)
    
    # Generate HMAC signature
    signature = hmac.new(
        secret_key.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha256
    ).digest()
    
    return base64.b64encode(signature).decode("utf-8")


async def refresh_token_if_needed(
    service_name: str,
    token_getter,
    force_refresh: bool = False
) -> str:
    """Refreshes authentication token if needed.

    Generic helper to manage token refresh for any service.

    Args:
        service_name: Name of the service (for caching).
        token_getter: Async function that returns a new token.
        force_refresh: Force token refresh even if cached.

    Returns:
        Valid authentication token.

    Example:
        >>> token = await refresh_token_if_needed(
        ...     "arqcor",
        ...     lambda: get_oauth2_token(url, client_id, client_secret)
        ... )
    """
    cache_key = f"token:{service_name}"
    
    if not force_refresh:
        cached_token = _token_cache.get(cache_key)
        if cached_token:
            return cached_token
    
    # Get new token
    if asyncio.iscoroutinefunction(token_getter):
        token_data = await token_getter()
    else:
        token_data = token_getter()
    
    # Handle different return types
    if isinstance(token_data, tuple):
        token, expires_in = token_data
        _token_cache.set(cache_key, token, expires_in)
        return token
    else:
        # Assume token with default expiry
        _token_cache.set(cache_key, token_data, 3600)
        return token_data


def clear_auth_cache() -> None:
    """Clears all cached authentication tokens.

    Useful for forcing re-authentication or during logout.
    """
    _token_cache.clear()


# Service-specific authentication helpers

def get_jira_auth_headers() -> Dict[str, str]:
    """Gets authentication headers for Jira API.

    Returns:
        Dictionary with Authorization header for Jira.
    """
    settings = get_settings().jira
    auth_header = get_basic_auth_header(settings.username, settings.api_token)
    return {"Authorization": auth_header}


def get_vt_auth_headers() -> Dict[str, str]:
    """Gets authentication headers for VT API.

    Returns:
        Dictionary with Authorization header for VT.
    """
    settings = get_settings().vt
    auth_header = get_bearer_auth_header(settings.api_key)
    return {"Authorization": auth_header}


def get_portal_tech_auth_headers() -> Dict[str, str]:
    """Gets authentication headers for Portal Tech API.

    Returns:
        Dictionary with Authorization header if token is configured.
    """
    settings = get_settings().portal_tech
    if settings.auth_token:
        return {"Authorization": get_bearer_auth_header(settings.auth_token)}
    return {}


async def get_arqcor_auth_headers() -> Dict[str, str]:
    """Gets authentication headers for ARQCOR API.

    Handles OAuth2 token acquisition and caching.

    Returns:
        Dictionary with Authorization header for ARQCOR.
    """
    settings = get_settings().arqcor
    
    async def get_token():
        return await get_oauth2_token(
            f"{settings.base_url}/oauth/token",
            settings.client_id,
            settings.client_secret,
            scope="forms.write forms.read"
        )
    
    token = await refresh_token_if_needed("arqcor", get_token)
    return {"Authorization": get_bearer_auth_header(token)}