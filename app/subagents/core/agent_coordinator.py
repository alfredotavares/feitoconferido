"""
Agente coordenador principal - orquestra subagentes
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent, AgentMessage, AgentResponse, AgentStatus

class AgentCoordinator(BaseAgent):
    """Coordenador principal que gerencia todos os subagentes"""
    
    def __init__(self):
        super().__init__("coordinator", "Coordenador Principal")
        self.subagents: Dict[str, BaseAgent] = {}
        self.task_queue = asyncio.Queue()
        self.results_cache: Dict[str, Any] = {}
        
    def register_agent(self, agent: BaseAgent):
        """Registra um subagente"""
        self.subagents[agent.agent_id] = agent
        self.logger.info(f"Agente {agent.name} registrado")
        
    async def process_message(self, message: AgentMessage) -> AgentResponse:
        """Processa mensagem recebida"""
        try:
            self.status = AgentStatus.PROCESSING
            
            if message.message_type == "task_request":
                return await self._handle_task_request(message.content)
            elif message.message_type == "agent_response":
                return await self._handle_agent_response(message.content)
            else:
                return AgentResponse(
                    agent_id=self.agent_id,
                    status=AgentStatus.ERROR,
                    error=f"Tipo de mensagem desconhecido: {message.message_type}"
                )
                
        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem: {str(e)}")
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                error=str(e)
            )
        finally:
            self.status = AgentStatus.IDLE
            
    async def execute_task(self, task: Dict[str, Any]) -> AgentResponse:
        """Executa tarefa coordenando subagentes"""
        try:
            self.status = AgentStatus.PROCESSING
            task_type = task.get("type", "unknown")
            
            if task_type == "search_reports":
                return await self._coordinate_search_task(task)
            elif task_type == "validate_data":
                return await self._coordinate_validation_task(task)
            elif task_type == "process_reports":
                return await self._coordinate_processing_task(task)
            else:
                return AgentResponse(
                    agent_id=self.agent_id,
                    status=AgentStatus.ERROR,
                    error=f"Tipo de tarefa desconhecido: {task_type}"
                )
                
        except Exception as e:
            self.logger.error(f"Erro ao executar tarefa: {str(e)}")
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                error=str(e)
            )
        finally:
            self.status = AgentStatus.IDLE
            
    async def _coordinate_search_task(self, task: Dict[str, Any]) -> AgentResponse:
        """Coordena tarefa de busca nos relatórios"""
        # Delega para o agente de processamento de dados
        if "processamento_dados" in self.subagents:
            agent = self.subagents["processamento_dados"]
            return await agent.execute_task(task)
        else:
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                error="Agente de processamento de dados não encontrado"
            )
            
    async def _coordinate_validation_task(self, task: Dict[str, Any]) -> AgentResponse:
        """Coordena tarefa de validação"""
        # Delega para o agente de validação
        if "validacao_conferencia" in self.subagents:
            agent = self.subagents["validacao_conferencia"]
            return await agent.execute_task(task)
        else:
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                error="Agente de validação não encontrado"
            )
            
    async def _coordinate_processing_task(self, task: Dict[str, Any]) -> AgentResponse:
        """Coordena tarefa de processamento completo"""
        results = []
        
        # Primeiro processa os dados
        if "processamento_dados" in self.subagents:
            processing_result = await self.subagents["processamento_dados"].execute_task(task)
            results.append(processing_result)
            
            # Se processamento foi bem-sucedido, valida os resultados
            if processing_result.status == AgentStatus.COMPLETED and "validacao_conferencia" in self.subagents:
                validation_task = {
                    "type": "validate_data",
                    "data": processing_result.result
                }
                validation_result = await self.subagents["validacao_conferencia"].execute_task(validation_task)
                results.append(validation_result)
                
        return AgentResponse(
            agent_id=self.agent_id,
            status=AgentStatus.COMPLETED,
            result={"coordinated_results": results}
        )
        
    async def _handle_task_request(self, content: Dict[str, Any]) -> AgentResponse:
        """Manipula solicitação de tarefa"""
        return await self.execute_task(content)
        
    async def _handle_agent_response(self, content: Dict[str, Any]) -> AgentResponse:
        """Manipula resposta de agente"""
        # Armazena resultado no cache
        agent_id = content.get("agent_id")
        if agent_id:
            self.results_cache[agent_id] = content
            
        return AgentResponse(
            agent_id=self.agent_id,
            status=AgentStatus.COMPLETED,
            result={"message": "Resposta processada"}
        )
        
    async def get_system_status(self) -> Dict[str, Any]:
        """Retorna status do sistema"""
        status = {
            "coordinator_status": self.status.value,
            "registered_agents": len(self.subagents),
            "agents_status": {}
        }
        
        for agent_id, agent in self.subagents.items():
            status["agents_status"][agent_id] = {
                "name": agent.name,
                "status": agent.status.value
            }
            
        return status

