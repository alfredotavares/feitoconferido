"""
Agente Conferido integrado com Google ADK
Baseado no FeitoConferidoADKAgent, adaptado para arquitetura de software
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import structlog
from app.utils.security_validator import SecurityValidator, AuditLogger, RateLimiter, SessionManager

# Configuração de logs estruturados
logger = structlog.get_logger("conferido_adk_agent")

class ConferidoADKAgent:
    """Agente Conferido integrado com ADK para validação de arquitetura"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.criterios_file = Path("criterios_arquitetura.json")
        self.aprovacoes_data = self._load_aprovacoes()
        self.criterios_data = self._load_criterios()
        
        # Componentes de segurança
        self.security_validator = SecurityValidator()
        self.audit_logger = AuditLogger()
        self.rate_limiter = RateLimiter()
        self.session_manager = SessionManager()
        
        logger.info(
            "conferido_agent_initialized",
            aprovacoes_count=len(self.aprovacoes_data),
            criterios_count=len(self.criterios_data)
        )
    
    def _load_aprovacoes(self) -> List[Dict[str, Any]]:
        """Carrega todas as aprovações JSON disponíveis"""
        aprovacoes = []
        if not self.data_dir.exists():
            logger.warning("data_directory_not_found", path=str(self.data_dir))
            return aprovacoes
            
        for json_file in self.data_dir.glob("*.json"):
            try:
                # Validação de segurança do arquivo
                if not self.security_validator.validate_file_path(str(json_file)):
                    logger.error("file_path_security_violation", file=str(json_file))
                    continue
                
                if not self.security_validator.validate_file_size(str(json_file)):
                    logger.error("file_size_exceeded", file=str(json_file))
                    continue
                
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Validação da estrutura
                    is_valid, error_msg = self.security_validator.validate_json_structure(data, "aprovacao")
                    if not is_valid:
                        logger.error("invalid_json_structure", file=str(json_file), error=error_msg)
                        continue
                    
                    data['_source_file'] = json_file.name
                    data['_file_hash'] = self.security_validator.generate_hash(json.dumps(data, sort_keys=True))
                    aprovacoes.append(data)
                    
                    logger.info("aprovacao_loaded", file=json_file.name, ciclo=data.get('ciclo_desenvolvimento'))
                    
            except Exception as e:
                logger.error("load_aprovacao_error", file=str(json_file), error=str(e))
        
        return aprovacoes
    
    def _load_criterios(self) -> Dict[str, str]:
        """Carrega critérios de arquitetura"""
        if not self.criterios_file.exists():
            logger.error("criterios_file_not_found", file=str(self.criterios_file))
            return {}
        
        try:
            with open(self.criterios_file, 'r', encoding='utf-8') as f:
                criterios = json.load(f)
                logger.info("criterios_loaded", count=len(criterios))
                return criterios
        except Exception as e:
            logger.error("criterios_load_error", error=str(e))
            return {}
    
    def get_available_evaluations(self, user_id: str = "anonymous") -> str:
        """Retorna lista de aprovações disponíveis"""
        # Rate limiting
        allowed, message = self.rate_limiter.is_allowed(user_id)
        if not allowed:
            self.audit_logger.log_security_event("RATE_LIMIT_EXCEEDED", message, user_id=user_id)
            return f"ERRO: {message}"
        
        # Log de acesso
        self.audit_logger.log_access(user_id, "GET_EVALUATIONS", "aprovacoes", True)
        
        if not self.aprovacoes_data:
            return "❌ Nenhuma aprovação encontrada na pasta data/"
        
        evaluation_list = ["📊 **APROVAÇÕES DE ARQUITETURA DISPONÍVEIS:**\n"]
        
        for i, aprovacao in enumerate(self.aprovacoes_data, 1):
            source = aprovacao.get('_source_file', f'aprovacao_{i}')
            ciclo = aprovacao.get('ciclo_desenvolvimento', 'N/A')
            arquiteto = aprovacao.get('arquiteto_responsavel', 'N/A')
            parecer = aprovacao.get('parecer_final', 'N/A')
            componentes_count = len(aprovacao.get('componentes', []))
            
            evaluation_list.append(f"**{i}. {source}**")
            evaluation_list.append(f"   📋 Ciclo: {ciclo}")
            evaluation_list.append(f"   👤 Arquiteto: {arquiteto}")
            evaluation_list.append(f"   📦 Componentes: {componentes_count}")
            evaluation_list.append(f"   🎯 Parecer: {parecer}")
            evaluation_list.append("")
        
        evaluation_list.append("💡 **Comandos disponíveis:**")
        evaluation_list.append("• 'Análise de conformidade' - Análise completa")
        evaluation_list.append("• 'Buscar [termo]' - Busca específica")
        evaluation_list.append("• 'Débitos técnicos' - Análise de issues")
        evaluation_list.append("• 'Componentes' - Lista componentes")
        evaluation_list.append("• 'Critérios' - Mostra critérios")
        
        return "\n".join(evaluation_list)
    
    def search_in_evaluations(self, query: str, user_id: str = "anonymous") -> str:
        """Busca nas aprovações com validações de segurança"""
        import time
        start_time = time.time()
        
        # Rate limiting
        allowed, message = self.rate_limiter.is_allowed(user_id)
        if not allowed:
            return f"ERRO: {message}"
        
        # Validações de segurança
        if not self.security_validator.validate_input_length(query):
            self.audit_logger.log_security_event("QUERY_TOO_LONG", f"Query length: {len(query)}", user_id=user_id)
            return "ERRO: Consulta muito longa. Limite de 1000 caracteres."
        
        # Sanitização
        query_sanitized = self.security_validator.sanitize_input(query)
        
        # Detecção de dados sensíveis
        sensitive_data = self.security_validator.detect_sensitive_data(query_sanitized)
        if sensitive_data:
            self.audit_logger.log_security_event("SENSITIVE_DATA_IN_QUERY", f"Tipos: {sensitive_data}", user_id=user_id)
            return "ERRO: Consulta contém dados sensíveis. Remova informações pessoais."
        
        # Log de acesso
        self.audit_logger.log_access(user_id, "SEARCH", "aprovacoes", True, query_hash=self.security_validator.generate_hash(query_sanitized)[:16])
        
        if not self.aprovacoes_data:
            return "❌ Nenhuma aprovação disponível para busca"
        
        query_lower = query_sanitized.lower()
        results = []
        
        for aprovacao in self.aprovacoes_data:
            # Busca em campos principais
            fields_to_search = [
                aprovacao.get('titulo', ''),
                aprovacao.get('ciclo_desenvolvimento', ''),
                aprovacao.get('arquiteto_responsavel', ''),
                aprovacao.get('parecer_final', ''),
                ' '.join(aprovacao.get('componentes', [])),
                ' '.join(aprovacao.get('issues_debito_tecnico', []))
            ]
            
            # Busca em validação
            validacao = aprovacao.get('validacao', {})
            for criterio_data in validacao.values():
                if isinstance(criterio_data, dict):
                    fields_to_search.extend([
                        criterio_data.get('resposta', ''),
                        criterio_data.get('comentario', '')
                    ])
            
            # Verifica se a query está em algum campo
            content = ' '.join(fields_to_search).lower()
            if query_lower in content:
                results.append(aprovacao)
        
        execution_time = time.time() - start_time
        self.audit_logger.log_query_analysis(query_sanitized, len(results), execution_time, user_id=user_id)
        
        if not results:
            return f"❌ Nenhum resultado encontrado para: '{query_sanitized}'"
        
        # Formata resultados
        response = [f"🔍 **RESULTADOS DA BUSCA:** '{query_sanitized}'\n"]
        response.append(f"📊 Encontradas {len(results)} aprovação(ões)\n")
        
        for i, aprovacao in enumerate(results, 1):
            source = aprovacao.get('_source_file', f'aprovacao_{i}')
            ciclo = aprovacao.get('ciclo_desenvolvimento', 'N/A')
            arquiteto = aprovacao.get('arquiteto_responsavel', 'N/A')
            parecer = aprovacao.get('parecer_final', 'N/A')
            
            response.append(f"**{i}. {source}**")
            response.append(f"   📋 Ciclo: {ciclo}")
            response.append(f"   👤 Arquiteto: {arquiteto}")
            response.append(f"   🎯 Parecer: {parecer}")
            
            # Mostra componentes relevantes
            componentes = aprovacao.get('componentes', [])
            componentes_relevantes = [c for c in componentes if query_lower in c.lower()]
            if componentes_relevantes:
                response.append(f"   📦 Componentes relevantes: {', '.join(componentes_relevantes)}")
            
            # Mostra issues relevantes
            issues = aprovacao.get('issues_debito_tecnico', [])
            issues_relevantes = [i for i in issues if query_lower in i.lower()]
            if issues_relevantes:
                response.append(f"   🚨 Issues relevantes: {', '.join(issues_relevantes)}")
            
            response.append("")
        
        return "\n".join(response)
    
    def analyze_compliance(self, query: str = "", user_id: str = "anonymous") -> str:
        """Analisa conformidade com validações de segurança"""
        # Rate limiting
        allowed, message = self.rate_limiter.is_allowed(user_id)
        if not allowed:
            return f"ERRO: {message}"
        
        # Validações de segurança
        if not self.security_validator.validate_input_length(query):
            return "ERRO: Consulta muito longa. Limite de 1000 caracteres."
        
        query_sanitized = self.security_validator.sanitize_input(query)
        
        # Detecção de dados sensíveis
        sensitive_data = self.security_validator.detect_sensitive_data(query_sanitized)
        if sensitive_data:
            self.audit_logger.log_security_event("SENSITIVE_DATA_IN_QUERY", f"Tipos: {sensitive_data}", user_id=user_id)
            return "ERRO: Consulta contém dados sensíveis. Remova informações pessoais."
        
        # Log de acesso
        self.audit_logger.log_access(user_id, "ANALYZE_COMPLIANCE", "arquitetura", True, query_hash=self.security_validator.generate_hash(query_sanitized)[:16])
        
        if not self.aprovacoes_data:
            return "❌ Nenhuma aprovação encontrada"
        
        if not self.criterios_data:
            return "❌ Critérios não encontrados"
        
        # Análise de conformidade
        result = ["📊 **ANÁLISE DE CONFORMIDADE - ARQUITETURA DE SOFTWARE**\n"]
        
        total_aprovacoes = len(self.aprovacoes_data)
        total_criterios = len(self.criterios_data)
        
        # Estatísticas gerais
        pareceres_count = {}
        total_conformidade = 0
        aprovacoes_com_debito = 0
        total_issues = 0
        
        for aprovacao in self.aprovacoes_data:
            parecer = aprovacao.get('parecer_final', 'N/A')
            pareceres_count[parecer] = pareceres_count.get(parecer, 0) + 1
            
            # Conta débitos
            issues = aprovacao.get('issues_debito_tecnico', [])
            if issues:
                aprovacoes_com_debito += 1
                total_issues += len(issues)
            
            # Calcula conformidade
            validacao = aprovacao.get('validacao', {})
            conformes = sum(1 for v in validacao.values() if isinstance(v, dict) and v.get('resposta', '').lower() == 'sim')
            total_validacoes = len(validacao)
            
            if total_validacoes > 0:
                conformidade = conformes / total_validacoes * 100
                total_conformidade += conformidade
        
        # Conformidade média
        conformidade_media = total_conformidade / total_aprovacoes if total_aprovacoes > 0 else 0
        
        result.append(f"📈 **ESTATÍSTICAS GERAIS:**")
        result.append(f"   • Aprovações analisadas: {total_aprovacoes}")
        result.append(f"   • Critérios avaliados: {total_criterios}")
        result.append(f"   • Conformidade média: {conformidade_media:.1f}%")
        result.append(f"   • Aprovações com débito: {aprovacoes_com_debito}/{total_aprovacoes}")
        result.append(f"   • Total de issues: {total_issues}")
        result.append("")
        
        # Distribuição por parecer
        result.append("🎯 **DISTRIBUIÇÃO POR PARECER:**")
        for parecer, count in pareceres_count.items():
            percentage = count / total_aprovacoes * 100
            result.append(f"   • {parecer}: {count} ({percentage:.1f}%)")
        result.append("")
        
        # Análise por critério
        result.append("📋 **CONFORMIDADE POR CRITÉRIO:**")
        for criterio_id, criterio_desc in self.criterios_data.items():
            sim_count = 0
            nao_count = 0
            na_count = 0
            
            for aprovacao in self.aprovacoes_data:
                validacao = aprovacao.get('validacao', {})
                if criterio_id in validacao:
                    resposta = validacao[criterio_id].get('resposta', '').lower()
                    if resposta == 'sim':
                        sim_count += 1
                    elif resposta == 'não':
                        nao_count += 1
                    elif resposta == 'não se aplica':
                        na_count += 1
            
            total_respostas = sim_count + nao_count + na_count
            if total_respostas > 0:
                conformidade = sim_count / total_respostas * 100
                emoji = '✅' if conformidade >= 80 else '⚠️' if conformidade >= 50 else '❌'
                result.append(f"{emoji} {criterio_id.replace('_', ' ').title()}: {conformidade:.1f}% ({sim_count}/{total_respostas})")
        
        result.append("")
        
        # Issues críticos
        if total_issues > 0:
            result.append("🚨 **ISSUES DE DÉBITO TÉCNICO:**")
            for aprovacao in self.aprovacoes_data:
                issues = aprovacao.get('issues_debito_tecnico', [])
                if issues:
                    ciclo = aprovacao.get('ciclo_desenvolvimento', 'N/A')
                    result.append(f"   • Ciclo {ciclo}: {', '.join(issues)}")
            result.append("")
        
        # Recomendações
        result.append("💡 **RECOMENDAÇÕES:**")
        if conformidade_media < 70:
            result.append("   • Conformidade baixa - revisar implementação dos critérios")
        if aprovacoes_com_debito > total_aprovacoes * 0.3:
            result.append("   • Alto número de débitos técnicos - priorizar resolução")
        if nao_count > sim_count:
            result.append("   • Muitos critérios não conformes - revisar arquitetura")
        
        # Mascara dados sensíveis na resposta
        response_text = "\n".join(result)
        response_masked = self.security_validator.mask_sensitive_data(response_text)
        
        return response_masked
    
    def process_message(self, message: str, user_id: str = "anonymous", session_id: str = None) -> str:
        """Processa mensagem do usuário com validações completas"""
        # Validação de sessão
        if session_id:
            session_valid, session_msg = self.session_manager.validate_session(session_id)
            if not session_valid:
                return f"ERRO: {session_msg}"
        
        # Rate limiting
        allowed, rate_msg = self.rate_limiter.is_allowed(user_id)
        if not allowed:
            self.audit_logger.log_security_event("RATE_LIMIT_EXCEEDED", rate_msg, user_id=user_id)
            return f"ERRO: {rate_msg}"
        
        # Validações básicas
        if not message or not message.strip():
            return "ERRO: Mensagem vazia"
        
        if not self.security_validator.validate_input_length(message):
            self.audit_logger.log_security_event("MESSAGE_TOO_LONG", f"Length: {len(message)}", user_id=user_id)
            return "ERRO: Mensagem muito longa. Limite de 1000 caracteres."
        
        # Sanitização
        message_sanitized = self.security_validator.sanitize_input(message)
        
        # Detecção de dados sensíveis
        sensitive_data = self.security_validator.detect_sensitive_data(message_sanitized)
        if sensitive_data:
            self.audit_logger.log_security_event("SENSITIVE_DATA_IN_MESSAGE", f"Tipos: {sensitive_data}", user_id=user_id)
            return "ERRO: Mensagem contém dados sensíveis. Remova informações pessoais."
        
        # Log da mensagem
        self.audit_logger.log_access(user_id, "PROCESS_MESSAGE", "conferido", True, 
                                   message_hash=self.security_validator.generate_hash(message_sanitized)[:16])
        
        # Processamento da mensagem
        message_lower = message_sanitized.lower()
        
        try:
            if any(term in message_lower for term in ['aprovações', 'aprovacoes', 'disponíveis', 'disponiveis', 'lista']):
                return self.get_available_evaluations(user_id)
            
            elif any(term in message_lower for term in ['análise', 'analise', 'conformidade']):
                return self.analyze_compliance(message_sanitized, user_id)
            
            elif any(term in message_lower for term in ['buscar', 'procurar', 'encontrar']):
                # Remove comando da busca
                query = message_sanitized
                for cmd in ['buscar', 'procurar', 'encontrar']:
                    query = query.replace(cmd, '').strip()
                return self.search_in_evaluations(query, user_id)
            
            elif any(term in message_lower for term in ['débito', 'debito', 'issue']):
                return self.search_in_evaluations('débito técnico', user_id)
            
            elif 'componentes' in message_lower:
                return self.search_in_evaluations('componentes', user_id)
            
            elif any(term in message_lower for term in ['critério', 'criterio']):
                criterios_list = ["📋 **CRITÉRIOS DE ARQUITETURA:**\n"]
                for criterio_id, criterio_desc in self.criterios_data.items():
                    criterios_list.append(f"• **{criterio_id.replace('_', ' ').title()}**")
                    criterios_list.append(f"  {criterio_desc}")
                    criterios_list.append("")
                return "\n".join(criterios_list)
            
            else:
                # Busca geral
                return self.search_in_evaluations(message_sanitized, user_id)
                
        except Exception as e:
            logger.error("message_processing_error", error=str(e), user_id=user_id)
            self.audit_logger.log_security_event("PROCESSING_ERROR", str(e), "ERROR", user_id=user_id)
            return "ERRO: Falha no processamento da mensagem. Tente novamente."

# Instância global do agente
conferido_agent = ConferidoADKAgent()

