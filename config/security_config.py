"""
Configurações de segurança para o sistema Feito Conferido
"""

import os
import logging
from typing import Dict, List, Any

# Configuração de logging seguro
SECURITY_LOG_LEVEL = os.getenv('SECURITY_LOG_LEVEL', 'INFO')
SECURITY_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Configurações de validação de entrada
MAX_QUERY_LENGTH = 1000
MAX_FILE_SIZE_MB = 50
ALLOWED_FILE_EXTENSIONS = ['.json', '.txt', '.csv']

# Configurações de rate limiting
MAX_REQUESTS_PER_MINUTE = 60
MAX_REQUESTS_PER_HOUR = 1000

# Configurações de sanitização
DANGEROUS_PATTERNS = [
    r'<script.*?>.*?</script>',
    r'javascript:',
    r'vbscript:',
    r'onload\s*=',
    r'onerror\s*=',
    r'eval\s*\(',
    r'exec\s*\(',
    r'import\s+os',
    r'import\s+subprocess',
    r'__import__',
]

# Configurações de auditoria
AUDIT_ENABLED = True
AUDIT_LOG_PATH = os.getenv('AUDIT_LOG_PATH', '/var/log/feito_conferido_audit.log')

# Configurações de criptografia
ENCRYPTION_KEY_PATH = os.getenv('ENCRYPTION_KEY_PATH', '/etc/feito_conferido/encryption.key')
HASH_ALGORITHM = 'sha256'

# Configurações de acesso
REQUIRE_AUTHENTICATION = True
SESSION_TIMEOUT_MINUTES = 30
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION_MINUTES = 15

# Configurações de dados sensíveis
SENSITIVE_DATA_PATTERNS = [
    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
    r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
    r'\b\d{3}\.\d{3}\.\d{3}\.\d{3}\b',  # IP address
]

# Configurações de backup e recuperação
BACKUP_ENABLED = True
BACKUP_ENCRYPTION_ENABLED = True
BACKUP_RETENTION_DAYS = 90

class SecurityConfig:
    """Classe para gerenciar configurações de segurança"""
    
    @staticmethod
    def get_max_query_length() -> int:
        """Retorna o tamanho máximo permitido para queries"""
        return MAX_QUERY_LENGTH
    
    @staticmethod
    def get_allowed_extensions() -> List[str]:
        """Retorna extensões de arquivo permitidas"""
        return ALLOWED_FILE_EXTENSIONS
    
    @staticmethod
    def get_dangerous_patterns() -> List[str]:
        """Retorna padrões perigosos para validação"""
        return DANGEROUS_PATTERNS
    
    @staticmethod
    def is_audit_enabled() -> bool:
        """Verifica se auditoria está habilitada"""
        return AUDIT_ENABLED
    
    @staticmethod
    def get_session_timeout() -> int:
        """Retorna timeout de sessão em minutos"""
        return SESSION_TIMEOUT_MINUTES
    
    @staticmethod
    def get_sensitive_patterns() -> List[str]:
        """Retorna padrões de dados sensíveis"""
        return SENSITIVE_DATA_PATTERNS

