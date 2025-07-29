"""Ferramentas principais de validação para o processo Feito/Conferido com respostas MOCKADAS.

Fornece a ferramenta de validação principal que orquestra
o fluxo de trabalho completo de validação Feito/Conferido.

ESTA VERSÃO CONTÉM RESPOSTAS MOCKADAS PARA TESTES!
"""

from typing import Dict, List, Any, Optional
from google.adk.tools import ToolContext
from datetime import datetime, timezone
import random


# ===== DADOS MOCK DO BLIZZDESIGN =====
BLIZZDESIGN_MOCK_EXPORTS = {
    "JT-147338": {
        "viewInfo": {
            "name": "Visão Técnica - NPS/CES/CSAT",
            "JT": "JT-147338"
        },
        "elements": [
            {
                "id": "bb502786-647f-ef11-84d2-16ffc1277435",
                "name": "caapi-hubd-base-avaliacao-v1",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "NOVO"
            },
            {
                "id": "4680d0d7-647f-ef11-84d2-16ffc1277435",
                "name": "GET /v1/evaluation/{evaluationType}",
                "type": "ArchiMate:ApplicationService",
                "stereotype": "NOVO"
            },
            {
                "id": "5e9ea4d8-2480-ef11-84d2-16ffe58a20bb",
                "name": "POST /v1/evaluation/{evaluationType}",
                "type": "ArchiMate:ApplicationService",
                "stereotype": "NOVO"
            },
            {
                "id": "fc413269-0081-ef11-84d2-16ffc926a3dd",
                "name": "caapi-hubd-base-avaliacao-gravar-v3",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "REMOVIDO"
            },
            {
                "id": "11a00ad4-3862-ee11-844a-16243b297e85",
                "name": "flutmicro-hubd-base-app-rating",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "ALTERADO"
            },
            {
                "id": "748ef25d-737f-ef11-84d2-16ffc1277435",
                "name": "ng15-hubd-base-portal-configuracao",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "ALTERADO"
            },
            {
                "id": "61dfb81a-2bcc-ee11-8469-16b943249bff",
                "name": "HUBDAvaliacaoAplicativo_APPL",
                "type": "ArchiMate:TechnologyArtifact",
                "stereotype": "ALTERADO"
            },
            {
                "id": "c7a4e14a-757f-ef11-84d2-16ffc1277435",
                "name": "springboot-hubd-base-bff-portal-configuracao",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "ALTERADO"
            },
            {
                "id": "9f9fc917-1c80-ef11-84d2-16ffe58a20bb",
                "name": "sboot-hubd-base-atom-avaliacao",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "NOVO"
            },
            {
                "id": "05aeb61f-0f7d-ef11-84d2-16ffe90bcc57",
                "name": "Avaliação e Análise pelo Cliente em Canais",
                "type": "ArchiMate:ApplicationCollaboration",
                "stereotype": "NOVO"
            },
            {
                "id": "ed9f0ad4-3862-ee11-844a-16243b297e85",
                "name": "sboot-hubd-base-atom-avaliacao-store",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "REMOVIDO"
            },
            {
                "id": "f29f0ad4-3862-ee11-844a-16243b297e85",
                "name": "sboot-hubd-base-orch-avaliacao-store",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "REMOVIDO"
            }
        ],
        "relationships": [
            {
                "id": "3da9c240-6a7f-ef11-84d2-16ffc1277435",
                "type": "ArchiMate:ApplicationServiceApplicationComponentUse",
                "stereotype": "NOVO",
                "source": {
                    "id": "1a2333f4-697f-ef11-84d2-16ffc1277435",
                    "name": "GET /v1/evaluations/{evaluationType}",
                    "type": "ArchiMate:ApplicationService"
                },
                "target": {
                    "id": "bb502786-647f-ef11-84d2-16ffc1277435",
                    "name": "caapi-hubd-base-avaliacao-v1",
                    "type": "ArchiMate:ApplicationComponent"
                }
            },
            {
                "id": "97d5a166-2480-ef11-84d2-16ffe58a20bb",
                "type": "ArchiMate:ApplicationServiceApplicationComponentUse",
                "stereotype": "NOVO",
                "source": {
                    "id": "27dbeac1-697f-ef11-84d2-16ffc1277435",
                    "name": "POST /v1/evaluations/{evaluationType}",
                    "type": "ArchiMate:ApplicationService"
                },
                "target": {
                    "id": "bb502786-647f-ef11-84d2-16ffc1277435",
                    "name": "caapi-hubd-base-avaliacao-v1",
                    "type": "ArchiMate:ApplicationComponent"
                }
            },
            {
                "id": "c72e7260-2080-ef11-84d2-16ffe58a20bb",
                "type": "ArchiMate:ApplicationComponentApplicationServiceRealisation",
                "source": {
                    "id": "bb502786-647f-ef11-84d2-16ffc1277435",
                    "name": "caapi-hubd-base-avaliacao-v1",
                    "type": "ArchiMate:ApplicationComponent"
                },
                "target": {
                    "id": "4680d0d7-647f-ef11-84d2-16ffc1277435",
                    "name": "GET /v1/evaluation/{evaluationType}",
                    "type": "ArchiMate:ApplicationService"
                }
            }
        ],
        "metadata": {
            "elementCount": 33,
            "relationshipCount": 46
        }
    },
    "JT-DEFAULT": {
        "viewInfo": {
            "name": "Visão Técnica - Sistema Padrão",
            "JT": "JT-DEFAULT"
        },
        "elements": [
            {
                "id": "mock-component-1",
                "name": "sboot-exemplo-api",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "NOVO"
            },
            {
                "id": "mock-service-1",
                "name": "GET /v1/exemplo",
                "type": "ArchiMate:ApplicationService",
                "stereotype": "NOVO"
            },
            {
                "id": "mock-component-2",
                "name": "user-service",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "MANTIDO"
            },
            {
                "id": "mock-component-3",
                "name": "auth-module",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "MANTIDO"
            },
            {
                "id": "mock-component-4",
                "name": "notification-service",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "ALTERADO"
            },
            {
                "id": "mock-component-5",
                "name": "api-gateway",
                "type": "ArchiMate:ApplicationComponent",
                "stereotype": "NOVO"
            }
        ],
        "relationships": [
            {
                "id": "mock-rel-1",
                "type": "ArchiMate:ApplicationComponentApplicationServiceRealisation",
                "stereotype": "NOVO",
                "source": {
                    "id": "mock-component-1",
                    "name": "sboot-exemplo-api",
                    "type": "ArchiMate:ApplicationComponent"
                },
                "target": {
                    "id": "mock-service-1",
                    "name": "GET /v1/exemplo",
                    "type": "ArchiMate:ApplicationService"
                }
            }
        ],
        "metadata": {
            "elementCount": 6,
            "relationshipCount": 1,
            "exportDate": datetime.now().isoformat()
        }
    }
}


