"""
Módulo de validação e sanitização de segurança
"""

import re
import html
import logging
import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from config.security_config import SecurityConfig

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Classe para validação e sanitização de entrada"""
    
    def __init__(self):
        self.config = SecurityConfig()
        self.dangerous_patterns = self.config.get_dangerous_patterns()
        self.sensitive_patterns = self.config.get_sensitive_patterns()
    
    def validate_input_length(self, input_text: str) -> bool:
        """Valida se o texto de entrada não excede o tamanho máximo"""
        max_length = self.config.get_max_query_length()
        if len(input_text) > max_length:
            logger.warning(f"Input excede tamanho máximo: {len(input_text)} > {max_length}")
            return False
        return True
    
    def sanitize_input(self, input_text: str) -> str:
        """Sanitiza entrada do usuário removendo conteúdo perigoso"""
        if not input_text:
            return ""
        
        # Escape HTML
        sanitized = html.escape(input_text)
        
        # Remove padrões perigosos
        for pattern in self.dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Remove caracteres de controle
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')
        
        return sanitized.strip()
    
    def validate_file_path(self, file_path: str) -> bool:
        """Valida se o caminho do arquivo é seguro"""
        try:
            path = Path(file_path)
            
            # Verifica se é um caminho absoluto válido
            if not path.is_absolute():
                logger.warning(f"Caminho não é absoluto: {file_path}")
                return False
            
            # Verifica se não contém traversal de diretório
            if '..' in str(path):
                logger.warning(f"Tentativa de traversal de diretório: {file_path}")
                return False
            
            # Verifica extensão do arquivo
            if path.suffix not in self.config.get_allowed_extensions():
                logger.warning(f"Extensão não permitida: {path.suffix}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação do caminho: {e}")
            return False
    
    def detect_sensitive_data(self, text: str) -> List[str]:
        """Detecta dados sensíveis no texto"""
        detected = []
        
        for pattern in self.sensitive_patterns:
            matches = re.findall(pattern, text)
            if matches:
                detected.extend(matches)
        
        return detected
    
    def mask_sensitive_data(self, text: str) -> str:
        """Mascara dados sensíveis no texto"""
        masked_text = text
        
        for pattern in self.sensitive_patterns:
            masked_text = re.sub(pattern, '[DADOS_SENSÍVEIS_MASCARADOS]', masked_text)
        
        return masked_text
    
    def validate_json_structure(self, json_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Valida estrutura de dados JSON"""
        try:
            # Verifica se é um dicionário válido
            if not isinstance(json_data, dict):
                return False, "Dados devem ser um objeto JSON válido"
            
            # Verifica tamanho do JSON serializado
            json_str = json.dumps(json_data)
            if len(json_str) > self.config.get_max_query_length() * 10:
                return False, "JSON muito grande"
            
            # Verifica profundidade máxima
            if self._get_json_depth(json_data) > 10:
                return False, "JSON com profundidade excessiva"
            
            return True, "JSON válido"
            
        except Exception as e:
            return False, f"Erro na validação JSON: {str(e)}"
    
    def _get_json_depth(self, obj: Any, depth: int = 0) -> int:
        """Calcula profundidade de um objeto JSON"""
        if isinstance(obj, dict):
            return max([self._get_json_depth(v, depth + 1) for v in obj.values()], default=depth)
        elif isinstance(obj, list):
            return max([self._get_json_depth(item, depth + 1) for item in obj], default=depth)
        else:
            return depth
    
    def generate_hash(self, data: str) -> str:
        """Gera hash seguro dos dados"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def validate_report_data(self, report_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Valida dados de relatório específicos"""
        try:
            # Verifica campos obrigatórios
            required_fields = ['timestamp', 'checks']
            for field in required_fields:
                if field not in report_data:
                    return False, f"Campo obrigatório ausente: {field}"
            
            # Valida estrutura de checks
            checks = report_data.get('checks', {})
            if not isinstance(checks, dict):
                return False, "Campo 'checks' deve ser um objeto"
            
            # Valida cada check
            for check_name, check_data in checks.items():
                if not isinstance(check_data, dict):
                    return False, f"Check '{check_name}' deve ser um objeto"
                
                if 'status' not in check_data:
                    return False, f"Check '{check_name}' deve ter campo 'status'"
                
                valid_statuses = ['COMPLIANT', 'PARTIAL', 'NON-COMPLIANT']
                if check_data['status'] not in valid_statuses:
                    return False, f"Status inválido em '{check_name}': {check_data['status']}"
            
            return True, "Dados de relatório válidos"
            
        except Exception as e:
            return False, f"Erro na validação de relatório: {str(e)}"

class AuditLogger:
    """Classe para logging de auditoria"""
    
    def __init__(self):
        self.config = SecurityConfig()
        self.setup_audit_logger()
    
    def setup_audit_logger(self):
        """Configura logger de auditoria"""
        if self.config.is_audit_enabled():
            self.audit_logger = logging.getLogger('audit')
            self.audit_logger.setLevel(logging.INFO)
            
            # Handler para arquivo de auditoria
            handler = logging.FileHandler('/tmp/feito_conferido_audit.log')
            formatter = logging.Formatter(
                '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.audit_logger.addHandler(handler)
    
    def log_access(self, user_id: str, action: str, resource: str, success: bool):
        """Registra acesso a recursos"""
        if self.config.is_audit_enabled():
            status = "SUCCESS" if success else "FAILURE"
            self.audit_logger.info(
                f"USER:{user_id} ACTION:{action} RESOURCE:{resource} STATUS:{status}"
            )
    
    def log_data_access(self, user_id: str, file_path: str, operation: str):
        """Registra acesso a dados"""
        if self.config.is_audit_enabled():
            self.audit_logger.info(
                f"USER:{user_id} DATA_ACCESS:{operation} FILE:{file_path}"
            )
    
    def log_security_event(self, event_type: str, details: str, severity: str = "INFO"):
        """Registra eventos de segurança"""
        if self.config.is_audit_enabled():
            self.audit_logger.log(
                getattr(logging, severity),
                f"SECURITY_EVENT:{event_type} DETAILS:{details}"
            )

