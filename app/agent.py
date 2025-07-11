from google.adk.agents import Agent
import json
import os

def load_reports():
    """Carrega relatórios da pasta data"""
    reports = []
    base_path = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    if not os.path.exists(base_path):
        return reports
    
    try:
        for file in os.listdir(base_path):
            if file.endswith('.json'):
                with open(os.path.join(base_path, file), 'r') as f:
                    report = json.load(f)
                    report['_source_file'] = file
                    reports.append(report)
    except Exception:
        pass
    
    return reports

def load_criterios():
    """Carrega critérios da pasta criterios (TXT) e arquivo criterios.json"""
    criterios_text = ""
    
    # Carrega criterios.json da raiz do projeto
    criterios_json_path = os.path.join(os.path.dirname(__file__), '..', 'criterios.json')
    if os.path.exists(criterios_json_path):
        try:
            with open(criterios_json_path, 'r', encoding='utf-8') as f:
                criterios_json = json.load(f)
                criterios_text += "=== CRITÉRIOS DE CONFORMIDADE (JSON) ===\n\n"
                for key, value in criterios_json.items():
                    criterios_text += f"- {key.upper().replace('_', ' ')}: {value}\n"
                criterios_text += "\n"
        except Exception as e:
            criterios_text += f"ERRO: Erro ao carregar criterios.json: {e}\n\n"
    
    # Carrega critérios TXT da pasta criterios (mantém compatibilidade)
    criterios_path = os.path.join(os.path.dirname(__file__), '..', 'criterios')
    if os.path.exists(criterios_path):
        try:
            criterios_text += "=== CRITÉRIOS DE CONFORMIDADE (TXT) ===\n\n"
            for file in os.listdir(criterios_path):
                if file.endswith('.txt'):
                    criterios_text += f"--- {file.upper()} ---\n"
                    with open(os.path.join(criterios_path, file), 'r', encoding='utf-8') as f:
                        criterios_text += f.read() + "\n\n"
        except Exception as e:
            criterios_text += f"ERRO: Erro ao carregar critérios TXT: {e}\n\n"
    
    if not criterios_text:
        return "ERRO: Nenhum critério encontrado (criterios.json ou pasta criterios/)"
    
    return criterios_text

def analisar_conformidade(pergunta: str = "") -> str:
    """Analisa conformidade cruzando dados com critérios"""
    reports = load_reports()
    criterios = load_criterios()
    
    if not reports:
        return "ERRO: Nenhum relatório encontrado na pasta data/"
    
    if "ERRO" in criterios:
        return criterios  # Retorna erro se houver
    
    # Preparar contexto completo para o Gemini
    context = f"""
MISSÃO: Analisar conformidade técnica cruzando DADOS vs CRITÉRIOS

DADOS DOS SISTEMAS:
{json.dumps(reports, indent=2, ensure_ascii=False)}

{criterios}

PERGUNTA DO USUÁRIO: {pergunta}

INSTRUÇÕES DE ANÁLISE:
1. Compare cada sistema nos dados com os critérios aplicáveis (JSON e TXT)
2. Para critérios JSON, verifique se cada campo está implementado conforme esperado
3. Identifique conformidades ([CONFORME]) e não-conformidades ([NÃO CONFORME])
4. Use [PARCIAL] para conformidade parcial
5. Seja específico: cite valores exatos vs critérios
6. Priorize criticidade CRÍTICA > ALTA > MÉDIA
7. Sugira ações corretivas para não-conformidades
8. Foque no tipo de sistema da pergunta (PIX, ETL, Mobile, Arquitetura, etc.)

FORMATO DE RESPOSTA:
SISTEMA: [nome]
ANÁLISE:
   [CONFORME/NÃO CONFORME/PARCIAL] [Critério]: [Status] - [Justificativa]
AÇÕES: [Recomendações]

CRITÉRIOS ESPECIAIS JSON:
- Verifique se componentes foram implementados conforme proposto
- Valide se comunicação está operando corretamente
- Confirme se plataformização foi aplicada (backend/frontend)
- Verifique configurações de escalabilidade (vertical/horizontal)
- Confirme se patterns como EDA estão implementados
"""
    
    return context

root_agent = Agent(
    name="feito_conferido_agent",
    model="gemini-2.0-flash",
    description="Especialista em análise de conformidade que cruza dados com critérios definidos",
    instruction="""Você é o FEITO CONFERIDO - analista de conformidade técnica.

Use analisar_conformidade para:
- Cruzar dados dos sistemas com critérios da pasta criterios/
- Identificar conformidades e não-conformidades
- Priorizar por criticidade (CRÍTICA > ALTA > MÉDIA)
- Ser específico com valores e evidências
- Sugerir ações corretivas

Seja técnico, objetivo e focado em resultados acionáveis.""",
    tools=[analisar_conformidade]
)