# ===== FUNÇÕES AUXILIARES MOCK =====

def format_validation_result(
    overall_status: str,
    errors: List[str],
    warnings: List[str],
    manual_actions: List[str]
) -> str:
    """Formatador mock para resultados de validação.
    
    Cria uma apresentação estruturada dos resultados de validação
    com emojis e formatação visual para facilitar a leitura.
    
    Args:
        overall_status: Status geral da validação.
        errors: Lista de erros encontrados.
        warnings: Lista de avisos.
        manual_actions: Lista de ações manuais necessárias.
    
    Returns:
        String formatada com o resultado da validação.
        
    Example:
        >>> result = format_validation_result("APPROVED", [], ["Versão antiga"], [])
        >>> print(result)
        ✅ Status: APPROVED
        
        ⚠️ Warnings (1):
        - Versão antiga
    """
    summary = f"✅ Status: {overall_status}"
    
    if errors:
        summary += f"\n\n❌ Erros ({len(errors)}):"
        for error in errors:
            summary += f"\n- {error}"
    
    if warnings:
        summary += f"\n\n⚠️ Avisos ({len(warnings)}):"
        for warning in warnings:
            summary += f"\n- {warning}"
    
    if manual_actions:
        summary += f"\n\n📋 Ações Manuais Necessárias ({len(manual_actions)}):"
        for action in manual_actions:
            summary += f"\n- {action}"
    
    return summary


