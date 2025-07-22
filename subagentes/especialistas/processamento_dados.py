"""
Subagente especializado em processamento de dados
"""

import json
import os
from typing import Dict, List, Any, Optional
from ..core.base_agent import BaseAgent, AgentMessage, AgentResponse, AgentStatus

class ProcessamentoDadosAgent(BaseAgent):
    """Agente especializado em processamento e busca de dados nos relatórios"""
    
    def __init__(self):
        super().__init__("processamento_dados", "Agente de Processamento de Dados")
        self.reports_cache: Optional[List[Dict]] = None
        self.data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'mocks/data')
        
    async def process_message(self, message: AgentMessage) -> AgentResponse:
        """Processa mensagem recebida"""
        try:
            self.status = AgentStatus.PROCESSING
            
            if message.message_type == "search_request":
                return await self._handle_search_request(message.content)
            elif message.message_type == "load_data":
                return await self._handle_load_data(message.content)
            else:
                return AgentResponse(
                    agent_id=self.agent_id,
                    status=AgentStatus.ERROR,
                    error=f"Tipo de mensagem não suportado: {message.message_type}"
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
        """Executa tarefa de processamento de dados"""
        try:
            self.status = AgentStatus.PROCESSING
            task_type = task.get("type", "unknown")
            
            if task_type == "search_reports":
                return await self._search_reports(task.get("query", ""))
            elif task_type == "load_reports":
                return await self._load_reports()
            elif task_type == "get_report_summary":
                return await self._get_report_summary()
            elif task_type == "filter_reports":
                return await self._filter_reports(task.get("filters", {}))
            else:
                return AgentResponse(
                    agent_id=self.agent_id,
                    status=AgentStatus.ERROR,
                    error=f"Tipo de tarefa não suportado: {task_type}"
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
            
    async def _load_reports(self) -> AgentResponse:
        """Carrega todos os relatórios dos arquivos JSON"""
        try:
            if self.reports_cache is not None:
                return AgentResponse(
                    agent_id=self.agent_id,
                    status=AgentStatus.COMPLETED,
                    result={"reports": self.reports_cache, "source": "cache"}
                )
                
            reports = []
            
            if not os.path.exists(self.data_path):
                return AgentResponse(
                    agent_id=self.agent_id,
                    status=AgentStatus.ERROR,
                    error=f"Diretório de dados não encontrado: {self.data_path}"
                )
                
            for filename in os.listdir(self.data_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.data_path, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            report = json.load(f)
                            report['source_file'] = filename
                            reports.append(report)
                    except Exception as e:
                        self.logger.warning(f"Erro ao carregar arquivo {filename}: {str(e)}")
                        
            self.reports_cache = reports
            
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result={
                    "reports": reports,
                    "count": len(reports),
                    "source": "files"
                }
            )
            
        except Exception as e:
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                error=f"Erro ao carregar relatórios: {str(e)}"
            )
            
    async def _search_reports(self, query: str) -> AgentResponse:
        """Busca nos relatórios baseado na query"""
        try:
            # Carrega relatórios se não estiverem em cache
            if self.reports_cache is None:
                load_result = await self._load_reports()
                if load_result.status != AgentStatus.COMPLETED:
                    return load_result
                    
            results = []
            query_lower = query.lower()
            
            for report in self.reports_cache:
                for check_name, check_details in report.get("checks", {}).items():
                    if query_lower in check_name.lower():
                        results.append({
                            "timestamp": report.get("timestamp"),
                            "source_file": report.get("source_file"),
                            "check": check_name,
                            "status": check_details.get("status"),
                            "issues": check_details.get("issues", []),
                            "recommendations": check_details.get("recommendations", [])
                        })
                        
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result={
                    "query": query,
                    "results": results,
                    "count": len(results)
                }
            )
            
        except Exception as e:
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                error=f"Erro na busca: {str(e)}"
            )
            
    async def _get_report_summary(self) -> AgentResponse:
        """Gera resumo dos relatórios"""
        try:
            if self.reports_cache is None:
                load_result = await self._load_reports()
                if load_result.status != AgentStatus.COMPLETED:
                    return load_result
                    
            summary = {
                "total_reports": len(self.reports_cache),
                "status_summary": {"COMPLIANT": 0, "NON-COMPLIANT": 0, "PARTIAL": 0},
                "total_checks": 0,
                "total_issues": 0,
                "total_recommendations": 0
            }
            
            for report in self.reports_cache:
                for check_name, check_details in report.get("checks", {}).items():
                    summary["total_checks"] += 1
                    status = check_details.get("status", "UNKNOWN")
                    if status in summary["status_summary"]:
                        summary["status_summary"][status] += 1
                    summary["total_issues"] += len(check_details.get("issues", []))
                    summary["total_recommendations"] += len(check_details.get("recommendations", []))
                    
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result=summary
            )
            
        except Exception as e:
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                error=f"Erro ao gerar resumo: {str(e)}"
            )
            
    async def _filter_reports(self, filters: Dict[str, Any]) -> AgentResponse:
        """Filtra relatórios baseado nos critérios fornecidos"""
        try:
            if self.reports_cache is None:
                load_result = await self._load_reports()
                if load_result.status != AgentStatus.COMPLETED:
                    return load_result
                    
            filtered_results = []
            status_filter = filters.get("status")
            date_filter = filters.get("date")
            
            for report in self.reports_cache:
                for check_name, check_details in report.get("checks", {}).items():
                    include = True
                    
                    if status_filter and check_details.get("status") != status_filter:
                        include = False
                        
                    if date_filter and report.get("timestamp", "").startswith(date_filter):
                        include = True
                    elif date_filter:
                        include = False
                        
                    if include:
                        filtered_results.append({
                            "timestamp": report.get("timestamp"),
                            "source_file": report.get("source_file"),
                            "check": check_name,
                            "status": check_details.get("status"),
                            "issues": check_details.get("issues", []),
                            "recommendations": check_details.get("recommendations", [])
                        })
                        
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result={
                    "filters": filters,
                    "results": filtered_results,
                    "count": len(filtered_results)
                }
            )
            
        except Exception as e:
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                error=f"Erro ao filtrar relatórios: {str(e)}"
            )
            
    async def _handle_search_request(self, content: Dict[str, Any]) -> AgentResponse:
        """Manipula solicitação de busca"""
        query = content.get("query", "")
        return await self._search_reports(query)
        
    async def _handle_load_data(self, content: Dict[str, Any]) -> AgentResponse:
        """Manipula solicitação de carregamento de dados"""
        return await self._load_reports()

