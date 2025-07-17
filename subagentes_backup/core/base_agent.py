"""
Sistema base para comunicação entre agentes
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Status possíveis para um agente"""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AgentMessage:
    """Estrutura de mensagem entre agentes"""
    sender: str
    receiver: str
    message_type: str
    content: Dict[str, Any]
    timestamp: str
    priority: int = 1

@dataclass
class AgentResponse:
    """Estrutura de resposta de um agente"""
    agent_id: str
    status: AgentStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseAgent(ABC):
    """Classe base para todos os agentes do sistema"""
    
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.status = AgentStatus.IDLE
        self.message_queue = asyncio.Queue()
        self.logger = logging.getLogger(f"{__name__}.{agent_id}")
        
    async def send_message(self, receiver: str, message_type: str, content: Dict[str, Any]) -> None:
        """Envia mensagem para outro agente"""
        message = AgentMessage(
            sender=self.agent_id,
            receiver=receiver,
            message_type=message_type,
            content=content,
            timestamp=self._get_timestamp()
        )
        self.logger.info(f"Enviando mensagem para {receiver}: {message_type}")
        # Implementação específica de envio seria aqui
        
    async def receive_message(self) -> AgentMessage:
        """Recebe mensagem da fila"""
        return await self.message_queue.get()
        
    @abstractmethod
    async def process_message(self, message: AgentMessage) -> AgentResponse:
        """Processa uma mensagem recebida"""
        pass
        
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> AgentResponse:
        """Executa uma tarefa específica"""
        pass
        
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual"""
        from datetime import datetime
        return datetime.now().isoformat()
        
    async def start(self):
        """Inicia o agente"""
        self.logger.info(f"Agente {self.name} iniciado")
        self.status = AgentStatus.IDLE
        
    async def stop(self):
        """Para o agente"""
        self.logger.info(f"Agente {self.name} parado")
        self.status = AgentStatus.IDLE

