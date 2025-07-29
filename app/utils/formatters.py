"""Utilitários de formatação para o agente Feito/Conferido.

Fornece funções para formatação de saída, análise de entrada
e padronização de apresentação de dados.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import re


def format_component_name(component_name: str) -> str:
    """Formata um nome de componente para exibição consistente.

    Normaliza nomes de componentes para um formato padrão.

    Args:
        component_name: Nome bruto do componente.

    Returns:
        Nome do componente formatado.

    Example:
        >>> format_component_name("USER_SERVICE")
        'user-service'
        >>> format_component_name("auth.module")
        'auth-module'
    """
    
    formatted = component_name.lower()
    formatted = re.sub(r'[_.\s]+', '-', formatted)
    return formatted


def format_version_comparison(
    component: str, 
    current_version: str, 
    expected_version: str
) -> str:
    """Formata o resultado de uma comparação de versões para exibição.

    Cria uma comparação legível entre versões atual e esperada.

    Args:
        component: Nome do componente.
        current_version: Versão atualmente implantada.
        expected_version: Versão esperada/requerida.

    Returns:
        String de comparação formatada.

    Example:
        >>> format_version_comparison("user-service", "1.2.3", "1.3.0")
        'user-service: 1.2.3 → 1.3.0 (atualização necessária)'
    """
    comparison = compare_versions(current_version, expected_version)
    
    if comparison == 0:
        status = "✓ (versões coincidem)"
    elif comparison < 0:
        status = "⬆ (atualização necessária)"
    else:
        status = "⚠ (mais nova que esperada)"
    
    return f"{component}: {current_version} → {expected_version} {status}"


def compare_versions(version1: str, version2: str) -> int:
    """Compara duas strings de versão semântica.

    Realiza comparação de versões semânticas seguindo as regras do semver.

    Args:
        version1: Primeira string de versão.
        version2: Segunda string de versão.

    Returns:
        -1 se version1 < version2
         0 se version1 == version2
         1 se version1 > version2

    Example:
        >>> compare_versions("1.2.3", "1.2.4")
        -1
        >>> compare_versions("2.0.0", "1.9.9")
        1
    """
    def parse_version(v: str) -> tuple:
        """Converte string de versão em tupla de inteiros para comparação."""
        parts = v.split('.')
        return tuple(int(part) for part in parts[:3])  
    
    try:
        v1 = parse_version(version1)
        v2 = parse_version(version2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    except (ValueError, AttributeError):
        # Fallback para comparação lexicográfica se parsing falhar
        return -1 if version1 < version2 else (1 if version1 > version2 else 0)


def format_validation_result(status: str, 
                             errors: List[str], 
                             warnings: List[str],
                             manual_actions: List[str]) -> str:
    """Formata um resultado de validação para exibição.

    Cria uma apresentação estruturada do resultado de validação
    com diferentes tipos de mensagens organizadas por categoria.

    Args:
        status: Status geral (APPROVED, FAILED, REQUIRES_MANUAL_ACTION).
        errors: Lista de mensagens de erro.
        warnings: Lista de mensagens de aviso.
        manual_actions: Lista de ações manuais necessárias.

    Returns:
        String de resultado formatada.

    Example:
        >>> format_validation_result("APPROVED", [], ["Versão antiga"], [])
        '✅ Status: APPROVED\\n\\n⚠️ Avisos:\\n  • Versão antiga'
    """
    status_emoji = {
        "APPROVED": "✅",
        "FAILED": "❌",
        "REQUIRES_MANUAL_ACTION": "⚠️"
    }.get(status, "❓")
    
    result = f"{status_emoji} Status: {status}\n"
    
    if errors:
        result += "\n❌ Erros:\n"
        for error in errors:
            result += f"  • {error}\n"
    
    if warnings:
        result += "\n⚠️ Avisos:\n"
        for warning in warnings:
            result += f"  • {warning}\n"
    
    if manual_actions:
        result += "\n📋 Ações Manuais Necessárias:\n"
        for action in manual_actions:
            result += f"  • {action}\n"
    
    return result.strip()


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Formata um datetime para exibição.

    Converte um objeto datetime em string formatada padrão
    para uso em relatórios e logs.

    Args:
        dt: Datetime para formatar. Usa horário atual se None.

    Returns:
        String de timestamp formatada.

    Example:
        >>> format_timestamp(datetime(2024, 1, 15, 10, 30, 0))
        '2024-01-15 10:30:00'
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_component_list_from_text(text: str) -> Dict[str, str]:
    """Extrai componentes e versões do texto de entrada do usuário.

    Parser aprimorado que suporta múltiplos formatos para especificação de componentes:
    - "componente -> versão"
    - "componente : versão"
    - "componente versão" (separado por espaço)
    - Formato JSON
    - Listas separadas por vírgula

    Args:
        text: Texto de entrada do usuário contendo lista de componentes.

    Returns:
        Dicionário mapeando nomes de componentes para versões.

    Example:
        >>> text = '''
        ... caapi-hubd-base-avaliacao-v1 -> 1.3.2
        ... flutmicro-hubd-base-app-rating: 2.0.1
        ... ng15-hubd-base-portal 1.1.1
        ... user-service, auth-module: 2.0.0
        ... '''
        >>> result = parse_component_list_from_text(text)
        >>> print(result)
        {
            'caapi-hubd-base-avaliacao-v1': '1.3.2',
            'flutmicro-hubd-base-app-rating': '2.0.1',
            'ng15-hubd-base-portal': '1.1.1',
            'user-service': '',
            'auth-module': '2.0.0'
        }
    """
    components = {}
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        # Ignora linhas vazias e comentários
        if not line or line.startswith('#') or line.startswith('//'):
            continue
        
        # Tenta parsear como JSON
        if line.startswith('{') and line.endswith('}'):
            try:
                import json
                json_data = json.loads(line)
                if isinstance(json_data, dict):
                    components.update(json_data)
                    continue
            except:
                pass
        
        # Formato: componente -> versão
        if '->' in line:
            parts = line.split('->')
            if len(parts) == 2:
                component_name = parts[0].strip()
                version = parts[1].strip()
                components[component_name] = version
        
        # Formato: componente : versão
        elif ':' in line and not line.startswith('{'):
            parts = line.split(':', 1)
            if len(parts) == 2:
                component_name = parts[0].strip()
                version = parts[1].strip()
                
                # Suporta múltiplos componentes com a mesma versão
                if ',' in component_name:
                    comp_names = [c.strip() for c in component_name.split(',')]
                    for comp in comp_names:
                        if comp:
                            components[comp] = version
                else:
                    components[component_name] = version
        
        # Formato: componente versão (separado por espaço)
        else:
            parts = line.split()
            if len(parts) >= 2 and re.match(r'^\d+\.\d+', parts[-1]):
                version = parts[-1]
                component_name = ' '.join(parts[:-1])
                components[component_name] = version
            # Apenas nome do componente
            elif len(parts) == 1:
                components[parts[0]] = ""
            # Lista separada por vírgulas
            elif ',' in line:
                comp_names = [c.strip() for c in line.split(',')]
                for comp in comp_names:
                    if comp:
                        components[comp] = ""
    
    return components


def extract_blizzdesign_components(blizzdesign_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extrai informações de componentes do export do BlizzDesign.

    Extração aprimorada que lida com vários formatos de export do BlizzDesign
    e fornece metadados adicionais.

    Args:
        blizzdesign_data: Dados brutos do export do BlizzDesign.

    Returns:
        Lista de dicionários de componentes com nome, estereótipo e metadados.

    Example:
        >>> data = {
        ...     "elements": [
        ...         {
        ...             "name": "user-service",
        ...             "type": "ArchiMate:ApplicationComponent",
        ...             "stereotype": "NOVO",
        ...             "properties": {"version": "1.0.0"}
        ...         }
        ...     ]
        ... }
        >>> extract_blizzdesign_components(data)
        [{'name': 'user-service', 'stereotype': 'NOVO', 'version': '1.0.0'}]
    """
    components = []
    
    elements = blizzdesign_data.get("elements", [])
    for element in elements:
        element_type = element.get("type", "")
        
        # Filtra apenas componentes de aplicação
        if any(comp_type in element_type for comp_type in 
               ["ApplicationComponent", "Component", "Service"]):
            
            component_info = {
                "name": element.get("name", ""),
                "stereotype": element.get("stereotype", "INDEFINIDO"),
                "type": element_type.split(":")[-1] if ":" in element_type else element_type
            }
            
            # Adiciona propriedades adicionais se disponíveis
            properties = element.get("properties", {})
            if "version" in properties:
                component_info["version"] = properties["version"]
            
            # Metadados opcionais
            if "description" in element:
                component_info["description"] = element["description"]
            
            if "id" in element:
                component_info["id"] = element["id"]
            
            components.append(component_info)
    
    return components


