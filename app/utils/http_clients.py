"""Utilitários de cliente HTTP com retry e tratamento de erros.

Fornece clientes HTTP configurados para cada serviço externo com
autenticação apropriada, timeouts e estratégias de retry.
"""

import base64
from datetime import datetime, timedelta, timezone
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
    """Cliente HTTP base com lógica comum de retry e tratamento de erros.

    Fornece uma base para clientes HTTP específicos de serviços com
    lógica de retry integrada e tratamento adequado de erros.
    """

    def __init__(self, base_url: str, timeout: int = 30, headers: Optional[Dict[str, str]] = None):
        """Inicializa o cliente HTTP.

        Args:
            base_url: URL base para o serviço.
            timeout: Timeout da requisição em segundos.
            headers: Cabeçalhos padrão para todas as requisições.

        Example:
            >>> client = BaseHTTPClient("https://api.example.com", timeout=60)
            >>> # Cliente configurado com timeout de 60 segundos
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
        """Entrada do gerenciador de contexto assíncrono.
        
        Returns:
            Instância do próprio cliente para uso em contexto async with.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Saída do gerenciador de contexto assíncrono.
        
        Garante que o cliente HTTP seja fechado adequadamente
        mesmo em caso de exceções.
        
        Args:
            exc_type: Tipo de exceção (se houver).
            exc_val: Valor da exceção (se houver).
            exc_tb: Traceback da exceção (se houver).
        """
        await self.client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(httpx.HTTPError)
    )
    async def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Faz uma requisição HTTP com lógica de retry.

        Implementa estratégia de retry exponencial com até 3 tentativas
        para requisições que falham com HTTPError.

        Args:
            method: Método HTTP (GET, POST, etc.).
            endpoint: Caminho do endpoint da API.
            **kwargs: Argumentos adicionais para requisição httpx.

        Returns:
            Objeto de resposta HTTP.

        Raises:
            httpx.HTTPError: Se a requisição falha após todas as tentativas.

        Example:
            >>> response = await client.request("GET", "/users/1")
            >>> print(response.status_code)
            200
        """
        response = await self.client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return response

    async def get(self, endpoint: str, **kwargs) -> httpx.Response:
        """Faz uma requisição GET.

        Args:
            endpoint: Caminho do endpoint da API.
            **kwargs: Argumentos adicionais para a requisição.

        Returns:
            Objeto de resposta HTTP.

        Example:
            >>> response = await client.get("/users", params={"page": 1})
        """
        return await self.request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs) -> httpx.Response:
        """Faz uma requisição POST.

        Args:
            endpoint: Caminho do endpoint da API.
            **kwargs: Argumentos adicionais para a requisição.

        Returns:
            Objeto de resposta HTTP.

        Example:
            >>> response = await client.post("/users", json={"name": "João"})
        """
        return await self.request("POST", endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs) -> httpx.Response:
        """Faz uma requisição PUT.

        Args:
            endpoint: Caminho do endpoint da API.
            **kwargs: Argumentos adicionais para a requisição.

        Returns:
            Objeto de resposta HTTP.

        Example:
            >>> response = await client.put("/users/1", json={"name": "João Silva"})
        """
        return await self.request("PUT", endpoint, **kwargs)

    async def patch(self, endpoint: str, **kwargs) -> httpx.Response:
        """Faz uma requisição PATCH.

        Args:
            endpoint: Caminho do endpoint da API.
            **kwargs: Argumentos adicionais para a requisição.

        Returns:
            Objeto de resposta HTTP.

        Example:
            >>> response = await client.patch("/users/1", json={"email": "novo@email.com"})
        """
        return await self.request("PATCH", endpoint, **kwargs)


class JiraClient(BaseHTTPClient):
    """Cliente HTTP configurado para acesso à API do Jira.

    Lida com autenticação específica do Jira e formatação de requisições.
    Utiliza Bearer token para autenticação.
    """

    def __init__(self):
        """Inicializa cliente do Jira com configurações do arquivo de configuração.
        
        Obtém as configurações do Jira (URL base, token de acesso, timeout)
        do sistema de configuração e configura os cabeçalhos apropriados.
        
        Raises:
            ConfigurationError: Se as configurações do Jira não estiverem válidas.
        """
        settings = get_settings().jira
        
        # Configura cabeçalhos específicos do Jira
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
    """Cliente HTTP configurado para acesso à API do VT/BlizzDesign.

    Lida com autenticação específica do VT usando Bearer token.
    Usado para consultar dados de arquitetura e componentes.
    """

    def __init__(self):
        """Inicializa cliente do VT com configurações do arquivo de configuração.
        
        Configura autenticação via Bearer token e cabeçalhos
        apropriados para comunicação com a API do VT/BlizzDesign.
        
        Raises:
            ConfigurationError: Se as configurações do VT não estiverem válidas.
        """
        settings = get_settings().vt
        
        # Configura cabeçalhos específicos do VT/BlizzDesign
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
    """Cliente HTTP configurado para acesso ao Component (Portal Tech).

    Lida tanto com acesso via API (com token) quanto fallback via web scraping.
    Utilizado para obter informações de componentes e versões.
    """

    def __init__(self):
        """Inicializa cliente do Component (Portal Tech) com configurações do arquivo de configuração.
        
        Configura cabeçalhos para simular navegador web (útil para web scraping)
        e adiciona token de autenticação se disponível nas configurações.
        
        Raises:
            ConfigurationError: Se as configurações do Portal Tech não estiverem válidas.
        """
        settings = get_settings().portal_tech
        
        # Cabeçalhos que simulam um navegador web para compatibilidade
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
        }
        
        # Adiciona token de autenticação se configurado
        if settings.auth_token:
            headers["Authorization"] = f"Bearer {settings.auth_token}"
        
        super().__init__(
            base_url=settings.base_url,
            timeout=settings.timeout,
            headers=headers
        )


