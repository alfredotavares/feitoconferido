from google.adk.agents import Agent
import json
import os
import re
from pathlib import Path

def load_arch_data():
    """carrega jsons da pasta data - bem simples"""
    data_dir = Path("data")
    arch_data = []
    
    if not data_dir.exists():
        return {"erro": "pasta data nao existe"}
    
    # pega todos os .json da pasta
    for f in data_dir.glob("*.json"):
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                data['_file'] = f.name
                arch_data.append(data)
        except Exception as e:
            print(f"erro carregando {f}: {e}")
    
    return arch_data

def parse_components(text):
    """extrai componentes do texto - funciona com -> ou :"""
    comps = {}
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # formato: componente -> versao
        if '->' in line:
            parts = line.split(' -> ')
            if len(parts) == 2:
                comp_name = parts[0].strip()
                version = parts[1].strip()
                comps[comp_name] = version
        
        # formato: componente: versao
        elif ':' in line and not line.startswith('{'):
            parts = line.split(':', 1)
            if len(parts) == 2:
                comp_name = parts[0].strip()
                version = parts[1].strip()
                comps[comp_name] = version
    
    return comps

def validar_componentes(input_text: str = "") -> str:
    """valida componentes contra arquitetura"""
    
    if not input_text.strip():
        return """Por favor, envie sua lista de componentes!

Formato esperado:
caapi-hubd-base-avaliacao-v1 -> 1.3.2
flutmicro-hubd-base-app-rating -> 2.0.1
ng15-hubd-base-portal-configuracao -> 1.1.1"""
    
    # extrai componentes
    comps = parse_components(input_text)
    
    if not comps:
        return f"""Nao consegui extrair componentes do texto.

Texto recebido:
{input_text[:100]}...

Use o formato: componente -> versao"""
    
    # carrega dados da arquitetura
    arch_data = load_arch_data()
    if isinstance(arch_data, dict) and "erro" in arch_data:
        return f"ERRO: {arch_data['erro']}"
    
    if not arch_data:
        return "ERRO: nenhum arquivo JSON na pasta data/"
    
    # faz a validacao
    resp = []
    resp.append("=== VALIDACAO DE COMPONENTES ===")
    resp.append("")
    
    resp.append(f"COMPONENTES ENVIADOS: {len(comps)}")
    for comp_name, version in comps.items():
        resp.append(f"  - {comp_name} -> {version}")
    resp.append("")
    
    found_comps = {}
    missing_comps = []
    
    for arch_file in arch_data:
        fname = arch_file.get('_file', 'unknown')
        elements = arch_file.get('elements', [])
        
        resp.append(f"Arquivo: {fname}")
        
        for comp_name, exp_version in comps.items():
            found = False
            
            for element in elements:
                elem_name = element.get('name', '')
                stereotype = element.get('stereotype', '')
                
                # busca simples por substring
                if comp_name in elem_name:
                    found = True
                    found_comps[comp_name] = True
                    
                    status = ""
                    if stereotype == 'NOVO':
                        status = "[NOVO]"
                    elif stereotype == 'ALTERADO':
                        status = "[ALTERADO]"
                    elif stereotype == 'REMOVIDO':
                        status = "[REMOVIDO]"
                    else:
                        status = "[OK]"
                    
                    resp.append(f"  {status} {comp_name} -> {exp_version}")
                    break
            
            if not found:
                missing_comps.append(comp_name)
    
    # lista os que nao foram encontrados
    if missing_comps:
        resp.append("")
        resp.append(f"NAO ENCONTRADOS: {len(missing_comps)}")
        for comp in missing_comps:
            resp.append(f"  - {comp}")
    
    # estatisticas basicas
    total = len(comps)
    found = len(found_comps)
    missing = len(missing_comps)
    
    resp.append("")
    resp.append("=== RESUMO ===")
    resp.append(f"Total: {total}")
    resp.append(f"Encontrados: {found}")
    resp.append(f"Nao encontrados: {missing}")
    resp.append(f"Taxa de sucesso: {(found/total*100):.1f}%")
    
    if missing == 0:
        resp.append("TODOS OS COMPONENTES VALIDADOS!")
    else:
        resp.append("ALGUNS COMPONENTES NAO ENCONTRADOS")
    
    return "\n".join(resp)

