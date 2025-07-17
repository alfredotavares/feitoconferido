"""
Módulo de validação e sanitização de segurança
Baseado no sistema de segurança do Feito Conferido
"""

import re
import html
import hashlib
import json
import structlog
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

# Configuração de logs estruturados
logger = structlog.get_logger("security_validator")

class SecurityValidator:
    """Classe para validação e sanitização de entrada"""
    
    def __init__(self):
        # Padrões perigosos
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'eval\s*\(',
            r'exec\s*\(',
            r'import\s+os',
            r'__import__',
            r'subprocess',
            r'system\s*\(',
        ]
        
        # Padrões de dados sensíveis
        self.sensitive_patterns = {
            'cpf': r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}',
            'cnpj': r'\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'telefone': r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}',
            'cartao': r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}',
            'ip': r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        }
        
        # Configurações de segurança
        self.max_query_length = 1000
        self.max_file_size = 1024 * 1024  # 1MB
        
    def validate_input_length(self, text: str) -> bool:
        """Valida se o texto não excede o limite"""
        return len(text) <= self.max_query_length
    
    def sanitize_input(self, text: str) -> str:
        """Sanitiza entrada removendo caracteres perigosos"""
        if not text:
            return ""
        
        # HTML escape
        sanitized = html.escape(text)
        
        # Remove padrões perigosos
        for pattern in self.dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Remove caracteres de controle
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
        
        return sanitized.strip()
    
    def detect_sensitive_data(self, text: str) -> List[str]:
        """Detecta dados sensíveis no texto"""
        detected = []
        
        for data_type, pattern in self.sensitive_patterns.items():
            if re.search(pattern, text):
                detected.append(data_type)
        
        return detected
    
    def mask_sensitive_data(self, text: str) -> str:
        """Mascara dados sensíveis no texto"""
        masked = text
        
        # CPF: 123.456.789-01 -> 123.***.**-01
        masked = re.sub(r'(\d{3})\.?\d{3}\.?\d{3}(-?\d{2})', r'\1.***.**\2', masked)
        
        # CNPJ: 12.345.678/0001-90 -> 12.***.***/**01-90
        masked = re.sub(r'(\d{2})\.?\d{3}\.?\d{3}(/?\d{2})\d{2}(-?\d{2})', r'\1.***.***\2**\3', masked)
        
        # Email: user@domain.com -> u***@domain.com
        masked = re.sub(r'\b([A-Za-z])[A-Za-z0-9._%+-]*(@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b', r'\1***\2', masked)
        
        # Telefone: (11) 99999-9999 -> (11) 9****-9999
        masked = re.sub(r'(\(?\d{2}\)?\s?\d)\d{3,4}(-?\d{4})', r'\1****\2', masked)
        
        # Cartão: 1234 5678 9012 3456 -> 1234 **** **** 3456
        masked = re.sub(r'(\d{4})[\s-]?\d{4}[\s-]?\d{4}[\s-]?(\d{4})', r'\1 **** **** \2', masked)
        
        # IP: 192.168.1.100 -> 192.168.*.***
        masked = re.sub(r'(\d{1,3}\.\d{1,3}\.)\d{1,3}\.\d{1,3}', r'\1*.**', masked)
        
        return masked
    
    def validate_file_path(self, file_path: str) -> bool:
        """Valida se o caminho do arquivo é seguro"""
        # Previne directory traversal
        if '..' in file_path or file_path.startswith('/'):
            return False
        
        # Verifica extensões permitidas
        allowed_extensions = ['.json', '.txt', '.md']
        if not any(file_path.endswith(ext) for ext in allowed_extensions):
            return False
        
        return True
    
    def validate_json_structure(self, data: Dict[str, Any], schema_type: str) -> Tuple[bool, str]:
        """Valida estrutura JSON baseada no tipo"""
        try:
            if schema_type == "aprovacao":
                required_fields = ['titulo', 'arquiteto_responsavel', 'ciclo_desenvolvimento']
                for field in required_fields:
                    if field not in data:
                        return False, f"Campo obrigatório ausente: {field}"
                
                # Valida estrutura de validação
                if 'validacao' in data and not isinstance(data['validacao'], dict):
                    return False, "Campo 'validacao' deve ser um objeto"
                
                # Valida lista de componentes
                if 'componentes' in data and not isinstance(data['componentes'], list):
                    return False, "Campo 'componentes' deve ser uma lista"
            
            return True, ""
            
        except Exception as e:
            return False, f"Erro na validação: {str(e)}"
    
    def generate_hash(self, content: str) -> str:
        """Gera hash SHA-256 do conteúdo"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def validate_file_size(self, file_path: str) -> bool:
        """Valida se o arquivo não excede o tamanho máximo"""
        try:
            import os
            return os.path.getsize(file_path) <= self.max_file_size
        except:
            return False

class AuditLogger:
    """Classe para logs de auditoria estruturados"""
    
    def __init__(self):
        self.logger = structlog.get_logger("audit")
    
    def log_access(self, user_id: str, action: str, resource: str, success: bool, **kwargs):
        """Log de acesso a recursos"""
        self.logger.info(
            "access_log",
            user_id=user_id,
            action=action,
            resource=resource,
            success=success,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )
    
    def log_security_event(self, event_type: str, description: str, level: str = "WARNING", **kwargs):
        """Log de eventos de segurança"""
        self.logger.warning(
            "security_event",
            event_type=event_type,
            description=description,
            level=level,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )
    
    def log_data_access(self, user_id: str, resource: str, action: str, **kwargs):
        """Log de acesso a dados"""
        self.logger.info(
            "data_access",
            user_id=user_id,
            resource=resource,
            action=action,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )
    
    def log_json_validation(self, file_name: str, is_valid: bool, error_msg: str = ""):
        """Log de validação de JSON"""
        self.logger.info(
            "json_validation",
            file_name=file_name,
            is_valid=is_valid,
            error_message=error_msg,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_query_analysis(self, query: str, results_count: int, execution_time: float, **kwargs):
        """Log de análise de consultas"""
        self.logger.info(
            "query_analysis",
            query_hash=hashlib.sha256(query.encode()).hexdigest()[:16],
            results_count=results_count,
            execution_time_ms=execution_time * 1000,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )

class RateLimiter:
    """Classe para controle de rate limiting"""
    
    def __init__(self):
        self.requests = {}
        self.max_requests_per_minute = 60
        self.max_requests_per_hour = 1000
    
    def is_allowed(self, user_id: str) -> Tuple[bool, str]:
        """Verifica se o usuário pode fazer a requisição"""
        now = datetime.utcnow()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Remove requisições antigas (mais de 1 hora)
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if (now - req_time).total_seconds() < 3600
        ]
        
        # Verifica limite por hora
        if len(self.requests[user_id]) >= self.max_requests_per_hour:
            return False, "Limite de requisições por hora excedido"
        
        # Verifica limite por minuto
        recent_requests = [
            req_time for req_time in self.requests[user_id]
            if (now - req_time).total_seconds() < 60
        ]
        
        if len(recent_requests) >= self.max_requests_per_minute:
            return False, "Limite de requisições por minuto excedido"
        
        # Adiciona a requisição atual
        self.requests[user_id].append(now)
        return True, ""

class SessionManager:
    """Classe para gerenciamento de sessões"""
    
    def __init__(self):
        self.sessions = {}
        self.session_timeout = 1800  # 30 minutos
        self.max_failed_attempts = 5
        self.failed_attempts = {}
    
    def create_session(self, user_id: str) -> str:
        """Cria nova sessão"""
        import uuid
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'is_active': True
        }
        
        return session_id
    
    def validate_session(self, session_id: str) -> Tuple[bool, str]:
        """Valida sessão"""
        if session_id not in self.sessions:
            return False, "Sessão não encontrada"
        
        session = self.sessions[session_id]
        now = datetime.utcnow()
        
        # Verifica timeout
        if (now - session['last_activity']).total_seconds() > self.session_timeout:
            session['is_active'] = False
            return False, "Sessão expirada"
        
        # Atualiza última atividade
        session['last_activity'] = now
        return True, ""
    
    def record_failed_attempt(self, user_id: str):
        """Registra tentativa de acesso falhada"""
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = []
        
        self.failed_attempts[user_id].append(datetime.utcnow())
        
        # Remove tentativas antigas (mais de 1 hora)
        self.failed_attempts[user_id] = [
            attempt for attempt in self.failed_attempts[user_id]
            if (datetime.utcnow() - attempt).total_seconds() < 3600
        ]
    
    def is_user_blocked(self, user_id: str) -> bool:
        """Verifica se usuário está bloqueado"""
        if user_id not in self.failed_attempts:
            return False
        
        recent_attempts = [
            attempt for attempt in self.failed_attempts[user_id]
            if (datetime.utcnow() - attempt).total_seconds() < 3600
        ]
        
        return len(recent_attempts) >= self.max_failed_attempts