class ARQCORClient(BaseHTTPClient):
    """Cliente HTTP configurado para acesso à API do ARQCOR.

    Lida com fluxo de autenticação OAuth2 e gerenciamento de tokens.
    Implementa renovação automática de tokens quando expirados.
    """

    def __init__(self):
        """Inicializa cliente do ARQCOR com configurações do arquivo de configuração.
        
        Configura credenciais OAuth2 e inicializa variáveis de controle
        de token para gerenciamento automático de autenticação.
        
        Raises:
            ConfigurationError: Se as configurações do ARQCOR não estiverem válidas.
        """
        settings = get_settings().arqcor
        
        super().__init__(
            base_url=settings.base_url,
            timeout=settings.timeout
        )
        
        # Credenciais OAuth2
        self.client_id = settings.client_id
        self.client_secret = settings.client_secret
        
        # Controle de token interno
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    async def _ensure_authenticated(self) -> None:
        """Garante que um token OAuth2 válido está disponível.

        Verifica se o token atual ainda é válido e renova
        se expirado ou não presente.
        
        Raises:
            httpx.HTTPError: Se falha na renovação do token.
        """
        if self._access_token and self._token_expires_at:
            # Verifica se token ainda é válido
            if datetime.now(timezone.utc) < self._token_expires_at:
                return
        
        # Token expirado ou não presente, renova
        await self._authenticate()

    async def _authenticate(self) -> None:
        """Autentica com ARQCOR usando credenciais OAuth2 client credentials.
        
        Implementa o fluxo OAuth2 Client Credentials Grant para obter
        um access token válido para requisições subsequentes.
        
        Raises:
            httpx.HTTPError: Se falha na autenticação.
            ValueError: Se resposta não contém token válido.
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
        expires_in = token_data.get("expires_in", 3600)  # Default 1 hora
        
        # Define expiração com buffer de 60 segundos para renovação antecipada
        self._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 60)

    async def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Faz uma requisição autenticada para o ARQCOR.

        Garante que a requisição tenha um token válido no cabeçalho
        de autorização, renovando automaticamente se necessário.

        Args:
            method: Método HTTP.
            endpoint: Endpoint da API.
            **kwargs: Argumentos adicionais da requisição.

        Returns:
            Objeto de resposta HTTP.

        Raises:
            httpx.HTTPError: Se falha na autenticação ou requisição.

        Example:
            >>> response = await arqcor_client.request("GET", "/forms")
            >>> # Token é gerenciado automaticamente
        """
        await self._ensure_authenticated()
        
        # Adiciona cabeçalho de autenticação à requisição
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = f"Bearer {self._access_token}"
        
        return await super().request(method, endpoint, **kwargs)


# Instâncias singleton para reutilização eficiente
_clients: Dict[str, Any] = {}


async def get_jira_client() -> JiraClient:
    """Obtém ou cria instância singleton do cliente Jira.

    Implementa padrão singleton para reutilizar a mesma instância
    do cliente Jira em toda a aplicação, evitando múltiplas conexões.

    Returns:
        Instância configurada do JiraClient.

    Example:
        >>> jira = await get_jira_client()
        >>> response = await jira.get("/rest/api/2/issue/PROJECT-123")
    """
    if "jira" not in _clients:
        _clients["jira"] = JiraClient()
    return _clients["jira"]


async def get_vt_client() -> VTClient:
    """Obtém ou cria instância singleton do cliente VT.

    Implementa padrão singleton para reutilizar a mesma instância
    do cliente VT em toda a aplicação.

    Returns:
        Instância configurada do VTClient.

    Example:
        >>> vt = await get_vt_client()
        >>> response = await vt.get("/api/architecture/components")
    """
    if "vt" not in _clients:
        _clients["vt"] = VTClient()
    return _clients["vt"]


async def get_portal_tech_client() -> PortalTechClient:
    """Obtém ou cria instância singleton do cliente Component (Portal Tech).

    Implementa padrão singleton para reutilizar a mesma instância
    do cliente Portal Tech em toda a aplicação.

    Returns:
        Instância configurada do PortalTechClient.

    Example:
        >>> portal = await get_portal_tech_client()
        >>> response = await portal.get("/components/user-service")
    """
    if "portal_tech" not in _clients:
        _clients["portal_tech"] = PortalTechClient()
    return _clients["portal_tech"]


async def get_arqcor_client() -> ARQCORClient:
    """Obtém ou cria instância singleton do cliente ARQCOR.

    Implementa padrão singleton para reutilizar a mesma instância
    do cliente ARQCOR em toda a aplicação, mantendo o token OAuth2
    em memória para eficiência.

    Returns:
        Instância configurada do ARQCORClient.

    Example:
        >>> arqcor = await get_arqcor_client()
        >>> response = await arqcor.get("/api/forms/validation")
    """
    if "arqcor" not in _clients:
        _clients["arqcor"] = ARQCORClient()
    return _clients["arqcor"]