"""
Subagente especializado em validação e conferência
"""

from typing import Dict, List, Any, Optional
from ..core.base_agent import BaseAgent, AgentMessage, AgentResponse, AgentStatus

class ValidacaoConferenciaAgent(BaseAgent):
    """Agente especializado em validação e conferência de dados"""
    
    def __init__(self):
        super().__init__("validacao_conferencia", "Agente de Validação e Conferência")
        self.validation_rules = self._load_validation_rules()
        
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Carrega regras de validação"""
        return {
            "status_values": ["COMPLIANT", "NON-COMPLIANT", "PARTIAL"],
            "required_fields": ["timestamp", "checks"],
            "check_required_fields": ["status", "issues", "recommendations"],
            "timestamp_format": r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
            "max_issues_per_check": 10,
            "max_recommendations_per_check": 10
        }
        
    async def process_message(self, message: AgentMessage) -> AgentResponse:
        """Processa mensagem recebida"""
        try:
            self.status = AgentStatus.PROCESSING
            
            if message.message_type == "validate_request":
                return await self._handle_validation_request(message.content)
            elif message.message_type == "compliance_check":
                return await self._handle_compliance_check(message.content)
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
        """Executa tarefa de validação"""
        try:
            self.status = AgentStatus.PROCESSING
            task_type = task.get("type", "unknown")
            
            if task_type == "validate_data":
                return await self._validate_data(task.get("data", {}))
            elif task_type == "validate_report":
                return await self._validate_report(task.get("report", {}))
            elif task_type == "compliance_analysis":
                return await self._compliance_analysis(task.get("data", {}))
            elif task_type == "quality_check":
                return await self._quality_check(task.get("data", {}))
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
            
    async def _validate_data(self, data: Dict[str, Any]) -> AgentResponse:
        """Valida dados gerais"""
        try:
            validation_results = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "summary": {}
            }
            
            # Se os dados contêm resultados de busca
            if "results" in data:
                results = data["results"]
                validation_results["summary"]["total_results"] = len(results)
                
                for i, result in enumerate(results):
                    result_validation = await self._validate_search_result(result)
                    if not result_validation["is_valid"]:
                        validation_results["is_valid"] = False
                        validation_results["errors"].extend([
                            f"Resultado {i}: {error}" for error in result_validation["errors"]
                        ])
                        
            # Se os dados contêm relatórios
            elif "reports" in data:
                reports = data["reports"]
                validation_results["summary"]["total_reports"] = len(reports)
                
                for i, report in enumerate(reports):
                    report_validation = await self._validate_report(report)
                    if not report_validation["is_valid"]:
                        validation_results["is_valid"] = False
                        validation_results["errors"].extend([
                            f"Relatório {i}: {error}" for error in report_validation["errors"]
                        ])
                        
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result=validation_results
            )
            
        except Exception as e:
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                error=f"Erro na validação de dados: {str(e)}"
            )
            
    async def _validate_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Valida um relatório individual"""
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Verifica campos obrigatórios
        for field in self.validation_rules["required_fields"]:
            if field not in report:
                validation["is_valid"] = False
                validation["errors"].append(f"Campo obrigatório ausente: {field}")
                
        # Valida timestamp se presente
        if "timestamp" in report:
            import re
            if not re.match(self.validation_rules["timestamp_format"], report["timestamp"]):
                validation["warnings"].append("Formato de timestamp pode estar incorreto")
                
        # Valida checks
        if "checks" in report:
            for check_name, check_details in report["checks"].items():
                check_validation = self._validate_check(check_name, check_details)
                if not check_validation["is_valid"]:
                    validation["is_valid"] = False
                    validation["errors"].extend([
                        f"Check '{check_name}': {error}" for error in check_validation["errors"]
                    ])
                    
        return validation
        
    def _validate_check(self, check_name: str, check_details: Dict[str, Any]) -> Dict[str, Any]:
        """Valida um check individual"""
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Verifica campos obrigatórios do check
        for field in self.validation_rules["check_required_fields"]:
            if field not in check_details:
                validation["is_valid"] = False
                validation["errors"].append(f"Campo obrigatório ausente: {field}")
                
        # Valida status
        if "status" in check_details:
            if check_details["status"] not in self.validation_rules["status_values"]:
                validation["is_valid"] = False
                validation["errors"].append(f"Status inválido: {check_details['status']}")
                
        # Valida quantidade de issues
        if "issues" in check_details:
            if len(check_details["issues"]) > self.validation_rules["max_issues_per_check"]:
                validation["warnings"].append("Muitas issues para um check")
                
        # Valida quantidade de recomendações
        if "recommendations" in check_details:
            if len(check_details["recommendations"]) > self.validation_rules["max_recommendations_per_check"]:
                validation["warnings"].append("Muitas recomendações para um check")
                
        return validation
        
    async def _validate_search_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Valida um resultado de busca"""
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        required_fields = ["timestamp", "check", "status"]
        for field in required_fields:
            if field not in result:
                validation["is_valid"] = False
                validation["errors"].append(f"Campo obrigatório ausente: {field}")
                
        # Valida status
        if "status" in result:
            if result["status"] not in self.validation_rules["status_values"]:
                validation["is_valid"] = False
                validation["errors"].append(f"Status inválido: {result['status']}")
                
        return validation
        
    async def _compliance_analysis(self, data: Dict[str, Any]) -> AgentResponse:
        """Analisa conformidade dos dados"""
        try:
            analysis = {
                "compliance_score": 0.0,
                "total_checks": 0,
                "compliant_checks": 0,
                "non_compliant_checks": 0,
                "partial_checks": 0,
                "critical_issues": [],
                "recommendations_summary": []
            }
            
            if "results" in data:
                results = data["results"]
                analysis["total_checks"] = len(results)
                
                for result in results:
                    status = result.get("status", "UNKNOWN")
                    if status == "COMPLIANT":
                        analysis["compliant_checks"] += 1
                    elif status == "NON-COMPLIANT":
                        analysis["non_compliant_checks"] += 1
                        # Adiciona issues críticas
                        issues = result.get("issues", [])
                        analysis["critical_issues"].extend(issues)
                    elif status == "PARTIAL":
                        analysis["partial_checks"] += 1
                        
                    # Coleta recomendações
                    recommendations = result.get("recommendations", [])
                    analysis["recommendations_summary"].extend(recommendations)
                    
            # Calcula score de conformidade
            if analysis["total_checks"] > 0:
                analysis["compliance_score"] = (
                    analysis["compliant_checks"] + (analysis["partial_checks"] * 0.5)
                ) / analysis["total_checks"]
                
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result=analysis
            )
            
        except Exception as e:
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                error=f"Erro na análise de conformidade: {str(e)}"
            )
            
    async def _quality_check(self, data: Dict[str, Any]) -> AgentResponse:
        """Verifica qualidade dos dados"""
        try:
            quality_metrics = {
                "completeness": 0.0,
                "consistency": 0.0,
                "accuracy": 0.0,
                "overall_quality": 0.0,
                "issues_found": [],
                "suggestions": []
            }
            
            # Implementa verificações de qualidade específicas
            if "results" in data:
                results = data["results"]
                total_results = len(results)
                
                if total_results > 0:
                    complete_results = sum(1 for r in results if all(
                        field in r for field in ["timestamp", "check", "status"]
                    ))
                    quality_metrics["completeness"] = complete_results / total_results
                    
                    # Verifica consistência de status
                    status_values = [r.get("status") for r in results]
                    valid_statuses = sum(1 for s in status_values if s in self.validation_rules["status_values"])
                    quality_metrics["consistency"] = valid_statuses / total_results if total_results > 0 else 0
                    
                    # Assume accuracy baseada na presença de dados estruturados
                    structured_results = sum(1 for r in results if 
                        isinstance(r.get("issues", []), list) and 
                        isinstance(r.get("recommendations", []), list)
                    )
                    quality_metrics["accuracy"] = structured_results / total_results
                    
            # Calcula qualidade geral
            quality_metrics["overall_quality"] = (
                quality_metrics["completeness"] + 
                quality_metrics["consistency"] + 
                quality_metrics["accuracy"]
            ) / 3
            
            # Adiciona sugestões baseadas na qualidade
            if quality_metrics["completeness"] < 0.8:
                quality_metrics["suggestions"].append("Melhorar completude dos dados")
            if quality_metrics["consistency"] < 0.9:
                quality_metrics["suggestions"].append("Padronizar valores de status")
            if quality_metrics["accuracy"] < 0.8:
                quality_metrics["suggestions"].append("Verificar estrutura dos dados")
                
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result=quality_metrics
            )
            
        except Exception as e:
            return AgentResponse(
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                error=f"Erro na verificação de qualidade: {str(e)}"
            )
            
    async def _handle_validation_request(self, content: Dict[str, Any]) -> AgentResponse:
        """Manipula solicitação de validação"""
        return await self._validate_data(content)
        
    async def _handle_compliance_check(self, content: Dict[str, Any]) -> AgentResponse:
        """Manipula verificação de conformidade"""
        return await self._compliance_analysis(content)

