"""
Configurações da aplicação
"""

import os
from typing import Dict, Any

class AppConfig:
    """Configurações da aplicação"""
    
    # Configurações do servidor
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Configurações do GCP
    PROJECT_ID = os.getenv("GCP_PROJECT_ID", "gft-bu-gcp")
    REGION = os.getenv("GCP_REGION", "us-central1")
    
    # Configurações dos dados
    DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    # Configurações de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Configurações dos agentes
    AGENT_CONFIG = {
        "coordinator": {
            "name": "Coordenador Principal",
            "timeout": 30
        },
        "processamento_dados": {
            "name": "Agente de Processamento de Dados",
            "cache_enabled": True,
            "timeout": 15
        },
        "validacao_conferencia": {
            "name": "Agente de Validação e Conferência",
            "strict_validation": True,
            "timeout": 10
        }
    }
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Retorna todas as configurações"""
        return {
            "server": {
                "host": cls.HOST,
                "port": cls.PORT,
                "debug": cls.DEBUG
            },
            "gcp": {
                "project_id": cls.PROJECT_ID,
                "region": cls.REGION
            },
            "data": {
                "path": cls.DATA_PATH
            },
            "logging": {
                "level": cls.LOG_LEVEL
            },
            "agents": cls.AGENT_CONFIG
        }

