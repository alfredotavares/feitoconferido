def format_report_output(self, relatorio: Dict[str, Any]) -> str:
        """Formata relatório para saída legível com detalhes do Jira"""
        if "erro" in relatorio:
            return f"ERRO: {relatorio['erro']}"
        
        output = []
        output.append("=" * 100)
        output.append("📊 RELATÓRIO DETALHADO DE CONFORMIDADE DE COMPONENTES")
        output.append("=" * 100)
        
        # Metadados
        metadata = relatorio["metadata"]
        output.append(f"🆔 ID: {metadata['id']}")
        output.append(f"📅 Data: {metadata['timestamp'][:19].replace('T', ' ')}")
        output.append(f"🤖 Gerado por: {metadata['gerado_por']}")
        output.append(f"📊 Componentes analisados: {metadata['total_componentes_analisados']}")
        output.append("")
        
        # Fontes integradas
        fontes = metadata['fontes_integradas']
        output.append("🔗 FONTES INTEGRADAS:")
        output.append(f"   📋 Confluence: {fontes['confluence']}")
        output.append(f"   🎫 Jira: {fontes['jira']}")
        output.append(f"   🏛️ PortalTech: {fontes['portaltech']}")
        output.append("")
        
        # Resumo executivo
        resumo = relatorio["resumo_executivo"]
        output.append("📈 RESUMO EXECUTIVO:")
        output.append(f"   🎯 Conformidade média: {resumo['conformidade_media_geral']}%")
        output.append(f"   🎫 Issues críticas: {resumo['issues_criticas']}")
        output.append(f"   📋 Issues abertas: {resumo['issues_abertas']}")
        output.append(f"   🚦 Status do release: {resumo['status_release']}")
        output.append(f"   ⚠️ Risco de produção: {resumo['risco_producao']}")
        output.append(f"   🏆 PARECER GERAL: {resumo['parecer_geral']}")
        output.append("")
        
        # Distribuição por classificação
        if resumo.get('distribuicao_classificacoes'):
            output.append("📊 DISTRIBUIÇÃO POR CLASSIFICAÇÃO:")
            for classificacao, quantidade in resumo['distribuicao_classificacoes'].items():
                emoji = {"EXCELENTE": "🟢", "BOM": "🔵", "REGULAR": "🟡", "INSUFICIENTE": "🟠", "CRÍTICO": "🔴"}.get(classificacao, "⚪")
                output.append(f"   {emoji} {classificacao}: {quantidade} componente(s)")
            output.append("")
        
        # Análise detalhada por componente
        output.append("🔍 ANÁLISE DETALHADA POR COMPONENTE:")
        output.append("=" * 100)
        
        for nome, dados in relatorio["componentes"].items():
            output.append(f"\n📦 COMPONENTE: {nome}")
            output.append("-" * 80)
            
            # Informações básicas
            info = dados["informacoes_basicas"]
            output.append(f"   📊 Versão: {info['versao_anterior']} → {info['versao_atual']} ({info['tipo_mudanca']})")
            
            # Score final
            score = dados["score_final"]
            emoji_score = {"EXCELENTE": "🟢", "BOM": "🔵", "REGULAR": "🟡", "INSUFICIENTE": "🟠", "CRÍTICO": "🔴"}.get(score['classificacao'], "⚪")
            output.append(f"   {emoji_score} Score Final: {score['score_final']:.1f}% ({score['classificacao']})")
            output.append(f"   📋 Conformidade: {score['score_conformidade']:.1f}% | Penalidade Jira: -{score['penalidade_jira']} pontos")
            
            # Dados do PortalTech
            portaltech = dados["dados_portaltech"]
            if portaltech['aprovacao_relacionada']:
                output.append(f"   🏛️ PortalTech: {portaltech['aprovacao_relacionada']} | Arquiteto: {portaltech['arquiteto_responsavel']}")
                output.append(f"   📝 Status Aprovação: {portaltech# component_validator.py
"""
Validador de Componentes - Script Independente
Localização: app/component_validator.py

Emula integração com:
- Confluence: Critérios de arquitetura
- Jira: Issues de débito técnico
- PortalTech: Aprovações e dados de conformidade

Uso:
    from app.component_validator import ComponentReportEmulator
    
    emulator = ComponentReportEmulator()
    relatorio = emulator.generate_component_report(component_list)
    print(emulator.format_report_output(relatorio))
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class ComponentReportEmulator:
    """
    Emulador independente de relatórios de componentes
    Simula dados do Confluence, Jira e PortalTech
    """
    
    def __init__(self):
        """Inicializa com dados simulados das três fontes"""
        self.confluence_criterios = self._load_confluence_mock()
        self.jira_issues = self._load_jira_mock()
        self.portaltech_data = self._load_portaltech_mock()
        
        print("✅ ComponentReportEmulator inicializado")
        print(f"   📋 Critérios Confluence: {len(self.confluence_criterios)}")
        print(f"   🎫 Issues Jira: {len(self.jira_issues)}")
        print(f"   🏛️ Dados PortalTech: {len(self.portaltech_data)}")
    
    def _load_confluence_mock(self) -> Dict[str, Dict]:
        """
        MOCK - Confluence: Critérios de Arquitetura
        Simula dados vindos do Confluence via API
        """
        return {
            "seguranca_autenticacao": {
                "id": "CONF-SEC-001",
                "pergunta": "Componente implementa autenticação segura (OAuth2/JWT)?",
                "categoria": "Segurança",
                "peso": 10,
                "obrigatorio": True,
                "fonte": "confluence://wiki/criterios-arquitetura/seguranca",
                "descricao": "Todo componente deve implementar autenticação segura seguindo padrões OAuth2 ou JWT",
                "referencias": ["RFC 6749", "RFC 7519"]
            },
            "padrao_logging": {
                "id": "CONF-OBS-001", 
                "pergunta": "Componente implementa logging estruturado?",
                "categoria": "Observabilidade",
                "peso": 8,
                "obrigatorio": True,
                "fonte": "confluence://wiki/padrao-logging",
                "descricao": "Logs devem ser estruturados (JSON) com níveis apropriados",
                "referencias": ["ELK Stack Guidelines", "Structured Logging Best Practices"]
            },
            "documentacao_api": {
                "id": "CONF-DOC-001",
                "pergunta": "Componente possui documentação OpenAPI/Swagger atualizada?",
                "categoria": "Documentação", 
                "peso": 6,
                "obrigatorio": False,
                "fonte": "confluence://wiki/padrao-documentacao-api",
                "descricao": "APIs devem ter documentação OpenAPI/Swagger sempre atualizada",
                "referencias": ["OpenAPI 3.0 Specification"]
            },
            "testes_unitarios": {
                "id": "CONF-QUA-001",
                "pergunta": "Componente possui cobertura de testes >= 80%?",
                "categoria": "Qualidade",
                "peso": 9,
                "obrigatorio": True, 
                "fonte": "confluence://wiki/padrao-testes-qualidade",
                "descricao": "Cobertura mínima de testes unitários deve ser 80%",
                "referencias": ["SonarQube Quality Gates", "Jest Coverage Reports"]
            },
            "performance_sla": {
                "id": "CONF-PER-001",
                "pergunta": "Componente atende SLA de performance (response time < 200ms)?",
                "categoria": "Performance",
                "peso": 7,
                "obrigatorio": False,
                "fonte": "confluence://wiki/sla-performance-apis",
                "descricao": "APIs devem responder em menos de 200ms para 95% das requisições",
                "referencias": ["SLA Dashboard", "New Relic Monitoring"]
            },
            "seguranca_vulnerabilidades": {
                "id": "CONF-SEC-002",
                "pergunta": "Componente está livre de vulnerabilidades críticas?",
                "categoria": "Segurança",
                "peso": 10,
                "obrigatorio": True,
                "fonte": "confluence://wiki/security-scanning",
                "descricao": "Scan de segurança não deve apresentar vulnerabilidades críticas",
                "referencias": ["OWASP Top 10", "Snyk Security Reports"]
            }
        }
    
    def _load_jira_mock(self) -> List[Dict]:
        """
        MOCK - Jira: Issues de Débito Técnico
        Simula dados vindos do Jira via REST API
        
        ADICIONE MAIS ISSUES AQUI - Basta copiar e modificar o padrão
        """
        return [
            {
                "key": "TECH-001",
                "componente": "caapi-hubd-base-avaliacao-v1",
                "summary": "Implementar rate limiting na API de avaliação",
                "description": "API está sem controle de rate limiting, causando possível sobrecarga",
                "status": "Em Aberto",
                "priority": "Alta",
                "severity": "Major",
                "labels": ["security", "performance", "tech-debt"],
                "assignee": "dev.backend@company.com",
                "reporter": "architect@company.com", 
                "created": "2024-12-10T09:15:00Z",
                "updated": "2024-12-15T14:30:00Z",
                "fonte": "jira://browse/TECH-001",
                "impacto": "Segurança e Performance",
                "estimativa": "5 story points"
            },
            # 🆕 ADICIONE NOVAS ISSUES AQUI - EXEMPLO:
            {
                "key": "TECH-007",
                "componente": "caapi-hubd-base-avaliacao-v1",
                "summary": "Implementar cache Redis para melhor performance",
                "description": "Consultas ao banco estão lentas, implementar cache Redis",
                "status": "Backlog",
                "priority": "Média",
                "severity": "Minor",
                "labels": ["performance", "cache", "enhancement"],
                "assignee": "dev.backend@company.com",
                "reporter": "performance.team@company.com",
                "created": "2024-12-17T10:00:00Z",
                "updated": "2024-12-17T10:00:00Z",
                "fonte": "jira://browse/TECH-007",
                "impacto": "Performance",
                "estimativa": "8 story points"
            },
            {
                "key": "TECH-008",
                "componente": "novo-componente-exemplo",
                "summary": "Configurar CI/CD pipeline",
                "description": "Novo componente precisa de pipeline de deploy automatizado",
                "status": "Em Progresso",
                "priority": "Alta",
                "severity": "Major",
                "labels": ["devops", "ci-cd", "automation"],
                "assignee": "devops.team@company.com",
                "reporter": "tech.lead@company.com",
                "created": "2024-12-16T14:30:00Z",
                "updated": "2024-12-17T09:15:00Z",
                "fonte": "jira://browse/TECH-008",
                "impacto": "DevOps",
                "estimativa": "13 story points"
            },
            {
                "key": "TECH-002",
                "componente": "caapi-hubd-base-avaliacao-v1", 
                "summary": "Atualizar dependências com vulnerabilidades",
                "description": "Scan de segurança detectou 3 dependências com vulnerabilidades médias",
                "status": "Em Progresso",
                "priority": "Média",
                "severity": "Minor",
                "labels": ["security", "dependencies", "maintenance"],
                "assignee": "security.team@company.com",
                "reporter": "sonarqube@company.com",
                "created": "2024-12-08T16:45:00Z", 
                "updated": "2024-12-16T10:20:00Z",
                "fonte": "jira://browse/TECH-002",
                "impacto": "Segurança",
                "estimativa": "3 story points"
            },
            {
                "key": "TECH-003",
                "componente": "flutmicro-hubd-base-app-rating",
                "summary": "Melhorar logging estruturado",
                "description": "Logs não estão seguindo padrão estruturado definido pela arquitetura",
                "status": "Resolvido",
                "priority": "Baixa",
                "severity": "Trivial", 
                "labels": ["observability", "logging", "compliance"],
                "assignee": "dev.frontend@company.com",
                "reporter": "sre.team@company.com",
                "created": "2024-11-25T11:30:00Z",
                "updated": "2024-12-14T15:45:00Z",
                "resolved": "2024-12-14T15:45:00Z",
                "fonte": "jira://browse/TECH-003",
                "impacto": "Observabilidade",
                "estimativa": "2 story points"
            },
            {
                "key": "TECH-004",
                "componente": "flutmicro-hubd-base-app-rating",
                "summary": "Performance degradada - response time alto",
                "description": "API está respondendo em média 350ms, acima do SLA de 200ms",
                "status": "Em Aberto",
                "priority": "Crítica",
                "severity": "Critical",
                "labels": ["performance", "sla-breach", "urgent"],
                "assignee": "performance.team@company.com", 
                "reporter": "monitoring@company.com",
                "created": "2024-12-16T08:00:00Z",
                "updated": "2024-12-16T08:00:00Z",
                "fonte": "jira://browse/TECH-004",
                "impacto": "Performance - SLA Breach",
                "estimativa": "8 story points"
            },
            {
                "key": "TECH-005",
                "componente": "ng15-hubd-base-portal-configuracao",
                "summary": "Cobertura de testes abaixo do mínimo",
                "description": "Cobertura atual de 45%, abaixo do mínimo exigido de 80%",
                "status": "Em Aberto", 
                "priority": "Alta",
                "severity": "Major",
                "labels": ["testing", "quality", "coverage"],
                "assignee": "qa.team@company.com",
                "reporter": "sonarqube@company.com",
                "created": "2024-12-12T13:20:00Z",
                "updated": "2024-12-15T09:10:00Z",
                "fonte": "jira://browse/TECH-005",
                "impacto": "Qualidade",
                "estimativa": "13 story points"
            },
            {
                "key": "TECH-006",
                "componente": "ng15-hubd-base-portal-configuracao",
                "summary": "Documentação de componentes desatualizada",
                "description": "Storybook com componentes sem documentação há 6 meses",
                "status": "Em Aberto",
                "priority": "Baixa", 
                "severity": "Minor",
                "labels": ["documentation", "maintenance", "storybook"],
                "assignee": "dev.frontend@company.com",
                "reporter": "product.owner@company.com",
                "created": "2024-12-05T14:15:00Z",
                "updated": "2024-12-10T16:30:00Z",
                "fonte": "jira://browse/TECH-006",
                "impacto": "Documentação",
                "estimativa": "5 story points"
            }
        ]
    
    def _load_portaltech_mock(self) -> List[Dict]:
        """
        MOCK - PortalTech: Dados de Aprovação e Conformidade
        Simula dados vindos do PortalTech via API
        """
        return [
            {
                "id": "PTC-2024-Q4-001",
                "ciclo_aprovacao": "2024-Q4-RELEASE-12",
                "arquiteto_responsavel": "Alfredo Tavares",
                "data_aprovacao": "2024-12-15T10:30:00Z",
                "data_atualizacao": "2024-12-16T09:15:00Z",
                "status": "APROVADO_COM_RESSALVAS",
                "fonte": "portaltech://aprovacoes/PTC-2024-Q4-001",
                "componentes_escopo": [
                    "caapi-hubd-base-avaliacao-v1",
                    "flutmicro-hubd-base-app-rating", 
                    "ng15-hubd-base-portal-configuracao"
                ],
                "historico_versoes": {
                    "caapi-hubd-base-avaliacao-v1": {
                        "versao_anterior": "1.2.8",
                        "versao_nova": "1.3.2",
                        "tipo_mudanca": "MINOR_UPDATE",
                        "breaking_changes": False
                    },
                    "flutmicro-hubd-base-app-rating": {
                        "versao_anterior": "1.9.5", 
                        "versao_nova": "2.0.1",
                        "tipo_mudanca": "MAJOR_UPDATE",
                        "breaking_changes": True
                    },
                    "ng15-hubd-base-portal-configuracao": {
                        "versao_anterior": "1.0.9",
                        "versao_nova": "1.1.1", 
                        "tipo_mudanca": "MINOR_UPDATE",
                        "breaking_changes": False
                    }
                },
                "metricas_conformidade": {
                    "score_geral": 78.5,
                    "criterios_atendidos": 18,
                    "criterios_nao_atendidos": 4,
                    "criterios_nao_aplicaveis": 3,
                    "issues_criticas_abertas": 1,
                    "issues_totais": 6
                },
                "observacoes": [
                    "Componente flutmicro-hubd-base-app-rating apresenta issue crítica de performance",
                    "ng15-hubd-base-portal-configuracao precisa melhorar cobertura de testes",
                    "Todos os componentes aprovados para produção com monitoramento reforçado"
                ],
                "proxima_revisao": "2025-01-15T10:00:00Z"
            },
            {
                "id": "PTC-2024-Q3-045",
                "ciclo_aprovacao": "2024-Q3-RELEASE-09", 
                "arquiteto_responsavel": "Maria Silva",
                "data_aprovacao": "2024-09-20T14:20:00Z",
                "status": "APROVADO",
                "fonte": "portaltech://aprovacoes/PTC-2024-Q3-045",
                "componentes_escopo": [
                    "caapi-hubd-base-avaliacao-v1"
                ],
                "historico_versoes": {
                    "caapi-hubd-base-avaliacao-v1": {
                        "versao_anterior": "1.1.5",
                        "versao_nova": "1.2.0",
                        "tipo_mudanca": "MINOR_UPDATE",
                        "breaking_changes": False
                    }
                },
                "metricas_conformidade": {
                    "score_geral": 95.0,
                    "criterios_atendidos": 19,
                    "criterios_nao_atendidos": 1,
                    "criterios_nao_aplicaveis": 0,
                    "issues_criticas_abertas": 0,
                    "issues_totais": 2
                }
            }
        ]
    
    def parse_component_list(self, component_input: str) -> List[Dict[str, str]]:
        """
        Parse da lista de componentes no formato:
        componente -> versao
        """
        components = []
        
        if not component_input or not component_input.strip():
            return components
        
        for line in component_input.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if '->' in line:
                parts = line.split(' -> ')
                if len(parts) == 2:
                    name = parts[0].strip()
                    version = parts[1].strip()
                    
                    # Busca versão anterior no PortalTech
                    versao_anterior = self._get_previous_version_from_portaltech(name)
                    
                    components.append({
                        'nome': name,
                        'versao': version,
                        'versao_anterior': versao_anterior
                    })
        
        return components
    
    def _get_previous_version_from_portaltech(self, component_name: str) -> str:
        """Busca versão anterior nos dados do PortalTech"""
        for aprovacao in self.portaltech_data:
            historico = aprovacao.get('historico_versoes', {})
            if component_name in historico:
                return historico[component_name].get('versao_anterior', 'N/A')
        
        # Fallback se não encontrar
        version_fallback = {
            "caapi-hubd-base-avaliacao-v1": "1.2.8",
            "flutmicro-hubd-base-app-rating": "1.9.5",
            "ng15-hubd-base-portal-configuracao": "1.0.9"
        }
        return version_fallback.get(component_name, "N/A")
    
    def validate_component_against_confluence(self, component: Dict[str, str]) -> Dict[str, Any]:
        """Valida componente contra critérios do Confluence"""
        component_name = component['nome']
        validacoes = {}
        
        for criterio_id, criterio_data in self.confluence_criterios.items():
            # Simula validação automática baseada no componente
            compliance_result = self._simulate_compliance_check(component_name, criterio_id)
            
            validacoes[criterio_id] = {
                "id": criterio_data["id"],
                "pergunta": criterio_data["pergunta"],
                "categoria": criterio_data["categoria"],
                "resposta": compliance_result["resposta"],
                "comentario": compliance_result["comentario"],
                "evidencia": compliance_result.get("evidencia", ""),
                "peso": criterio_data["peso"],
                "obrigatorio": criterio_data["obrigatorio"],
                "fonte": criterio_data["fonte"]
            }
        
        return validacoes
    
    def _simulate_compliance_check(self, component_name: str, criterio_id: str) -> Dict[str, str]:
        """
        Simula verificação de conformidade baseada em regras de negócio
        Em produção, isso seria integração real com ferramentas de scan
        """
        
        # Matriz de conformidade simulada - baseada em análise real dos componentes
        compliance_matrix = {
            "caapi-hubd-base-avaliacao-v1": {
                "seguranca_autenticacao": {
                    "resposta": "Sim",
                    "comentario": "Implementa OAuth2 via Spring Security com JWT",
                    "evidencia": "spring-security-oauth2-core:5.7.2 configurado"
                },
                "padrao_logging": {
                    "resposta": "Não", 
                    "comentario": "Logs não estruturados - usando System.out.println",
                    "evidencia": "SonarQube: 15 ocorrências de logging não estruturado"
                },
                "documentacao_api": {
                    "resposta": "Sim",
                    "comentario": "Swagger UI disponível em /api-docs com specs atualizadas",
                    "evidencia": "springdoc-openapi-ui:1.6.12 configurado"
                },
                "testes_unitarios": {
                    "resposta": "Não",
                    "comentario": "Cobertura atual: 65% - Abaixo do mínimo de 80%", 
                    "evidencia": "JaCoCo Report: 65.2% line coverage"
                },
                "performance_sla": {
                    "resposta": "Sim",
                    "comentario": "Response time médio: 150ms - Dentro do SLA",
                    "evidencia": "New Relic: avg 147ms (últimos 7 dias)"
                },
                "seguranca_vulnerabilidades": {
                    "resposta": "Não",
                    "comentario": "2 vulnerabilidades médias detectadas",
                    "evidencia": "Snyk: jackson-databind CVE-2022-42003, CVE-2022-42004"
                }
            },
            "flutmicro-hubd-base-app-rating": {
                "seguranca_autenticacao": {
                    "resposta": "Sim",
                    "comentario": "JWT com refresh token via Passport.js",
                    "evidencia": "passport-jwt:4.0.1 implementado corretamente"
                },
                "padrao_logging": {
                    "resposta": "Sim",
                    "comentario": "Winston com formato JSON estruturado",
                    "evidencia": "winston:3.8.2 com transporte JSON configurado"
                },
                "documentacao_api": {
                    "resposta": "Não",
                    "comentario": "Documentação Swagger desatualizada há 3 meses",
                    "evidencia": "Última atualização: 2024-09-15"
                },
                "testes_unitarios": {
                    "resposta": "Sim", 
                    "comentario": "Cobertura atual: 87% - Acima do mínimo",
                    "evidencia": "Jest Coverage: 87.3% statements, 91.2% branches"
                },
                "performance_sla": {
                    "resposta": "Não",
                    "comentario": "Response time médio: 350ms - ACIMA DO SLA",
                    "evidencia": "DataDog: avg 347ms (últimos 7 dias) - SLA breach"
                },
                "seguranca_vulnerabilidades": {
                    "resposta": "Sim",
                    "comentario": "Nenhuma vulnerabilidade crítica detectada",
                    "evidencia": "npm audit: 0 critical, 1 moderate (non-exploitable)"
                }
            },
            "ng15-hubd-base-portal-configuracao": {
                "seguranca_autenticacao": {
                    "resposta": "Sim",
                    "comentario": "Angular Guard com OIDC via angular-oauth2-oidc",
                    "evidencia": "angular-oauth2-oidc:13.0.1 configurado"
                },
                "padrao_logging": {
                    "resposta": "Sim",
                    "comentario": "NGX-Logger com output estruturado",
                    "evidencia": "ngx-logger:5.0.12 com JSON formatter"
                },
                "documentacao_api": {
                    "resposta": "Sim",
                    "comentario": "Storybook atualizado com todos os componentes",
                    "evidencia": "Storybook 6.5.16 - última build: 2024-12-14"
                },
                "testes_unitarios": {
                    "resposta": "Não",
                    "comentario": "Cobertura atual: 45% - MUITO ABAIXO do mínimo",
                    "evidencia": "Karma/Jasmine: 45.1% statements - Crítico"
                },
                "performance_sla": {
                    "resposta": "Sim",
                    "comentario": "Load time < 2s conforme SLA para frontend",
                    "evidencia": "Lighthouse: First Contentful Paint 1.2s"
                },
                "seguranca_vulnerabilidades": {
                    "resposta": "Sim",
                    "comentario": "Scan limpo - nenhuma vulnerabilidade",
                    "evidencia": "npm audit: 0 vulnerabilities found"
                }
            }
        }
        
        # Resposta padrão se componente não encontrado
        default_response = {
            "resposta": "Não se Aplica",
            "comentario": "Componente não encontrado na matriz de conformidade",
            "evidencia": "Componente não catalogado no sistema"
        }
        
        component_rules = compliance_matrix.get(component_name, {})
        return component_rules.get(criterio_id, default_response)
    
    def get_jira_issues_for_component(self, component_name: str) -> List[Dict]:
        """Busca issues do Jira relacionadas ao componente"""
        return [
            issue for issue in self.jira_issues 
            if issue['componente'] == component_name
        ]
    
    def get_portaltech_approval_data(self, component_name: str) -> Optional[Dict]:
        """Busca dados de aprovação no PortalTech"""
        for aprovacao in self.portaltech_data:
            if component_name in aprovacao.get('componentes_escopo', []):
                return aprovacao
        return None
    
    def calculate_compliance_metrics(self, validacoes: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas de conformidade com pesos dos critérios"""
        
        # Contadores básicos
        total_criterios = len(validacoes)
        criterios_sim = sum(1 for v in validacoes.values() if v['resposta'] == 'Sim')
        criterios_nao = sum(1 for v in validacoes.values() if v['resposta'] == 'Não')
        criterios_na = sum(1 for v in validacoes.values() if v['resposta'] == 'Não se Aplica')
        
        # Score ponderado pelos pesos
        criterios_aplicaveis = {k: v for k, v in validacoes.items() if v['resposta'] != 'Não se Aplica'}
        
        if criterios_aplicaveis:
            total_peso = sum(v['peso'] for v in criterios_aplicaveis.values())
            peso_conforme = sum(v['peso'] for v in criterios_aplicaveis.values() if v['resposta'] == 'Sim')
            percentual_conformidade = (peso_conforme / total_peso * 100) if total_peso > 0 else 0
        else:
            percentual_conformidade = 0
        
        # Critérios obrigatórios não conformes (CRÍTICO)
        obrigatorios_nao_conformes = [
            k for k, v in validacoes.items() 
            if v['obrigatorio'] and v['resposta'] == 'Não'
        ]
        
        # Score qualitativo
        score_qualitativo = self._calculate_quality_score(
            percentual_conformidade, 
            obrigatorios_nao_conformes
        )
        
        return {
            "total_criterios": total_criterios,
            "criterios_sim": criterios_sim,
            "criterios_nao": criterios_nao,
            "criterios_nao_aplica": criterios_na,
            "criterios_aplicaveis": len(criterios_aplicaveis),
            "percentual_conformidade": round(percentual_conformidade, 1),
            "score_qualitativo": score_qualitativo,
            "obrigatorios_nao_conformes": obrigatorios_nao_conformes,
            "total_peso_possivel": sum(v['peso'] for v in criterios_aplicaveis.values()) if criterios_aplicaveis else 0,
            "peso_conquistado": sum(v['peso'] for v in criterios_aplicaveis.values() if v['resposta'] == 'Sim') if criterios_aplicaveis else 0
        }
    
    def _calculate_quality_score(self, percentual: float, obrigatorios_nao_conformes: List[str]) -> str:
        """Calcula score qualitativo baseado em regras de negócio"""
        
        # Regra 1: Critério obrigatório não conforme = CRÍTICO
        if obrigatorios_nao_conformes:
            return "CRÍTICO"
        
        # Regra 2: Score baseado no percentual
        if percentual >= 95:
            return "EXCELENTE"
        elif percentual >= 85:
            return "MUITO BOM" 
        elif percentual >= 75:
            return "BOM"
        elif percentual >= 65:
            return "REGULAR"
        elif percentual >= 50:
            return "INSUFICIENTE"
        else:
            return "CRÍTICO"
    
    def generate_component_report(self, component_input: str) -> Dict[str, Any]:
        """
        FUNÇÃO PRINCIPAL
        Gera relatório completo integrando Confluence + Jira + PortalTech
        """
        
        # 1. Parse da entrada
        componentes = self.parse_component_list(component_input)
        
        if not componentes:
            return {
                "erro": "Nenhum componente válido encontrado na entrada",
                "formato_esperado": "componente -> versao",
                "exemplo": "caapi-hubd-base-avaliacao-v1 -> 1.3.2"
            }
        
        # 2. Estrutura base do relatório
        timestamp = datetime.now()
        relatorio = {
            "metadata": {
                "id": f"REL-COMP-{timestamp.strftime('%Y%m%d%H%M%S')}",
                "timestamp": timestamp.isoformat(),
                "gerado_por": "ComponentReportEmulator v1.0",
                "fontes_integradas": {
                    "confluence": f"{len(self.confluence_criterios)} critérios carregados",
                    "jira": f"{len(self.jira_issues)} issues carregadas", 
                    "portaltech": f"{len(self.portaltech_data)} aprovações carregadas"
                },
                "total_componentes_analisados": len(componentes)
            },
            "componentes": {},
            "resumo_executivo": {},
            "recomendacoes": [],
            "anexos": {
                "criterios_confluence": self.confluence_criterios,
                "issues_jira_relacionadas": [],
                "aprovacoes_portaltech": []
            }
        }
        
        # 3. Análise individual por componente
        all_metrics = []
        all_issues = []
        
        for componente in componentes:
            nome = componente['nome']
            
            print(f"🔍 Analisando: {nome}")
            
            # 3.1 Validação contra Confluence
            validacoes = self.validate_component_against_confluence(componente)
            
            # 3.2 Issues do Jira
            issues = self.get_jira_issues_for_component(nome)
            all_issues.extend(issues)
            
            # 3.3 Dados do PortalTech
            aprovacao = self.get_portaltech_approval_data(nome)
            if aprovacao:
                relatorio["anexos"]["aprovacoes_portaltech"].append(aprovacao)
            
            # 3.4 Métricas de conformidade
            metricas = self.calculate_compliance_metrics(validacoes)
            all_metrics.append(metricas)
            
            # 3.5 Análise detalhada das issues do Jira
            analise_jira = self._analyze_jira_issues_detailed(issues)
            
            # 3.6 Consolidação dos dados do componente
            relatorio["componentes"][nome] = {
                "informacoes_basicas": {
                    "nome": nome,
                    "versao_atual": componente['versao'],
                    "versao_anterior": componente['versao_anterior'],
                    "tipo_mudanca": self._get_change_type(componente['versao_anterior'], componente['versao'])
                },
                "conformidade_confluence": {
                    "criterios_validados": validacoes,
                    "metricas": metricas,
                    "criterios_criticos": [k for k, v in validacoes.items() if v['obrigatorio'] and v['resposta'] == 'Não'],
                    "pontos_fortes": [k for k, v in validacoes.items() if v['resposta'] == 'Sim'],
                    "areas_melhoria": [k for k, v in validacoes.items() if v['resposta'] == 'Não']
                },
                "analise_jira": analise_jira,
                "dados_portaltech": {
                    "aprovacao_relacionada": aprovacao.get('id') if aprovacao else None,
                    "arquiteto_responsavel": aprovacao.get('arquiteto_responsavel') if aprovacao else "N/A",
                    "status_aprovacao": aprovacao.get('status') if aprovacao else "Não encontrado",
                    "observacoes": aprovacao.get('observacoes', []) if aprovacao else []
                },
                "score_final": self._calculate_component_final_score(metricas, analise_jira),
                "recomendacoes_especificas": self._generate_component_recommendations(validacoes, issues, metricas)
            }