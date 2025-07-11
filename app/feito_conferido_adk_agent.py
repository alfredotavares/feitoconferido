"""
Agente Feito Conferido integrado com Google ADK
Compatível com agent-starter-pack e Vertex AI
Inclui validações de segurança e boas práticas
Suporte a critérios JSON e TXT
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from app.utils.security_validator import SecurityValidator, AuditLogger
from app.utils.criterios_manager import CriteriosManager
from config.security_config import SecurityConfig

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeitoConferidoADKAgent:
    """Agente Feito Conferido integrado com ADK com validações de segurança e critérios JSON"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.security_validator = SecurityValidator()
        self.audit_logger = AuditLogger()
        self.security_config = SecurityConfig()
        self.criterios_manager = CriteriosManager()
        self.reports_data = self._load_reports()
        logger.info(f"FeitoConferidoADKAgent inicializado com {len(self.reports_data)} relatórios")
        self.audit_logger.log_security_event("AGENT_INITIALIZED", "Agente inicializado com sucesso")
    
    def _load_reports(self) -> List[Dict[str, Any]]:
        """Carrega todos os relatórios JSON disponíveis com validações de segurança"""
        reports = []
        if not self.data_dir.exists():
            logger.warning(f"Diretório {self.data_dir} não encontrado")
            return reports
            
        for json_file in self.data_dir.glob("*.json"):
            try:
                # Validação de segurança do caminho do arquivo
                if hasattr(self, 'security_validator') and not self.security_validator.validate_file_path(str(json_file)):
                    logger.error(f"Arquivo rejeitado por validação de segurança: {json_file}")
                    continue
                
                # Verificação de tamanho do arquivo
                file_size_mb = json_file.stat().st_size / (1024 * 1024)
                if file_size_mb > 50:  # Limite de 50MB
                    logger.error(f"Arquivo muito grande: {json_file} ({file_size_mb:.2f}MB)")
                    continue
                
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Validação da estrutura do relatório
                    if hasattr(self, 'security_validator'):
                        is_valid, error_msg = self.security_validator.validate_report_data(data)
                        if not is_valid:
                            logger.error(f"Relatório inválido {json_file}: {error_msg}")
                            continue
                    
                    data['_source_file'] = json_file.name
                    data['_file_hash'] = self.security_validator.generate_hash(json.dumps(data, sort_keys=True)) if hasattr(self, 'security_validator') else None
                    reports.append(data)
                    logger.info(f"Carregado com segurança: {json_file.name}")
                    
                    # Log de auditoria
                    if hasattr(self, 'audit_logger'):
                        self.audit_logger.log_data_access("system", str(json_file), "READ")
                        
            except json.JSONDecodeError as e:
                logger.error(f"Erro JSON em {json_file}: {e}")
            except Exception as e:
                logger.error(f"Erro ao carregar {json_file}: {e}")
                if hasattr(self, 'audit_logger'):
                    self.audit_logger.log_security_event("FILE_LOAD_ERROR", f"Erro ao carregar {json_file}: {e}", "ERROR")
        
        return reports
    
    def get_available_reports(self) -> str:
        """Retorna lista de relatórios disponíveis"""
        if not self.reports_data:
            return "ERRO: Nenhum relatório encontrado na pasta data/"
        
        report_list = ["RELATÓRIOS FEITO CONFERIDO DISPONÍVEIS:\n"]
        for i, report in enumerate(self.reports_data, 1):
            source = report.get('_source_file', f'report_{i}')
            timestamp = report.get('timestamp', 'N/A')
            
            # Conta status dos checks
            checks = report.get('checks', {})
            compliant = sum(1 for check in checks.values() if check.get('status') == 'COMPLIANT')
            partial = sum(1 for check in checks.values() if check.get('status') == 'PARTIAL')
            non_compliant = sum(1 for check in checks.values() if check.get('status') == 'NON-COMPLIANT')
            
            report_list.append(f"{i}. ARQUIVO: {source}")
            report_list.append(f"   Data: {timestamp}")
            report_list.append(f"   Conformes: {compliant}")
            report_list.append(f"   Parciais: {partial}")
            report_list.append(f"   Não conformes: {non_compliant}\n")
        
        return "\n".join(report_list)
    
    def search_in_reports(self, query: str, user_id: str = "anonymous") -> str:
        """Busca informações nos relatórios baseado na query com validações de segurança"""
        # Log de auditoria
        self.audit_logger.log_access(user_id, "SEARCH", "reports", True)
        
        if not self.reports_data:
            return "ERRO: Nenhum relatório disponível para busca."
        
        if not query or len(query.strip()) < 2:
            self.audit_logger.log_security_event("INVALID_QUERY", f"Query muito curta: {query}", "WARNING")
            return "ERRO: Por favor, forneça um termo de busca válido (mínimo 2 caracteres)."
        
        # Validações de segurança
        if not self.security_validator.validate_input_length(query):
            self.audit_logger.log_security_event("QUERY_TOO_LONG", f"Query excede tamanho máximo: {len(query)}", "WARNING")
            return "ERRO: Termo de busca muito longo."
        
        # Sanitização da entrada
        sanitized_query = self.security_validator.sanitize_input(query)
        if sanitized_query != query:
            self.audit_logger.log_security_event("INPUT_SANITIZED", f"Query sanitizada: {query} -> {sanitized_query}", "INFO")
        
        # Detecção de dados sensíveis
        sensitive_data = self.security_validator.detect_sensitive_data(sanitized_query)
        if sensitive_data:
            self.audit_logger.log_security_event("SENSITIVE_DATA_DETECTED", f"Dados sensíveis na query: {sensitive_data}", "WARNING")
            return "ERRO: Query contém dados sensíveis. Por favor, remova informações pessoais."
        
        results = []
        query_lower = sanitized_query.lower().strip()
        
        for report in self.reports_data:
            source = report.get('_source_file', 'unknown')
            timestamp = report.get('timestamp', 'N/A')
            
            # Busca nos checks
            checks = report.get('checks', {})
            for check_name, check_data in checks.items():
                if query_lower in check_name.lower() or query_lower in str(check_data).lower():
                    status = check_data.get('status', 'N/A')
                    issues = check_data.get('issues', [])
                    recommendations = check_data.get('recommendations', [])
                    
                    results.append(f"\nARQUIVO: {source} ({timestamp})")
                    results.append(f"VERIFICAÇÃO: {check_name}:")
                    results.append(f"   Status: {status}")
                    
                    if issues:
                        # Mascarar dados sensíveis nas issues
                        masked_issues = [self.security_validator.mask_sensitive_data(issue) for issue in issues[:2]]
                        results.append(f"   Issues: {', '.join(masked_issues)}")
                    
                    if recommendations:
                        # Mascarar dados sensíveis nas recomendações
                        masked_recommendations = [self.security_validator.mask_sensitive_data(rec) for rec in recommendations[:2]]
                        results.append(f"   Recomendações: {', '.join(masked_recommendations)}")
        
        if results:
            header = f"RESULTADOS PARA '{sanitized_query}' NO FEITO CONFERIDO:\n"
            self.audit_logger.log_access(user_id, "SEARCH_SUCCESS", f"query:{sanitized_query}", True)
            return header + "\n".join(results)
        else:
            self.audit_logger.log_access(user_id, "SEARCH_NO_RESULTS", f"query:{sanitized_query}", True)
            return f"ERRO: Nenhum resultado encontrado para '{sanitized_query}' nos relatórios do Feito Conferido"
    
    def analyze_compliance(self) -> str:
        """Analisa conformidade nos relatórios"""
        if not self.reports_data:
            return "ERRO: Nenhum relatório disponível para análise de conformidade."
        
        compliance_info = ["ANÁLISE DE CONFORMIDADE - FEITO CONFERIDO:\n"]
        
        total_checks = 0
        compliant_count = 0
        partial_count = 0
        non_compliant_count = 0
        
        for report in self.reports_data:
            source = report.get('_source_file', 'unknown')
            timestamp = report.get('timestamp', 'N/A')
            checks = report.get('checks', {})
            
            compliance_info.append(f"\nARQUIVO: {source} ({timestamp}):")
            
            for check_name, check_data in checks.items():
                status = check_data.get('status', 'N/A')
                total_checks += 1
                
                if status == 'COMPLIANT':
                    compliant_count += 1
                    compliance_info.append(f"   [CONFORME] {check_name}: {status}")
                elif status == 'PARTIAL':
                    partial_count += 1
                    compliance_info.append(f"   [PARCIAL] {check_name}: {status}")
                elif status == 'NON-COMPLIANT':
                    non_compliant_count += 1
                    compliance_info.append(f"   [NÃO CONFORME] {check_name}: {status}")
                else:
                    compliance_info.append(f"   [INDEFINIDO] {check_name}: {status}")
                
                # Adiciona issues se houver
                issues = check_data.get('issues', [])
                if issues:
                    compliance_info.append(f"      Issues: {', '.join(issues[:1])}")
        
        # Adiciona resumo estatístico
        if total_checks > 0:
            compliance_info.append(f"\nRESUMO ESTATÍSTICO FEITO CONFERIDO:")
            compliance_info.append(f"   Total de verificações: {total_checks}")
            compliance_info.append(f"   Conformes: {compliant_count} ({(compliant_count/total_checks*100):.1f}%)")
            compliance_info.append(f"   Parciais: {partial_count} ({(partial_count/total_checks*100):.1f}%)")
            compliance_info.append(f"   Não conformes: {non_compliant_count} ({(non_compliant_count/total_checks*100):.1f}%)")
            
            # Avaliação geral
            if compliant_count / total_checks >= 0.8:
                compliance_info.append(f"   Avaliação Geral: EXCELENTE (≥80% conforme)")
            elif compliant_count / total_checks >= 0.6:
                compliance_info.append(f"   Avaliação Geral: BOM (≥60% conforme)")
            elif compliant_count / total_checks >= 0.4:
                compliance_info.append(f"   Avaliação Geral: REGULAR (≥40% conforme)")
            else:
                compliance_info.append(f"   Avaliação Geral: CRÍTICO (<40% conforme)")
        
        return "\n".join(compliance_info)
    
    def analyze_with_json_criterios(self, user_id: str = "anonymous") -> str:
        """Analisa conformidade usando critérios JSON"""
        self.audit_logger.log_access(user_id, "ANALYZE_JSON_CRITERIOS", "criterios", True)
        
        if not self.reports_data:
            return "ERRO: Nenhum relatório disponível para análise."
        
        # Carrega data.json se existir
        data_json_path = self.data_dir / "data.json"
        if not data_json_path.exists():
            return "ERRO: Arquivo data.json não encontrado na pasta data/"
        
        try:
            with open(data_json_path, 'r', encoding='utf-8') as f:
                data_json = json.load(f)
        except Exception as e:
            return f"ERRO: Erro ao carregar data.json: {e}"
        
        # Gera relatório usando o CriteriosManager
        compliance_report = self.criterios_manager.generate_compliance_report(data_json)
        
        return compliance_report
    
    def process_message(self, message: str, user_id: str = "anonymous") -> str:
        """Processa mensagens do usuário e retorna resposta apropriada com validações de segurança"""
        # Log de auditoria
        self.audit_logger.log_access(user_id, "PROCESS_MESSAGE", "agent", True)
        
        if not message:
            self.audit_logger.log_security_event("EMPTY_MESSAGE", f"Mensagem vazia de {user_id}", "WARNING")
            return "ERRO: Mensagem vazia recebida."
        
        # Validações de segurança
        if not self.security_validator.validate_input_length(message):
            self.audit_logger.log_security_event("MESSAGE_TOO_LONG", f"Mensagem muito longa de {user_id}: {len(message)}", "WARNING")
            return "ERRO: Mensagem muito longa. Por favor, reduza o tamanho."
        
        # Sanitização da entrada
        sanitized_message = self.security_validator.sanitize_input(message)
        if sanitized_message != message:
            self.audit_logger.log_security_event("MESSAGE_SANITIZED", f"Mensagem sanitizada para {user_id}", "INFO")
        
        # Detecção de dados sensíveis
        sensitive_data = self.security_validator.detect_sensitive_data(sanitized_message)
        if sensitive_data:
            self.audit_logger.log_security_event("SENSITIVE_DATA_IN_MESSAGE", f"Dados sensíveis na mensagem de {user_id}", "WARNING")
            return "ERRO: Mensagem contém dados sensíveis. Por favor, remova informações pessoais."
        
        user_message = sanitized_message.lower().strip()
        
        # Comandos específicos do Feito Conferido
        if any(term in user_message for term in ['relatórios', 'reports', 'disponíveis', 'lista', 'listar']):
            self.audit_logger.log_access(user_id, "LIST_REPORTS", "reports", True)
            return self.get_available_reports()
        
        elif any(term in user_message for term in ['buscar', 'procurar', 'search', 'encontrar', 'pesquisar']):
            # Extrai termo de busca da mensagem
            query = sanitized_message
            for term in ['buscar', 'procurar', 'search', 'encontrar', 'pesquisar']:
                if term in user_message:
                    parts = user_message.split(term)
                    if len(parts) > 1:
                        query = parts[-1].strip()
                    break
            return self.search_in_reports(query, user_id)
        
        elif any(term in user_message for term in ['conformidade', 'compliance', 'análise', 'verificação', 'auditoria']):
            self.audit_logger.log_access(user_id, "ANALYZE_COMPLIANCE", "reports", True)
            return self.analyze_compliance()
        
        elif any(term in user_message for term in ['critérios json', 'criterios json', 'json criterios', 'análise json']):
            return self.analyze_with_json_criterios(user_id)
        
        else:
            self.audit_logger.log_access(user_id, "HELP_REQUEST", "agent", True)
            return f"""
Olá! Sou o Agente Feito Conferido no Vertex AI!

Tenho acesso a {len(self.reports_data)} relatórios de conformidade.

COMANDOS DISPONÍVEIS:
• "Quais relatórios estão disponíveis?"
• "Análise de conformidade"
• "Buscar [termo]"
• "Critérios JSON" - Análise usando critérios JSON

NOTA DE SEGURANÇA: Todas as interações são registradas para auditoria.
Não compartilhe informações pessoais ou sensíveis.

Como posso ajudar você hoje?
"""

# Instância global do agente
feito_conferido_adk_agent = FeitoConferidoADKAgent()