def format_component_status_summary(components_by_status: Dict[str, List[str]]) -> str:
    """Formata um resumo de componentes agrupados por status.

    Cria um resumo legível dos status dos componentes com contagens
    e indicadores visuais.

    Args:
        components_by_status: Dicionário mapeando status para listas de componentes.

    Returns:
        String de resumo formatada.

    Example:
        >>> status_data = {
        ...     "NOVO": ["service-a", "service-b"],
        ...     "ALTERADO": ["service-c"],
        ...     "REMOVIDO": []
        ... }
        >>> print(format_component_status_summary(status_data))
        📊 Resumo de Status dos Componentes:
        
        🆕 NOVO (2):
          • service-a
          • service-b
        
        🔄 ALTERADO (1):
          • service-c
        
        ❌ REMOVIDO (0):
          Nenhum
    """
    status_icons = {
        "NOVO": "🆕",
        "ALTERADO": "🔄",
        "REMOVIDO": "❌",
        "MANTIDO": "✅",
        "INDEFINIDO": "❓"
    }
    
    result = ["📊 Resumo de Status dos Componentes:"]
    result.append("")
    
    for status, components in components_by_status.items():
        icon = status_icons.get(status, "•")
        count = len(components)
        
        result.append(f"{icon} {status} ({count}):")
        
        if components:
            # Limita a exibição para evitar output muito longo
            for comp in components[:5]:
                result.append(f"  • {comp}")
            if len(components) > 5:
                result.append(f"  ... e mais {len(components) - 5}")
        else:
            result.append("  Nenhum")
        
        result.append("")
    
    return "\n".join(result).strip()


