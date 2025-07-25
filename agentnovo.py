from google.adk.agents import Agent
import json
import os
import re
from pathlib import Path
from datetime import datetime
import requests
from typing import Dict, List, Optional

# Configuração automática de credenciais
def setup_credentials():
    """Configura credenciais automaticamente baseado no ambiente"""
    
    # Prioridade 1: Verificar se já existe GOOGLE_API_KEY no ambiente
    if os.getenv('GOOGLE_API_KEY'):
        print("Usando GOOGLE_API_KEY do ambiente")
        return True
    
    # Prioridade 2: Verificar se já existe GOOGLE_APPLICATION_CREDENTIALS
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("Usando GOOGLE_APPLICATION_CREDENTIALS do ambiente")
        return True
    
    # Prioridade 3: Tentar usar Application Default Credentials (gcloud)
    try:
        import subprocess
        result = subprocess.run(['gcloud', 'auth', 'application-default', 'print-access-token'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            print("Usando Application Default Credentials (gcloud)")
            return True
    except:
        pass
    
    print("Nenhuma credencial encontrada automaticamente")
    print("Configure uma das opcoes:")
    print("   - export GOOGLE_API_KEY='sua-api-key'")
    print("   - export GOOGLE_APPLICATION_CREDENTIALS='caminho-para-service-account.json'") 
    print("   - gcloud auth application-default login")
    return False

# Configurar credenciais automaticamente
setup_credentials()

def load_architecture_data():
    """Carrega dados arquiteturais da pasta data/"""
    data_dir = Path("data")
    architecture_data = []
    
    if not data_dir.exists():
        return {"erro": "Pasta data/ nao encontrada"}
    
    for json_file in data_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['_source_file'] = json_file.name
                architecture_data.append(data)
        except Exception as e:
            print(f"Erro ao carregar {json_file}: {e}")
    
    return architecture_data

def parse_component_list_from_text(text: str):
    """Extrai componentes do texto enviado pelo usuário"""
    components = {}
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Padrão: "componente -> versão"
        if '->' in line:
            parts = line.split(' -> ')
            if len(parts) == 2:
                component_name = parts[0].strip()
                version = parts[1].strip()
                components[component_name] = version
        
        # Padrão: "componente: versão"
        elif ':' in line and not line.startswith('{'):
            parts = line.split(':', 1)
            if len(parts) == 2:
                component_name = parts[0].strip()
                version = parts[1].strip()
                components[component_name] = version
    
    return components

def validar_componentes_vs_arquitetura(input_text: str = "") -> str:
    """Valida componentes enviados pelo usuário contra arquitetura JSON"""
    
    if not input_text.strip():
        return """**Por favor, envie sua lista de componentes!**

**Formato esperado:**
```
caapi-hubd-base-avaliacao-v1 -> 1.3.2
flutmicro-hubd-base-app-rating -> 2.0.1
ng15-hubd-base-portal-configuracao -> 1.1.1
```"""
    
    # Extrai componentes do texto
    components = parse_component_list_from_text(input_text)
    
    if not components:
        return f"""**Nao consegui extrair componentes do texto.**

**Texto recebido:**
```
{input_text[:100]}...
```

**Use o formato:** componente -> versao"""
    
    # Carrega arquitetura
    arch_data = load_architecture_data()
    if isinstance(arch_data, dict) and "erro" in arch_data:
        return f"Erro: {arch_data['erro']}"
    
    if not arch_data:
        return "Erro: Nenhum arquivo JSON encontrado na pasta data/"
    
    # Validação
    result = []
    result.append("**VALIDACAO DE COMPONENTES**\n")
    
    result.append(f"**COMPONENTES ENVIADOS:** ({len(components)})")
    for comp_name, version in components.items():
        result.append(f"  - {comp_name} -> {version}")
    result.append("")
    
    found_components = {}
    missing_components = []
    
    for arch_file in arch_data:
        source_file = arch_file.get('_source_file', 'unknown')
        elements = arch_file.get('elements', [])
        
        result.append(f"**{source_file}:**")
        
        for comp_name, expected_version in components.items():
            found = False
            
            for element in elements:
                element_name = element.get('name', '')
                stereotype = element.get('stereotype', '')
                
                if comp_name in element_name:
                    found = True
                    found_components[comp_name] = True
                    
                    status_label = ""
                    if stereotype == 'NOVO':
                        status_label = "NOVO"
                    elif stereotype == 'ALTERADO':
                        status_label = "ALTERADO"
                    elif stereotype == 'REMOVIDO':
                        status_label = "REMOVIDO"
                    else:
                        status_label = "INDEFINIDO"
                    
                    result.append(f"  [{status_label}] **{comp_name}** -> {expected_version}")
                    break
            
            if not found:
                missing_components.append(comp_name)
    
    if missing_components:
        result.append(f"\n**NAO ENCONTRADOS:** ({len(missing_components)})")
        for comp in missing_components:
            result.append(f"  - {comp}")
    
    # Estatísticas
    total = len(components)
    found = len(found_components)
    missing = len(missing_components)
    
    result.append(f"\n**RESUMO:**")
    result.append(f"  - Total: {total}")
    result.append(f"  - Encontrados: {found}")
    result.append(f"  - Nao encontrados: {missing}")
    result.append(f"  - Taxa de sucesso: {(found/total*100):.1f}%")
    
    if missing == 0:
        result.append(f"\n**TODOS OS COMPONENTES VALIDADOS!**")
    else:
        result.append(f"\n**ALGUNS COMPONENTES NAO ENCONTRADOS**")
    
    return "\n".join(result)

def buscar_componente_especifico(nome_componente: str = "") -> str:
    """Busca um componente específico"""
    if not nome_componente.strip():
        return "Erro: Informe o nome do componente"
    
    arch_data = load_architecture_data()
    if isinstance(arch_data, dict) and "erro" in arch_data:
        return f"Erro: {arch_data['erro']}"
    
    result = []
    result.append(f"**BUSCA: '{nome_componente}'**\n")
    
    found = []
    for arch_file in arch_data:
        elements = arch_file.get('elements', [])
        for element in elements:
            element_name = element.get('name', '')
            if nome_componente.lower() in element_name.lower():
                found.append({
                    'name': element_name,
                    'type': element.get('type', ''),
                    'stereotype': element.get('stereotype', ''),
                    'file': arch_file.get('_source_file', 'unknown')
                })
    
    if found:
        result.append(f"**ENCONTRADOS:** ({len(found)})")
        for item in found:
            stereotype = item['stereotype']
            status_label = f"[{stereotype}]" if stereotype else "[INDEFINIDO]"
            
            result.append(f"  {status_label} {item['name']}")
            result.append(f"    Arquivo: {item['file']}")
            result.append(f"    Tipo: {item['type']}")
            result.append("")
    else:
        result.append("Componente nao encontrado")
    
    return "\n".join(result)

def listar_todos_componentes(query: str = "") -> str:
    """Lista todos os componentes"""
    arch_data = load_architecture_data()
    if isinstance(arch_data, dict) and "erro" in arch_data:
        return f"Erro: {arch_data['erro']}"
    
    result = []
    result.append("**TODOS OS COMPONENTES**\n")
    
    total_components = 0
    
    for arch_file in arch_data:
        source_file = arch_file.get('_source_file', 'unknown')
        elements = arch_file.get('elements', [])
        
        components = [e for e in elements if e.get('type') == 'ArchiMate:ApplicationComponent']
        
        if components:
            result.append(f"**{source_file}** ({len(components)} componentes):")
            
            novos = [c for c in components if c.get('stereotype') == 'NOVO']
            alterados = [c for c in components if c.get('stereotype') == 'ALTERADO']
            removidos = [c for c in components if c.get('stereotype') == 'REMOVIDO']
            
            if novos:
                result.append(f"  **NOVOS:** ({len(novos)})")
                for comp in novos[:3]:
                    result.append(f"    - {comp['name']}")
                if len(novos) > 3:
                    result.append(f"    ... e mais {len(novos)-3}")
            
            if alterados:
                result.append(f"  **ALTERADOS:** ({len(alterados)})")
                for comp in alterados[:3]:
                    result.append(f"    - {comp['name']}")
                if len(alterados) > 3:
                    result.append(f"    ... e mais {len(alterados)-3}")
            
            if removidos:
                result.append(f"  **REMOVIDOS:** ({len(removidos)})")
                for comp in removidos[:3]:
                    result.append(f"    - {comp['name']}")
                if len(removidos) > 3:
                    result.append(f"    ... e mais {len(removidos)-3}")
            
            result.append("")
            total_components += len(components)
    
    result.append(f"**TOTAL GERAL:** {total_components} componentes")
    
    return "\n".join(result)

def buscar_aprovacao_por_ciclo(ciclo_id: str = "") -> str:
    """Busca aprovação específica por ID do ciclo (C-XXXXXX)"""
    if not ciclo_id.strip():
        return "Erro: Informe o ID do ciclo (formato: C-XXXXXX)"
    
    # Validar formato do ID
    if not re.match(r'^C-\d{6}$', ciclo_id.upper()):
        return "Erro: Formato invalido. Use: C-XXXXXX (exemplo: C-123456)"
    
    # Placeholder para integração futura
    result = []
    result.append(f"**BUSCA DE APROVACAO - CICLO: {ciclo_id.upper()}**\n")
    result.append("Status: Implementacao pendente")
    result.append("Requer integracao com sistema de aprovacoes")
    result.append("\nFuncionalidades planejadas:")
    result.append("- Busca em base de dados de aprovacoes")
    result.append("- Validacao de status contra padroes")
    result.append("- Historico de modificacoes")
    
    return "\n".join(result)

def validar_status_aprovacao(ticket_id: str = "") -> str:
    """Valida status de aprovação contra padrões arquiteturais"""
    if not ticket_id.strip():
        return "Erro: Informe o ID do ticket"
    
    # Placeholder para integração futura
    result = []
    result.append(f"**VALIDACAO DE STATUS - TICKET: {ticket_id}**\n")
    result.append("Status: Implementacao pendente")
    result.append("Requer integracao com Jira/ARQCOR")
    result.append("\nFuncionalidades planejadas:")
    result.append("- Validacao automatica de status")
    result.append("- Verificacao de conformidade")
    result.append("- Identificacao de desvios")
    
    return "\n".join(result)

def gerar_relatorio_conformidade(periodo: str = "") -> str:
    """Gera relatório abrangente de conformidade com métricas"""
    arch_data = load_architecture_data()
    if isinstance(arch_data, dict) and "erro" in arch_data:
        return f"Erro: {arch_data['erro']}"
    
    result = []
    result.append("**RELATORIO DE CONFORMIDADE**\n")
    result.append(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    if periodo:
        result.append(f"Periodo: {periodo}")
    result.append("")
    
    total_components = 0
    novos = 0
    alterados = 0
    removidos = 0
    
    for arch_file in arch_data:
        elements = arch_file.get('elements', [])
        components = [e for e in elements if e.get('type') == 'ArchiMate:ApplicationComponent']
        
        for comp in components:
            total_components += 1
            stereotype = comp.get('stereotype', '')
            if stereotype == 'NOVO':
                novos += 1
            elif stereotype == 'ALTERADO':
                alterados += 1
            elif stereotype == 'REMOVIDO':
                removidos += 1
    
    result.append("**METRICAS GERAIS:**")
    result.append(f"Total de componentes: {total_components}")
    result.append(f"Componentes novos: {novos} ({(novos/total_components*100):.1f}%)")
    result.append(f"Componentes alterados: {alterados} ({(alterados/total_components*100):.1f}%)")
    result.append(f"Componentes removidos: {removidos} ({(removidos/total_components*100):.1f}%)")
    result.append("")
    
    result.append("**CONFORMIDADE POR ARQUIVO:**")
    for arch_file in arch_data:
        source_file = arch_file.get('_source_file', 'unknown')
        elements = arch_file.get('elements', [])
        components = [e for e in elements if e.get('type') == 'ArchiMate:ApplicationComponent']
        
        if components:
            result.append(f"- {source_file}: {len(components)} componentes")
    
    return "\n".join(result)

def analisar_performance_arquiteto(arquiteto_nome: str = "") -> str:
    """Analisa métricas individuais de performance de arquitetos"""
    if not arquiteto_nome.strip():
        return "Erro: Informe o nome do arquiteto"
    
    # Placeholder para integração futura
    result = []
    result.append(f"**ANALISE DE PERFORMANCE - ARQUITETO: {arquiteto_nome}**\n")
    result.append("Status: Implementacao pendente")
    result.append("Requer integracao com sistema de auditoria")
    result.append("\nMetricas planejadas:")
    result.append("- Taxa de aprovacao/rejeicao")
    result.append("- Tempo medio de validacao")
    result.append("- Tipos de nao-conformidades identificadas")
    result.append("- Historico de decisoes")
    
    return "\n".join(result)

def listar_debito_tecnico_aberto() -> str:
    """Lista issues de débito técnico em aberto"""
    # Placeholder para integração futura
    result = []
    result.append("**DEBITO TECNICO EM ABERTO**\n")
    result.append("Status: Implementacao pendente")
    result.append("Requer integracao com sistema de tickets")
    result.append("\nFuncionalidades planejadas:")
    result.append("- Lista de issues abertas")
    result.append("- Priorizacao por impacto")
    result.append("- Estimativa de esforco")
    result.append("- Rastreamento de progresso")
    
    return "\n".join(result)

def validar_repositorio_codigo(repo_url: str = "") -> str:
    """Valida repositório de código fonte"""
    if not repo_url.strip():
        return "Erro: Informe a URL do repositorio"
    
    # Validação básica de URL
    if not (repo_url.startswith('http://') or repo_url.startswith('https://')):
        return "Erro: URL invalida. Use formato: https://github.com/user/repo"
    
    # Placeholder para integração futura
    result = []
    result.append(f"**VALIDACAO DE REPOSITORIO**\n")
    result.append(f"URL: {repo_url}")
    result.append("Status: Implementacao pendente")
    result.append("\nValidacoes planejadas:")
    result.append("- Verificacao de estrutura do projeto")
    result.append("- Analise de dependencias")
    result.append("- Verificacao de especificacao OpenAPI")
    result.append("- Validacao de padroes de codigo")
    result.append("- Verificacao de testes")
    
    return "\n".join(result)

def verificar_openapi_spec(componente: str = "") -> str:
    """Verifica se especificação OpenAPI existe"""
    if not componente.strip():
        return "Erro: Informe o nome do componente"
    
    # Placeholder para integração futura
    result = []
    result.append(f"**VERIFICACAO OPENAPI - COMPONENTE: {componente}**\n")
    result.append("Status: Implementacao pendente")
    result.append("Requer acesso ao repositorio de codigo")
    result.append("\nVerificacoes planejadas:")
    result.append("- Presenca de arquivo openapi.yaml/swagger.json")
    result.append("- Validacao de estrutura da especificacao")
    result.append("- Verificacao de completude")
    result.append("- Conformidade com padroes")
    
    return "\n".join(result)

def criar_formulario_arqcor(ticket_id: str = "") -> str:
    """Cria formulário ARQCOR"""
    if not ticket_id.strip():
        return "Erro: Informe o ID do ticket"
    
    # Placeholder para integração futura
    result = []
    result.append(f"**CRIACAO FORMULARIO ARQCOR - TICKET: {ticket_id}**\n")
    result.append("Status: Implementacao pendente")
    result.append("Requer integracao com sistema ARQCOR")
    result.append("\nFuncionalidades planejadas:")
    result.append("- Criacao automatica de formulario")
    result.append("- Preenchimento de dados basicos")
    result.append("- Vinculacao com ticket origem")
    result.append("- Rastreamento de status")
    
    return "\n".join(result)

def validar_ticket_jira(ticket_id: str = "") -> str:
    """Valida ticket Jira (PDI ou JT)"""
    if not ticket_id.strip():
        return "Erro: Informe o ID do ticket"
    
    # Validação básica de formato
    if not (ticket_id.upper().startswith('PDI-') or ticket_id.upper().startswith('JT-')):
        return "Erro: Formato invalido. Use: PDI-XXXXX ou JT-XXXXX"
    
    # Placeholder para integração futura
    result = []
    result.append(f"**VALIDACAO TICKET JIRA: {ticket_id.upper()}**\n")
    result.append("Status: Implementacao pendente")
    result.append("Requer integracao com Jira API")
    result.append("\nValidacoes planejadas:")
    result.append("- Status do ticket")
    result.append("- Campos obrigatorios preenchidos")
    result.append("- Anexos necessarios")
    result.append("- Aprovacoes pendentes")
    
    return "\n".join(result)

def validate_feito_conferido(ticket_id: str = "", evaluator_name: str = "", tool_context: str = "") -> str:
    """Ferramenta principal de validação completa - 4 estágios"""
    if not ticket_id.strip():
        return "Erro: Informe o ID do ticket"
    
    if not evaluator_name.strip():
        return "Erro: Informe o nome do avaliador"
    
    result = []
    result.append("**VALIDACAO FEITO CONFERIDO**\n")
    result.append(f"Ticket: {ticket_id}")
    result.append(f"Avaliador: {evaluator_name}")
    result.append(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    result.append("")
    
    # Simulação dos 4 estágios
    stages = [
        "1. Validacao de componentes contra VT",
        "2. Criacao de formulario ARQCOR", 
        "3. Verificacao de versoes com Component Portal Tech",
        "4. Validacao de codigo/contrato"
    ]
    
    result.append("**ESTAGIOS DE VALIDACAO:**")
    for stage in stages:
        result.append(f"  {stage}")
    result.append("")
    
    result.append("**STATUS ATUAL:**")
    result.append("- Status geral: REQUIRES_MANUAL_ACTION")
    result.append("- Estagios completados: 0/4")
    result.append("- Implementacao pendente para integracao completa")
    result.append("")
    
    result.append("**ACOES MANUAIS NECESSARIAS:**")
    result.append("- Configurar integracao com sistemas externos")
    result.append("- Implementar validacoes especificas")
    result.append("- Configurar acesso a repositorios")
    
    return "\n".join(result)

def test_credentials():
    """Testa se as credenciais estão funcionando"""
    try:
        # Teste simples criando um agente
        test_agent = Agent(
            name="test_agent",
            model="gemini-2.0-flash",
            description="Teste de credenciais"
        )
        return "Credenciais configuradas corretamente!"
    except Exception as e:
        return f"Erro nas credenciais: {str(e)}"

# Criar o agente principal
try:
    root_agent = Agent(
        name="meu_validador_componentes",
        model="gemini-2.0-flash",
        description="Meu assistente para analise de componentes e validacao arquitetural",
        instruction="""Voce e meu assistente especializado em analise e validacao de componentes arquiteturais.

SUAS FUNCOES:

1. Controle de Validacoes
- Localizar informacoes por codigo de ciclo (formato C-XXXXXX)
- Verificar conformidade com diretrizes estabelecidas
- Manter registro de alteracoes e atualizacoes

2. Geração de Reports
- Criar documentos de analise com dados quantitativos
- Apresentar indices de aderencia aos padroes
- Mapear inconsistencias entre diferentes modulos

3. Avaliacao de Qualidade
- Examinar indicadores de trabalho de especialistas
- Monitorar indices de aprovacao em processos
- Documentar atividades para controle interno

4. Controle de Pendencias
- Catalogar questoes tecnicas pendentes
- Classificar por nivel de criticidade
- Acompanhar resolucoes

5. Analise de Codigo Fonte
- Examinar estruturas de repositorios
- Confirmar presenca de documentacao tecnica
- Verificar organizacao de projetos

COMANDOS QUE ACEITO:
- Lista de componentes -> validar_componentes_vs_arquitetura
- "buscar X" -> buscar_componente_especifico  
- "listar" -> listar_todos_componentes
- "ciclo C-XXXXXX" -> buscar_aprovacao_por_ciclo
- "ticket PDI-XXXXX" -> validar_ticket_jira
- "relatorio" -> gerar_relatorio_conformidade
- "arquiteto NOME" -> analisar_performance_arquiteto
- "debito" -> listar_debito_tecnico_aberto
- "repo URL" -> validar_repositorio_codigo
- "openapi COMPONENTE" -> verificar_openapi_spec
- "validar TICKET AVALIADOR" -> validate_feito_conferido

Meu foco e fornecer informacoes precisas e dados concretos.""",
        tools=[
            validar_componentes_vs_arquitetura,
            buscar_componente_especifico,
            listar_todos_componentes,
            buscar_aprovacao_por_ciclo,
            validar_status_aprovacao,
            gerar_relatorio_conformidade,
            analisar_performance_arquiteto,
            listar_debito_tecnico_aberto,
            validar_repositorio_codigo,
            verificar_openapi_spec,
            criar_formulario_arqcor,
            validar_ticket_jira,
            validate_feito_conferido
        ]
    )
    print("Agente criado com sucesso!")
    print("Status das credenciais:", test_credentials())
    
except Exception as e:
    print(f"Erro ao criar agente: {e}")
    print("\nSolucoes possiveis:")
    print("1. Configure uma API Key:")
    print("   os.environ['GOOGLE_API_KEY'] = 'sua-api-key'")
    print("\n2. Ou configure Service Account:")
    print("   os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'caminho-para-json'")
    print("\n3. Ou execute 'gcloud auth application-default login'")