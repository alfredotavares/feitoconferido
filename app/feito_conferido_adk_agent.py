"""
Agente Feito Conferido integrado com Google ADK
Compatível com agent-starter-pack e Vertex AI
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeitoConferidoADKAgent:
    """Agente Feito Conferido integrado com ADK"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.reports_data = self._load_reports()
        logger.info(f"FeitoConferidoADKAgent inicializado com {len(self.reports_data)} relatórios")
    
    def _load_reports(self) -> List[Dict[str, Any]]:
        """Carrega todos os relatórios JSON disponíveis"""
        reports = []
        if not self.data_dir.exists():
            logger.warning(f"Diretório {self.data_dir} não encontrado")
            return reports
            
        for json_file in self.data_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_source_file'] = json_file.name
                    reports.append(data)
                    logger.info(f"Carregado: {json_file.name}")
            except Exception as e:
                logger.error(f"Erro ao carregar {json_file}: {e}")
        
        return reports
    
    def get_available_reports(self) -> str:
        """Retorna lista de relatórios disponíveis"""
        if not self.reports_data:
            return "❌ Nenhum relatório encontrado na pasta data/"
        
        report_list = ["📊 **RELATÓRIOS FEITO CONFERIDO DISPONÍVEIS:**\n"]
        for i, report in enumerate(self.reports_data, 1):
            source = report.get('_source_file', f'report_{i}')
            timestamp = report.get('timestamp', 'N/A')
            
            # Conta status dos checks
            checks = report.get('checks', {})
            compliant = sum(1 for check in checks.values() if check.get('status') == 'COMPLIANT')
            partial = sum(1 for check in checks.values() if check.get('status') == 'PARTIAL')
            non_compliant = sum(1 for check in checks.values() if check.get('status') == 'NON-COMPLIANT')
            
            report_list.append(f"{i}. 📄 **{source}**")
            report_list.append(f"   📅 Data: {timestamp}")
            report_list.append(f"   ✅ Conformes: {compliant}")
            report_list.append(f"   ⚠️ Parciais: {partial}")
            report_list.append(f"   ❌ Não conformes: {non_compliant}\n")
        
        return "\n".join(report_list)
    
    def search_in_reports(self, query: str) -> str:
        """Busca informações nos relatórios baseado na query"""
        if not self.reports_data:
            return "❌ Nenhum relatório disponível para busca."
        
        if not query or len(query.strip()) < 2:
            return "❌ Por favor, forneça um termo de busca válido (mínimo 2 caracteres)."
        
        results = []
        query_lower = query.lower().strip()
        
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
                    
                    results.append(f"\n📄 **{source}** ({timestamp})")
                    results.append(f"🔍 **{check_name}**:")
                    results.append(f"   📊 Status: {status}")
                    
                    if issues:
                        results.append(f"   ⚠️ Issues: {', '.join(issues[:2])}")
                    
                    if recommendations:
                        results.append(f"   💡 Recomendações: {', '.join(recommendations[:2])}")
        
        if results:
            header = f"🔍 **RESULTADOS PARA '{query}' NO FEITO CONFERIDO:**\n"
            return header + "\n".join(results)
        else:
            return f"❌ Nenhum resultado encontrado para '{query}' nos relatórios do Feito Conferido"
    
    def analyze_compliance(self) -> str:
        """Analisa conformidade nos relatórios"""
        if not self.reports_data:
            return "❌ Nenhum relatório disponível para análise de conformidade."
        
        compliance_info = ["📊 **ANÁLISE DE CONFORMIDADE - FEITO CONFERIDO:**\n"]
        
        total_checks = 0
        compliant_count = 0
        partial_count = 0
        non_compliant_count = 0
        
        for report in self.reports_data:
            source = report.get('_source_file', 'unknown')
            timestamp = report.get('timestamp', 'N/A')
            checks = report.get('checks', {})
            
            compliance_info.append(f"\n📄 **{source}** ({timestamp}):")
            
            for check_name, check_data in checks.items():
                status = check_data.get('status', 'N/A')
                total_checks += 1
                
                if status == 'COMPLIANT':
                    compliant_count += 1
                    compliance_info.append(f"   ✅ {check_name}: {status}")
                elif status == 'PARTIAL':
                    partial_count += 1
                    compliance_info.append(f"   ⚠️ {check_name}: {status}")
                elif status == 'NON-COMPLIANT':
                    non_compliant_count += 1
                    compliance_info.append(f"   ❌ {check_name}: {status}")
                else:
                    compliance_info.append(f"   ❓ {check_name}: {status}")
                
                # Adiciona issues se houver
                issues = check_data.get('issues', [])
                if issues:
                    compliance_info.append(f"      🔸 Issues: {', '.join(issues[:1])}")
        
        # Adiciona resumo estatístico
        if total_checks > 0:
            compliance_info.append(f"\n📈 **RESUMO ESTATÍSTICO FEITO CONFERIDO:**")
            compliance_info.append(f"   📊 Total de verificações: {total_checks}")
            compliance_info.append(f"   ✅ Conformes: {compliant_count} ({(compliant_count/total_checks*100):.1f}%)")
            compliance_info.append(f"   ⚠️ Parciais: {partial_count} ({(partial_count/total_checks*100):.1f}%)")
            compliance_info.append(f"   ❌ Não conformes: {non_compliant_count} ({(non_compliant_count/total_checks*100):.1f}%)")
            
            # Avaliação geral
            if compliant_count / total_checks >= 0.8:
                compliance_info.append(f"   🎯 **Avaliação Geral: EXCELENTE** (≥80% conforme)")
            elif compliant_count / total_checks >= 0.6:
                compliance_info.append(f"   🎯 **Avaliação Geral: BOM** (≥60% conforme)")
            elif compliant_count / total_checks >= 0.4:
                compliance_info.append(f"   🎯 **Avaliação Geral: REGULAR** (≥40% conforme)")
            else:
                compliance_info.append(f"   🎯 **Avaliação Geral: CRÍTICO** (<40% conforme)")
        
        return "\n".join(compliance_info)
    
    def process_message(self, message: str) -> str:
        """Processa mensagens do usuário e retorna resposta apropriada"""
        if not message:
            return "❌ Mensagem vazia recebida."
        
        user_message = message.lower().strip()
        
        # Comandos específicos do Feito Conferido
        if any(term in user_message for term in ['relatórios', 'reports', 'disponíveis', 'lista', 'listar']):
            return self.get_available_reports()
        
        elif any(term in user_message for term in ['buscar', 'procurar', 'search', 'encontrar', 'pesquisar']):
            # Extrai termo de busca da mensagem
            query = message
            for term in ['buscar', 'procurar', 'search', 'encontrar', 'pesquisar']:
                if term in user_message:
                    parts = user_message.split(term)
                    if len(parts) > 1:
                        query = parts[-1].strip()
                    break
            return self.search_in_reports(query)
        
        elif any(term in user_message for term in ['conformidade', 'compliance', 'análise', 'verificação', 'auditoria']):
            return self.analyze_compliance()
        
        else:
            return f"""
👋 **Olá! Sou o Agente Feito Conferido no Vertex AI!**

Tenho acesso a **{len(self.reports_data)} relatórios** de conformidade.

💬 **Comandos disponíveis:**
• "Quais relatórios estão disponíveis?"
• "Análise de conformidade"
• "Buscar [termo]"

Como posso ajudar você hoje?
"""

# Instância global do agente
feito_conferido_adk_agent = FeitoConferidoADKAgent()