def format_architecture_validation_report(
    validation_result: Dict[str, Any],
    include_details: bool = True
) -> str:
    """Formata um relatório abrangente de validação de arquitetura.

    Cria um relatório detalhado dos resultados de validação de arquitetura
    com estatísticas e informações acionáveis.

    Args:
        validation_result: Resultado de validação de validate_components_vs_architecture.
        include_details: Se deve incluir listas detalhadas de componentes.

    Returns:
        String de relatório formatada.

    Example:
        >>> result = {
        ...     "validation_summary": {"total": 10, "found": 8, "missing": 2, "success_rate": "80.0%"},
        ...     "status_breakdown": {"NOVO": ["service-a"], "ALTERADO": ["service-b"]},
        ...     "missing_components": ["service-x", "service-y"]
        ... }
        >>> print(format_architecture_validation_report(result))
        📋 Relatório de Validação de Arquitetura
        ========================================
        ...
    """
    lines = ["📋 Relatório de Validação de Arquitetura", "=" * 40]
    
    # Seção de resumo
    if "validation_summary" in validation_result:
        summary = validation_result["validation_summary"]
        lines.extend([
            "",
            "📊 Resumo:",
            f"  Total de Componentes: {summary.get('total', 0)}",
            f"  Encontrados: {summary.get('found', 0)}",
            f"  Ausentes: {summary.get('missing', 0)}",
            f"  Taxa de Sucesso: {summary.get('success_rate', '0%')}",
            ""
        ])
    
    # Seção de breakdown por status
    if "status_breakdown" in validation_result and include_details:
        lines.append(format_component_status_summary(
            validation_result["status_breakdown"]
        ))
        lines.append("")
    
    # Seção de componentes ausentes
    if "missing_components" in validation_result:
        missing = validation_result["missing_components"]
        if missing:
            lines.extend([
                "❌ Componentes Ausentes:",
                *[f"  • {comp}" for comp in missing],
                ""
            ])
    
    # Seção de componentes encontrados (com detalhes limitados)
    if "found_components" in validation_result and include_details:
        found = validation_result["found_components"]
        if found:
            lines.append("✅ Componentes Encontrados:")
            for comp_name, details in list(found.items())[:10]:
                lines.append(f"  • {comp_name}")
                lines.append(f"    Status: {details.get('status', 'Desconhecido')}")
                lines.append(f"    Versão: {details.get('version', 'N/A')}")
            if len(found) > 10:
                lines.append(f"  ... e mais {len(found) - 10}")
            lines.append("")
    
    # Rodapé do relatório
    lines.extend([
        "",
        f"Gerado em: {format_timestamp()}",
        "=" * 40
    ])
    
    return "\n".join(lines)