def buscar_componente(nome: str = "") -> str:
    """busca um componente especifico"""
    if not nome.strip():
        return "informe o nome do componente"
    
    arch_data = load_arch_data()
    if isinstance(arch_data, dict) and "erro" in arch_data:
        return f"ERRO: {arch_data['erro']}"
    
    resp = []
    resp.append(f"BUSCA: '{nome}'")
    resp.append("")
    
    found = []
    for arch_file in arch_data:
        elements = arch_file.get('elements', [])
        for element in elements:
            elem_name = element.get('name', '')
            if nome.lower() in elem_name.lower():
                found.append({
                    'name': elem_name,
                    'type': element.get('type', ''),
                    'stereotype': element.get('stereotype', ''),
                    'file': arch_file.get('_file', 'unknown')
                })
    
    if found:
        resp.append(f"ENCONTRADOS: {len(found)}")
        for item in found:
            stereotype = item['stereotype']
            if stereotype == 'NOVO':
                status = "[NOVO]"
            elif stereotype == 'ALTERADO':
                status = "[ALTERADO]"
            elif stereotype == 'REMOVIDO':
                status = "[REMOVIDO]"
            else:
                status = "[OK]"
            
            resp.append(f"  {status} {item['name']}")
            resp.append(f"    Arquivo: {item['file']}")
            resp.append(f"    Tipo: {item['type']}")
            resp.append("")
    else:
        resp.append("componente nao encontrado")
    
    return "\n".join(resp)

def listar_componentes(filtro: str = "") -> str:
    """lista todos os componentes"""
    arch_data = load_arch_data()
    if isinstance(arch_data, dict) and "erro" in arch_data:
        return f"ERRO: {arch_data['erro']}"
    
    resp = []
    resp.append("=== TODOS OS COMPONENTES ===")
    resp.append("")
    
    total_comps = 0
    
    for arch_file in arch_data:
        fname = arch_file.get('_file', 'unknown')
        elements = arch_file.get('elements', [])
        
        # filtra so os componentes de aplicacao
        comps = [e for e in elements if e.get('type') == 'ArchiMate:ApplicationComponent']
        
        if comps:
            resp.append(f"{fname} ({len(comps)} componentes):")
            
            # separa por tipo
            novos = [c for c in comps if c.get('stereotype') == 'NOVO']
            alterados = [c for c in comps if c.get('stereotype') == 'ALTERADO']
            removidos = [c for c in comps if c.get('stereotype') == 'REMOVIDO']
            
            if novos:
                resp.append(f"  NOVOS ({len(novos)}):")
                # mostra so os primeiros 3
                for comp in novos[:3]:
                    resp.append(f"    - {comp['name']}")
                if len(novos) > 3:
                    resp.append(f"    ... e mais {len(novos)-3}")
            
            if alterados:
                resp.append(f"  ALTERADOS ({len(alterados)}):")
                for comp in alterados[:3]:
                    resp.append(f"    - {comp['name']}")
                if len(alterados) > 3:
                    resp.append(f"    ... e mais {len(alterados)-3}")
            
            if removidos:
                resp.append(f"  REMOVIDOS ({len(removidos)}):")
                for comp in removidos[:3]:
                    resp.append(f"    - {comp['name']}")
                if len(removidos) > 3:
                    resp.append(f"    ... e mais {len(removidos)-3}")
            
            resp.append("")
            total_comps += len(comps)
    
    resp.append(f"TOTAL GERAL: {total_comps} componentes")
    
    return "\n".join(resp)

# cria o agente
root_agent = Agent(
    name="validador_componentes",
    model="gemini-2.0-flash",
    description="Valida componentes contra arquitetura",
    instruction="""Voce eh um validador de componentes.

Quando o usuario enviar uma lista de componentes no formato:
caapi-hubd-base-avaliacao-v1 -> 1.3.2
flutmicro-hubd-base-app-rating -> 2.0.1

Valide contra a arquitetura JSON na pasta data/

COMANDOS:
- Lista de componentes -> validar_componentes
- "buscar X" -> buscar_componente  
- "listar" -> listar_componentes

Seja direto nas respostas.""",
    tools=[
        validar_componentes,
        buscar_componente,
        listar_componentes
    ]
)