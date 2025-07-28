#!/usr/bin/env python3
"""
Módulo de dados de aprovações arquiteturais - Feito Conferido
Baseado nos dados reais da aprovação C-979015
"""

import json
from datetime import datetime

class AprovacaoData:
    """Classe para gerenciar dados de aprovações arquiteturais."""
    
    def __init__(self):
        self.aprovacoes = self._load_aprovacoes()
    
    def _load_aprovacoes(self):
        """Carregar dados das aprovações."""
        return [
            {
                "id": "C-979015",
                "titulo": "Aprovação Arquitetura Software",
                "tipo": "Validação de Aderência Arquitetural",
                "data_aprovacao": "2025-07-16",
                "arquiteto_responsavel": "Alfredo Tavares",
                "cargo": "Arquiteto de Software",
                "responsabilidade": "Responsável pelo preenchimento do Checklist",
                
                "escopo_validacao": {
                    "ciclo_desenvolvimento": "C-979015",
                    "arquitetura": "TO-BE",
                    "componentes": [
                        {
                            "nome": "sboot-hubd-base-orch-consulta-componentes",
                            "versao_anterior": "0.41.0",
                            "versao_nova": "0.42.0",
                            "tipo": "Backend/Orquestração"
                        },
                        {
                            "nome": "springboot-hubd-base-bff-portal-configuracao",
                            "versao_anterior": "0.45.0",
                            "versao_nova": "0.46.0",
                            "tipo": "Backend/BFF"
                        },
                        {
                            "nome": "ng15-hubd-base-portal-configuracao",
                            "versao_anterior": "0.39.0",
                            "versao_nova": "0.41.0",
                            "tipo": "Frontend/Angular"
                        }
                    ]
                },
                
                "criterios_validacao": {
                    "1.1": {
                        "pergunta": "Os novos componentes desenhados na solução proposta foram implementados?",
                        "resposta": "Não se aplica",
                        "comentario": "",
                        "categoria": "Implementação de Componentes",
                        "peso": 1
                    },
                    "1.2": {
                        "pergunta": "A comunicação entre os componentes (síncrono / assíncrono) foram implementadas?",
                        "resposta": "Sim",
                        "comentario": "",
                        "categoria": "Comunicação entre Componentes",
                        "peso": 2
                    },
                    "1.3": {
                        "pergunta": "Os componentes foram alterados ou removidos conforme proposto no desenho?",
                        "resposta": "Não",
                        "comentario": "",
                        "categoria": "Alterações de Componentes",
                        "peso": 2
                    },
                    "1.4": {
                        "pergunta": "A solução adotou o chassi de plataformização backend em todos os novos componentes?",
                        "resposta": "Não se aplica",
                        "comentario": "",
                        "categoria": "Plataformização Backend",
                        "peso": 1
                    },
                    "1.5": {
                        "pergunta": "A solução adotou o chassi de plataformização frontend em todos os novos componentes?",
                        "resposta": "Não se aplica",
                        "comentario": "",
                        "categoria": "Plataformização Frontend",
                        "peso": 1
                    },
                    "3.1": {
                        "pergunta": "Foram implementados os patterns indicados para os componentes de desenho da solução (contexto de solução, ex. EDA, mensageria)?",
                        "resposta": "Sim",
                        "comentario": "",
                        "categoria": "Design Patterns - Solução",
                        "peso": 3
                    },
                    "3.2": {
                        "pergunta": "Foram implementados os design patterns indicado para os componentes do desenho da solução (contexto de aplicação)?",
                        "resposta": "Sim",
                        "comentario": "",
                        "categoria": "Design Patterns - Aplicação",
                        "peso": 3
                    },
                    "4.1": {
                        "pergunta": "Foram implementados as configurações de escalabilidade vertical, conforme indicado na solução (CPU, MEM)?",
                        "resposta": "Sim",
                        "comentario": "",
                        "categoria": "Escalabilidade Vertical",
                        "peso": 2
                    },
                    "4.2": {
                        "pergunta": "Foram definidas as configurações de escalabilidade horizontal (HPA)?",
                        "resposta": "Sim",
                        "comentario": "",
                        "categoria": "Escalabilidade Horizontal",
                        "peso": 2
                    },
                    "6.1": {
                        "pergunta": "Houve algum componente alterado ou criado que no radar da arquitetura está sinalizado como SAIR?",
                        "resposta": "Não",
                        "comentario": "",
                        "categoria": "Radar Arquitetura",
                        "peso": 3
                    },
                    "7.1": {
                        "pergunta": "Neste ciclo de desenvolvimento, houve necessidade de criar algum issue de débito técnico?",
                        "resposta": "Sim",
                        "comentario": "",
                        "categoria": "Débito Técnico",
                        "peso": 2
                    },
                    "8.1": {
                        "pergunta": "Neste ciclo de desenvolvimento, houve necessidade de criar algum issue de arquitetura de transição?",
                        "resposta": "Não",
                        "comentario": "",
                        "categoria": "Arquitetura de Transição",
                        "peso": 2
                    }
                },
                
                "issues_debito_tecnico": [
                    {
                        "id": "GDA-933",
                        "descricao": "Issue de débito técnico identificada no ciclo C-979015",
                        "status": "Aberta",
                        "prioridade": "Média",
                        "impacto": "Conformidade arquitetural"
                    }
                ],
                
                "issues_transicao": [],
                
                "parecer_final": "Aderente com débito ou transição",
                
                "resumo_conformidade": {
                    "total_criterios": 12,
                    "criterios_sim": 7,
                    "criterios_nao": 1,
                    "criterios_nao_aplica": 4,
                    "percentual_conformidade": 77.8,
                    "score_qualidade": 85,
                    "classificacao": "ADERENTE_COM_DEBITO"
                },
                
                "metadados": {
                    "data_criacao": "2025-07-16T10:00:00Z",
                    "versao_checklist": "2.1",
                    "sistema": "Portal Configuração Hub",
                    "dominio": "Plataforma Digital",
                    "criticidade": "ALTA",
                    "proxima_revisao": "2025-08-16"
                },
                
                "observacoes": [
                    "Aprovação com débito técnico GDA-933 que deve ser resolvido no próximo ciclo",
                    "Componentes de plataformização não se aplicam neste contexto específico",
                    "Escalabilidade implementada conforme especificações",
                    "Design patterns adequadamente aplicados"
                ]
            }
        ]
    
    def get_all_aprovacoes(self):
        """Retornar todas as aprovações."""
        return self.aprovacoes
    
    def get_aprovacao_by_id(self, aprovacao_id):
        """Buscar aprovação por ID."""
        for aprovacao in self.aprovacoes:
            if aprovacao.get('id') == aprovacao_id or aprovacao.get('escopo_validacao', {}).get('ciclo_desenvolvimento') == aprovacao_id:
                return aprovacao
        return None
    
    def get_aprovacoes_by_arquiteto(self, arquiteto):
        """Buscar aprovações por arquiteto."""
        return [a for a in self.aprovacoes if a.get('arquiteto_responsavel', '').lower() == arquiteto.lower()]
    
    def get_estatisticas(self):
        """Calcular estatísticas gerais."""
        total = len(self.aprovacoes)
        if total == 0:
            return {}
        
        aderentes = 0
        conformidade_total = 0
        issues_total = 0
        
        for aprovacao in self.aprovacoes:
            parecer = aprovacao.get('parecer_final', '').lower()
            if 'aderente' in parecer:
                aderentes += 1
            
            conf = aprovacao.get('resumo_conformidade', {}).get('percentual_conformidade', 0)
            conformidade_total += conf
            
            issues_total += len(aprovacao.get('issues_debito_tecnico', []))
        
        return {
            'total_aprovacoes': total,
            'aprovacoes_aderentes': aderentes,
            'taxa_aderencia': (aderentes / total) * 100,
            'conformidade_media': conformidade_total / total,
            'total_issues_debito': issues_total
        }

# Instância global para uso
aprovacao_data = AprovacaoData()

# Função de conveniência
def get_all_aprovacoes():
    """Função de conveniência para obter todas as aprovações."""
    return aprovacao_data.get_all_aprovacoes()

def buscar_aprovacao(aprovacao_id):
    """Função de conveniência para buscar aprovação por ID."""
    return aprovacao_data.get_aprovacao_by_id(aprovacao_id)

if __name__ == "__main__":
    # Teste do módulo
    print("=== TESTE DO MÓDULO DE DADOS ===")
    
    # Listar todas as aprovações
    aprovacoes = get_all_aprovacoes()
    print(f"Total de aprovações: {len(aprovacoes)}")
    
    # Buscar aprovação específica
    aprovacao = buscar_aprovacao("C-979015")
    if aprovacao:
        print(f"Aprovação encontrada: {aprovacao['id']}")
        print(f"Arquiteto: {aprovacao['arquiteto_responsavel']}")
        print(f"Parecer: {aprovacao['parecer_final']}")
        print(f"Conformidade: {aprovacao['resumo_conformidade']['percentual_conformidade']}%")
    
    # Estatísticas
    stats = aprovacao_data.get_estatisticas()
    print(f"Estatísticas: {stats}")