def parse_jira_components(components_data: List[Dict[str, Any]]) -> List[str]:
    """Extrai nomes de componentes dos dados do campo de componentes do Jira.

    A API do Jira frequentemente retorna componentes como uma lista de objetos.
    Esta função extrai apenas o 'name' de cada objeto.

    Args:
        components_data: Os dados brutos de componentes da API do Jira,
                         tipicamente uma lista de dicionários.

    Returns:
        Uma lista de strings com nomes de componentes.

    Example:
        >>> data = [{'id': '1', 'name': 'user-service'}, {'id': '2', 'name': 'auth-module'}]
        >>> parse_jira_components(data)
        ['user-service', 'auth-module']
        >>> parse_jira_components(None)
        []
    """
    if not isinstance(components_data, list):
        return []
    
    return [
        name for comp in components_data
        if isinstance(comp, dict) and (name := comp.get("name")) is not None
    ]


def parse_development_cycle(cycle_data: Any) -> str:
    """Analisa o ciclo de desenvolvimento de um campo customizado do Jira.

    Lida com diferentes estruturas de dados que um campo customizado pode ter
    (ex: uma string ou um dicionário com chave 'value').

    Args:
        cycle_data: Os dados brutos do campo customizado do Jira.

    Returns:
        O ciclo de desenvolvimento como string, ou string vazia se não encontrado.

    Example:
        >>> parse_development_cycle({'value': 'Sprint 23'})
        'Sprint 23'
        >>> parse_development_cycle('Sprint 24')
        'Sprint 24'
        >>> parse_development_cycle(None)
        ''
    """
    if isinstance(cycle_data, dict):
        # Formato de campo customizado do Jira
        return cycle_data.get("value", "")
    
    if isinstance(cycle_data, str):
        return cycle_data
        
    return ""


def format_validation_scope(
    development_cycle: str, 
    architecture: str, 
    components: List[str]
) -> str:
    """Formata o escopo de validação para documentação.

    Cria uma seção estruturada do escopo da validação de aderência
    em formato Wiki/Confluence para documentação formal.

    Args:
        development_cycle: Ciclo de desenvolvimento atual.
        architecture: Nome da arquitetura de referência.
        components: Lista de componentes no escopo.

    Returns:
        String formatada em markup Wiki para o escopo de validação.

    Example:
        >>> scope = format_validation_scope("Sprint 23", "Microservices v2", ["service-a", "service-b"])
        >>> print(scope)
        h2. Escopo da Validação de Aderência
        *Ciclo de Desenvolvimento:* Sprint 23
        *Arquitetura de Referência:* Microservices v2
        
        h3. Componentes no Escopo:
        * service-a
        * service-b
    """
    lines = [
        "h2. Escopo da Validação de Aderência",
        f"*Ciclo de Desenvolvimento:* {development_cycle or 'Não informado'}",
        f"*Arquitetura de Referência:* {architecture or 'Não informada'}",
        "",
        "h3. Componentes no Escopo:"
    ]
    
    if components:
        for component in components:
            lines.append(f"* {component}")
    else:
        lines.append("_Nenhum componente informado._")
        
    return "\n".join(lines)


def format_version_changes(version_changes: List[Dict[str, str]]) -> str:
    """Formata alterações de versão em formato de tabela Wiki.

    Cria uma tabela estruturada das alterações de versão dos componentes
    em formato Wiki/Confluence para documentação.

    Args:
        version_changes: Lista de dicionários com informações de mudança de versão.
                         Cada dicionário deve conter 'component', 'from_version', 'to_version'.

    Returns:
        String formatada em markup Wiki com tabela de alterações.

    Example:
        >>> changes = [
        ...     {"component": "user-service", "from_version": "1.0.0", "to_version": "1.1.0"},
        ...     {"component": "auth-module", "from_version": "2.0.0", "to_version": "2.1.0"}
        ... ]
        >>> print(format_version_changes(changes))
        h2. Alterações de Versão dos Componentes
        ||Componente||Versão Anterior||Nova Versão||
        |user-service|1.0.0|1.1.0|
        |auth-module|2.0.0|2.1.0|
    """
    if not version_changes:
        return "h3. Alterações de Versão\n_Nenhuma alteração de versão detectada._"

    lines = [
        "h2. Alterações de Versão dos Componentes",
        "||Componente||Versão Anterior||Nova Versão||"
    ]
    
    for change in version_changes:
        component = change.get("component", "N/A")
        from_version = change.get("from_version", "N/A")
        to_version = change.get("to_version", "N/A")
        lines.append(f"|{component}|{from_version}|{to_version}|")
        
    return "\n".join(lines)