def extract_blizzdesign_components(blizzdesign_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extrai componentes de aplicação do export do BlizzDesign.
    
    Filtra apenas elementos do tipo ApplicationComponent do export
    do BlizzDesign e extrai informações relevantes.
    
    Args:
        blizzdesign_data: Dados do export do BlizzDesign.
    
    Returns:
        Lista de componentes com informações extraídas.
        
    Example:
        >>> data = {"elements": [{"name": "user-service", "type": "ArchiMate:ApplicationComponent", "stereotype": "NOVO"}]}
        >>> components = extract_blizzdesign_components(data)
        >>> print(components[0]["name"])
        'user-service'
    """
    components = []
    
    for element in blizzdesign_data.get("elements", []):
        # Filtra apenas componentes de aplicação
        if element.get("type") == "ArchiMate:ApplicationComponent":
            components.append({
                "name": element.get("name"),
                "stereotype": element.get("stereotype", "MANTIDO"),
                "id": element.get("id"),
                "type": element.get("type")
            })
    
    return components


# ===== FUNÇÕES MOCK VT/BLIZZDESIGN =====

async def get_blizzdesign_export(jt_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKADO: Retorna dados mock de export do BlizzDesign.
    
    Simula a busca de dados de export do BlizzDesign para um JT específico.
    Usa dados pré-definidos para JTs conhecidos ou retorna dados padrão.
    
    Args:
        jt_id: ID do JT (Journey/Template) para buscar dados.
        tool_context: Contexto da ferramenta para armazenar estado.
    
    Returns:
        Dicionário com dados de export do BlizzDesign.
        
    Example:
        >>> export_data = await get_blizzdesign_export("JT-147338", context)
        >>> print(export_data["viewInfo"]["name"])
        'Visão Técnica - NPS/CES/CSAT'
    """
    # Armazena flag de mock no contexto
    tool_context.state["use_mock"] = True
    
    # Verifica se temos dados mock específicos para este JT
    if jt_id in BLIZZDESIGN_MOCK_EXPORTS:
        export_data = BLIZZDESIGN_MOCK_EXPORTS[jt_id]
    else:
        # Retorna dados mock padrão
        export_data = BLIZZDESIGN_MOCK_EXPORTS["JT-DEFAULT"]
        # Atualiza ID do JT para corresponder à requisição
        export_data["viewInfo"]["JT"] = jt_id
        export_data["viewInfo"]["name"] = f"Visão Técnica - {jt_id}"
    
    # Armazena no contexto para reutilização
    tool_context.state[f"blizzdesign_export_{jt_id}"] = export_data
    tool_context.state[f"blizzdesign_mock_{jt_id}"] = export_data
    
    return export_data


async def parse_blizzdesign_data(
    blizzdesign_json: Dict[str, Any], 
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKADO: Analisa dados de export do BlizzDesign.
    
    Processa os dados de export do BlizzDesign extraindo componentes
    e agrupando-os por estereótipo (NOVO, ALTERADO, REMOVIDO, MANTIDO).
    
    Args:
        blizzdesign_json: Dados JSON do export do BlizzDesign.
        tool_context: Contexto da ferramenta para armazenar estado.
    
    Returns:
        Dicionário com dados processados e agrupados.
        
    Raises:
        Exception: Se falha ao processar os dados do BlizzDesign.
        
    Example:
        >>> parsed = await parse_blizzdesign_data(export_data, context)
        >>> print(f"Total: {parsed['total_components']} componentes")
        >>> print(f"Novos: {len(parsed['new_components'])}")
    """
    try:
        view_info = blizzdesign_json.get("viewInfo", {})
        view_name = view_info.get("name", "Desconhecido")
        jt_id = view_info.get("JT", "")
        
        # Extrai componentes
        components = extract_blizzdesign_components(blizzdesign_json)
        
        # Agrupa por estereótipo
        new_components = []
        modified_components = []
        removed_components = []
        maintained_components = []
        
        for comp in components:
            name = comp["name"]
            stereotype = comp["stereotype"]
            
            # Classifica componentes por estereótipo
            if stereotype == "NOVO":
                new_components.append(name)
            elif stereotype == "ALTERADO":
                modified_components.append(name)
            elif stereotype == "REMOVIDO":
                removed_components.append(name)
            elif stereotype == "MANTIDO":
                maintained_components.append(name)
        
        # Obtém metadados
        metadata = blizzdesign_json.get("metadata", {})
        element_count = metadata.get("elementCount", 0)
        relationship_count = metadata.get("relationshipCount", 0)
        
        # Armazena dados processados no contexto
        tool_context.state[f"blizzdesign_{jt_id}"] = {
            "components": components,
            "new_components": new_components,
            "modified_components": modified_components,
            "removed_components": removed_components,
            "maintained_components": maintained_components
        }
        
        return {
            "view_name": view_name,
            "jt_id": jt_id,
            "components": components,
            "new_components": new_components,
            "modified_components": modified_components,
            "removed_components": removed_components,
            "maintained_components": maintained_components,
            "total_components": len(components),
            "element_count": element_count,
            "relationship_count": relationship_count
        }
        
    except Exception as e:
        return {
            "error": f"Falha ao processar dados do BlizzDesign: {str(e)}"
        }


# ===== FUNÇÕES MOCK JIRA =====

async def get_jira_ticket(ticket_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKADO: Retorna dados mock de ticket do Jira correspondendo à estrutura real da API.
    
    Simula diferentes cenários baseados no ID do ticket para testes
    abrangentes do fluxo de validação.
    
    Args:
        ticket_id: ID do ticket Jira para buscar.
        tool_context: Contexto da ferramenta para armazenar estado.
    
    Returns:
        Dicionário com dados do ticket Jira.
        
    Example:
        >>> ticket = await get_jira_ticket("PDI-12345", context)
        >>> print(ticket["summary"])
        'Deploy new services for PDI-12345'
        >>> print(ticket["components"])
        ['user-service', 'auth-module', 'notification-service']
    """
    # Simula diferentes cenários baseados no ID do ticket
    if "ERROR" in ticket_id:
        return {
            "ticket_id": ticket_id,
            "error": "Falha ao buscar ticket Jira: Timeout de conexão"
        }
    
    if ticket_id == "PDI-99999":
        # Mock de ticket sem componentes
        return {
            "ticket_id": "10099999",
            "ticket_key": "PDI-99999",
            "summary": "Deploy service vazio",
            "description": "Deploy de service sem componentes para teste",
            "status": "Em Progresso",
            "status_category": "Em Progresso",
            "assignee": "Maria Santos",
            "reporter": "João Silva",
            "priority": "Alta",
            "components": [],
            "development_cycle": "Sprint 23",
            "pdi_description": "Deploy de service sem componentes",
            "arqcor_id": ""
        }
    
    # Resposta mock padrão com estrutura completa
    mock_components = ["user-service", "auth-module", "notification-service"]
    if "GATEWAY" in ticket_id:
        mock_components.append("api-gateway")
    
    # Gera ID interno a partir do ID do ticket
    internal_id = f"100{ticket_id.split('-')[1]}"
    
    return {
        "ticket_id": internal_id,
        "ticket_key": ticket_id,
        "summary": f"Deploy de novos services para {ticket_id}",
        "description": f"Este é um ticket mock para deploy de {', '.join(mock_components)} no ambiente de produção.",
        "status": "Em Progresso",
        "status_category": "Em Progresso",
        "assignee": "João Silva",
        "reporter": "Ana Costa",
        "priority": "Média",
        "components": mock_components,
        "development_cycle": "Sprint 23",
        "pdi_description": f"Deploy de {', '.join(mock_components)} no ambiente de produção",
        "arqcor_id": "ARQCOR-123"
    }


async def validate_pdi_components(ticket_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """MOCKADO: Retorna resultado mock de validação de PDI.
    
    Simula a validação de componentes mencionados na descrição do PDI
    versus os componentes efetivamente listados no ticket.
    
    Args:
        ticket_id: ID do ticket PDI para validar.
        tool_context: Contexto da ferramenta para armazenar estado.
    
    Returns:
        Dicionário com resultado da validação do PDI.
        
    Example:
        >>> result = await validate_pdi_components("PDI-12345", context)
        >>> print(result["is_valid"])
        True
        >>> print(result["warnings"])
        []
    """
    # Simula diferentes cenários
    if ticket_id == "PDI-DONE":
        return {
            "ticket_id": ticket_id,
            "is_valid": False,
            "components_not_in_description": [],
            "warnings": ["PDI tem status 'Concluído' - não é possível prosseguir com PDI finalizado"]
        }
    
    if ticket_id == "PDI-INVALID":
        return {
            "ticket_id": ticket_id,
            "is_valid": False,
            "components_not_in_description": ["notification-service"],
            "warnings": ["Componente 'notification-service' não mencionado na descrição do PDI"]
        }
    
    # Padrão: PDI válido
    return {
        "ticket_id": ticket_id,
        "is_valid": True,
        "components_not_in_description": [],
        "warnings": []
    }


async def validate_components_in_vt(
    ticket_id: str, 
    components: List[str], 
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKADO: Retorna resultado mock de validação no VT.
    
    Simula a validação de componentes contra a Visão Técnica (VT)
    para verificar se estão aprovados na arquitetura de referência.
    
    Args:
        ticket_id: ID do ticket para contexto.
        components: Lista de componentes para validar.
        tool_context: Contexto da ferramenta para armazenar estado.
    
    Returns:
        Dicionário com resultado da validação no VT.
        
    Example:
        >>> result = await validate_components_in_vt("PDI-12345", ["user-service"], context)
        >>> print(result["is_valid"])
        True
        >>> print(result["approved_components"])
        ['user-service']
    """
    # Armazena no contexto para uso posterior
    tool_context.state[f"vt_{ticket_id}"] = {
        "vt_id": "VT-2024-001",
        "architecture": "Microservices",
        "approved_components": ["user-service", "auth-module", "notification-service"]
    }
    
    # Simula componentes não aprovados
    if ticket_id == "PDI-UNAPPROVED":
        return {
            "is_valid": False,
            "unapproved_components": ["payment-service", "billing-service"],
            "approved_components": ["user-service"],
            "vt_id": "VT-2024-001"
        }
    
    # Verifica se algum componente não está na lista aprovada
    approved = ["user-service", "auth-module", "notification-service", "api-gateway"]
    unapproved = [c for c in components if c not in approved]
    
    if unapproved:
        return {
            "is_valid": False,
            "unapproved_components": unapproved,
            "approved_components": [c for c in components if c in approved],
            "vt_id": "VT-2024-001"
        }
    
    # Padrão: todos os componentes aprovados
    return {
        "is_valid": True,
        "unapproved_components": [],
        "approved_components": components,
        "vt_id": "VT-2024-001"
    }


# ===== FUNÇÕES MOCK ARQCOR =====

async def create_arqcor_form(
    ticket_id: str,
    evaluator_name: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKADO: Retorna resultado mock de criação de formulário ARQCOR.
    
    Simula a criação de um formulário no sistema ARQCOR para
    documentar a validação de aderência arquitetural.
    
    Args:
        ticket_id: ID do ticket associado ao formulário.
        evaluator_name: Nome do avaliador responsável.
        tool_context: Contexto da ferramenta para armazenar estado.
    
    Returns:
        Dicionário com informações do formulário criado.
        
    Example:
        >>> form = await create_arqcor_form("PDI-12345", "João Silva", context)
        >>> print(form["form_id"])
        'ARQCOR-2024-1234'
        >>> print(form["status"])
        'draft'
    """
    # Simula cenário de erro
    if ticket_id == "PDI-ARQCOR-ERROR":
        return {"error": "Falha ao criar formulário ARQCOR: Serviço indisponível"}
    
    # Gera ID mock do formulário
    form_id = f"ARQCOR-2024-{random.randint(1000, 9999)}"
    
    # Armazena no contexto
    tool_context.state[f"arqcor_form_{ticket_id}"] = {
        "form_id": form_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    return {
        "form_id": form_id,
        "status": "rascunho",
        "form_url": f"https://arqcor.company.com/forms/{form_id}"
    }


async def update_arqcor_form_with_versions(
    form_id: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKADO: Retorna resultado mock de atualização do ARQCOR.
    
    Simula a atualização de um formulário ARQCOR com informações
    de versões dos componentes validados.
    
    Args:
        form_id: ID do formulário a ser atualizado.
        tool_context: Contexto da ferramenta para armazenar estado.
    
    Returns:
        Dicionário com status da atualização.
        
    Example:
        >>> result = await update_arqcor_form_with_versions("ARQCOR-2024-1234", context)
        >>> print(result["updated"])
        True
    """
    # Simula cenário de erro
    if "ERROR" in form_id:
        return {
            "form_id": form_id,
            "error": "Falha ao atualizar formulário ARQCOR: Formulário bloqueado"
        }
    
    return {
        "form_id": form_id,
        "updated": True
    }


async def add_validation_checklist_to_form(
    form_id: str,
    checklist_items: List[Dict[str, Any]],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKADO: Retorna resultado mock de adição de checklist.
    
    Simula a adição de itens de checklist de validação
    ao formulário ARQCOR.
    
    Args:
        form_id: ID do formulário para adicionar checklist.
        checklist_items: Lista de itens do checklist a serem adicionados.
        tool_context: Contexto da ferramenta para armazenar estado.
    
    Returns:
        Dicionário com status da adição do checklist.
        
    Example:
        >>> items = [{"item": "Validar componentes", "status": "pending"}]
        >>> result = await add_validation_checklist_to_form("ARQCOR-2024-1234", items, context)
        >>> print(result["checklist_added"])
        True
    """
    # Simula cenário de erro
    if "ERROR" in form_id:
        return {
            "form_id": form_id,
            "error": "Falha ao adicionar checklist: Erro de banco de dados"
        }
    
    return {
        "form_id": form_id,
        "checklist_added": True
    }


# ===== FUNÇÕES MOCK PORTAL TECH =====

async def check_multiple_component_versions(
    components: List[Dict[str, str]],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """MOCKADO: Retorna resultado mock de verificação de versões correspondendo à estrutura real da API.
    
    Simula a verificação de versões de múltiplos componentes no Portal Tech,
    classificando mudanças por tipo (NEW, MAJOR, MINOR, PATCH) e identificando
    componentes com erro.
    
    Args:
        components: Lista de dicionários com 'name' e 'version' dos componentes.
        tool_context: Contexto da ferramenta para armazenar estado.
    
    Returns:
        Dicionário com resultados detalhados da verificação de versões.
        
    Example:
        >>> components = [{"name": "user-service", "version": "1.2.0"}]
        >>> result = await check_multiple_component_versions(components, context)
        >>> print(result["summary"])
        '1 components: 1 minor updates'
        >>> print(result["version_changes"][0]["type"])
        'MINOR'
    """
    version_changes = []
    new_components = []
    major_changes = []
    components_with_errors = []
    
    for comp in components:
        name = comp["name"]
        version = comp["version"]
        
        # Simula erro para nomes de componentes específicos
        if "error" in name.lower():
            components_with_errors.append(name)
            continue
        
        # Simula diferentes cenários baseados no nome do componente
        if "new" in name.lower():
            new_components.append(name)
            version_changes.append({
                "component": name,
                "change": f"NOVO → {version}",
                "type": "NEW"
            })
        elif "major" in name.lower():
            major_changes.append(name)
            version_changes.append({
                "component": name,
                "change": f"1.5.0 → {version}",
                "type": "MAJOR"
            })
        else:
            # Simula mudança de versão menor
            old_version = "1.0.0"
            if version.startswith("1.0."):
                change_type = "PATCH"
            elif version.startswith("1."):
                change_type = "MINOR"
            else:
                change_type = "MAJOR"
                major_changes.append(name)
            
            version_changes.append({
                "component": name,
                "change": f"{old_version} → {version}",
                "type": change_type
            })
    
    # Constrói resumo
    total = len(components)
    new_count = len(new_components)
    major_count = len(major_changes)
    error_count = len(components_with_errors)
    minor_count = len([vc for vc in version_changes if vc["type"] == "MINOR"])
    patch_count = len([vc for vc in version_changes if vc["type"] == "PATCH"])
    
    summary_parts = [f"{total} componentes"]
    details = []
    if new_count > 0:
        details.append(f"{new_count} novos")
    if major_count > 0:
        details.append(f"{major_count} atualizações major")
    if minor_count > 0:
        details.append(f"{minor_count} atualizações minor")
    if patch_count > 0:
        details.append(f"{patch_count} atualizações patch")
    if error_count > 0:
        details.append(f"{error_count} erros")
    
    summary = summary_parts[0]
    if details:
        summary += ": " + ", ".join(details)
    
    # Armazena no contexto
    tool_context.state["version_check_results"] = {
        "version_changes": version_changes,
        "new_components": new_components,
        "major_changes": major_changes
    }
    
    return {
        "total_components": total,
        "version_changes": version_changes,
        "new_components": new_components,
        "major_changes": major_changes,
        "components_with_errors": components_with_errors,
        "summary": summary
    }
