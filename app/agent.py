from google.adk.agents import Agent
import json
import os
import time
from datetime import datetime
from .utils.security_validator import SecurityValidator, AuditLogger, RateLimiter

# Inicializar componentes de segurança
security_validator = SecurityValidator()
audit_logger = AuditLogger()
rate_limiter = RateLimiter()

def load_reports():
    """Carrega relatórios da pasta data com validação de segurança"""
    reports = []
    base_path = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    if not os.path.exists(base_path):
        audit_logger.log_security_event("file_access", f"Diretório data não encontrado: {base_path}")
        return reports
    
    try:
        for file in os.listdir(base_path):
            if file.endswith('.json'):
                file_path = os.path.join(base_path, file)
                
                # Validação de segurança do arquivo
                if not security_validator.validate_file_path(file) or not security_validator.validate_file_size(file_path):
                    audit_logger.log_security_event("file_validation", f"Arquivo rejeitado: {file}")
                    continue
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Validação de conteúdo
                    if not security_validator.validate_input_length(content):
                        audit_logger.log_security_event("content_validation", f"Arquivo muito grande: {file}")
                        continue
                    
                    report = json.loads(content)
                    
                    # Validação de estrutura JSON
                    is_valid, error_msg = security_validator.validate_json_structure(report, "aprovacao")
                    audit_logger.log_json_validation(file, is_valid, error_msg)
                    
                    if is_valid:
                        report['_source_file'] = file
                        report['_file_hash'] = security_validator.generate_hash(content)
                        reports.append(report)
                
                audit_logger.log_data_access("system", file, "read")
                
    except Exception as e:
        audit_logger.log_security_event("file_error", f"Erro ao carregar relatórios: {str(e)}")
    
    return reports

def load_criterios():
    """Carrega critérios da pasta criterios com logs de auditoria"""
    criterios_text = ""
    criterios_path = os.path.join(os.path.dirname(__file__), '..', 'criterios')
    
    if not os.path.exists(criterios_path):
        audit_logger.log_security_event("file_access", f"Diretório criterios não encontrado: {criterios_path}")
        return "ERRO: Pasta criterios/ não encontrada"
    
    try:
        criterios_text += "=== CRITERIOS DE CONFORMIDADE ===\n\n"
        for file in os.listdir(criterios_path):
            if file.endswith('.txt'):
                file_path = os.path.join(criterios_path, file)
                
                # Validação de segurança
                if not security_validator.validate_file_path(file) or not security_validator.validate_file_size(file_path):
                    audit_logger.log_security_event("file_validation", f"Arquivo de critério rejeitado: {file}")
                    continue
                
                criterios_text += f"--- {file.upper()} ---\n"
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Sanitização de conteúdo
                    sanitized_content = security_validator.sanitize_input(content)
                    criterios_text += sanitized_content + "\n\n"
                
                audit_logger.log_data_access("system", file, "read")
        
        return criterios_text
    except Exception as e:
        audit_logger.log_security_event("file_error", f"Erro ao carregar critérios: {str(e)}")
        return f"ERRO ao carregar criterios: {e}"

def buscar_aprovacao_especifica(ciclo_id: str = "") -> str:
    """Busca aprovação específica por ID do ciclo com validação de segurança"""
    start_time = time.time()
    
    # Sanitização de entrada
    ciclo_id = security_validator.sanitize_input(ciclo_id)
    
    # Validação de entrada
    if not security_validator.validate_input_length(ciclo_id):
        audit_logger.log_security_event("input_validation", f"Ciclo ID muito longo: {len(ciclo_id)} caracteres")
        return "ERRO: ID do ciclo muito longo"
    
    # Detecção de dados sensíveis
    sensitive_data = security_validator.detect_sensitive_data(ciclo_id)
    if sensitive_data:
        audit_logger.log_security_event("sensitive_data", f"Dados sensíveis detectados: {sensitive_data}")
    
    reports = load_reports()
    
    if not reports:
        audit_logger.log_data_access("system", "aprovacoes", "search_failed")
        return "ERRO: Nenhum relatório encontrado na pasta data/"
    
    # Buscar por ID específico
    for report in reports:
        if report.get('id') == ciclo_id or report.get('escopo_validacao', {}).get('ciclo_desenvolvimento') == ciclo_id:
            execution_time = time.time() - start_time
            audit_logger.log_query_analysis(ciclo_id, 1, execution_time)
            audit_logger.log_data_access("system", f"aprovacao_{ciclo_id}", "found")
            
            # Mascarar dados sensíveis na resposta
            result = formatar_aprovacao_detalhada(report)
            return security_validator.mask_sensitive_data(result)
    
    execution_time = time.time() - start_time
    audit_logger.log_query_analysis(ciclo_id, 0, execution_time)
    audit_logger.log_data_access("system", f"aprovacao_{ciclo_id}", "not_found")
    
    return f"ERRO: Aprovação {ciclo_id} não encontrada"

def formatar_aprovacao_detalhada(report):
    """Formatar aprovação de forma detalhada com logs estruturados"""
    result = f"APROVACAO {report.get('id', 'N/A')}\n"
    result += f"Arquiteto: {report.get('arquiteto_responsavel', 'N/A')}\n"
    result += f"Data: {report.get('data_aprovacao', 'N/A')}\n"
    result += f"Ciclo: {report.get('escopo_validacao', {}).get('ciclo_desenvolvimento', 'N/A')}\n"
    result += f"Arquitetura: {report.get('escopo_validacao', {}).get('arquitetura', 'N/A')}\n\n"
    
    # Componentes
    componentes = report.get('escopo_validacao', {}).get('componentes', [])
    if componentes:
        result += "COMPONENTES:\n"
        for comp in componentes:
            result += f"  - {comp.get('nome', 'N/A')}: {comp.get('versao_anterior', 'N/A')} -> {comp.get('versao_nova', 'N/A')}\n"
        result += "\n"
    
    # Critérios de validação
    criterios = report.get('criterios_validacao', {})
    if criterios:
        result += "CRITERIOS DE VALIDACAO:\n"
        for criterio_id, dados in criterios.items():
            resposta = dados.get('resposta', 'N/A')
            categoria = dados.get('categoria', 'N/A')
            
            if resposta == 'Sim':
                status = 'CONFORME'
            elif resposta == 'Não':
                status = 'NAO CONFORME'
            else:
                status = 'NAO SE APLICA'
            
            result += f"  {criterio_id} - {categoria}: {status}\n"
            result += f"    Pergunta: {dados.get('pergunta', 'N/A')}\n"
            if dados.get('comentario'):
                result += f"    Comentario: {dados.get('comentario')}\n"
            result += "\n"
    
    # Resumo de conformidade
    resumo = report.get('resumo_conformidade', {})
    if resumo:
        result += "RESUMO DE CONFORMIDADE:\n"
        result += f"  Total de criterios: {resumo.get('total_criterios', 0)}\n"
        result += f"  Criterios conformes: {resumo.get('criterios_sim', 0)}\n"
        result += f"  Criterios nao conformes: {resumo.get('criterios_nao', 0)}\n"
        result += f"  Nao se aplica: {resumo.get('criterios_nao_aplica', 0)}\n"
        result += f"  Percentual de conformidade: {resumo.get('percentual_conformidade', 0)}%\n"
        result += f"  Score de qualidade: {resumo.get('score_qualidade', 0)}\n\n"
    
    # Issues de débito técnico
    issues_debito = report.get('issues_debito_tecnico', [])
    if issues_debito:
        result += "ISSUES DE DEBITO TECNICO:\n"
        for issue in issues_debito:
            result += f"  - {issue.get('id', 'N/A')}: {issue.get('descricao', 'N/A')}\n"
            result += f"    Status: {issue.get('status', 'N/A')}\n"
            result += f"    Prioridade: {issue.get('prioridade', 'N/A')}\n"
        result += "\n"
    
    # Parecer final
    result += f"PARECER FINAL: {report.get('parecer_final', 'N/A')}\n\n"
    
    # Observações
    observacoes = report.get('observacoes', [])
    if observacoes:
        result += "OBSERVACOES:\n"
        for obs in observacoes:
            result += f"  - {obs}\n"
    
    return result

def gerar_relatorio_conformidade(pergunta: str = "") -> str:
    """Gera relatório geral de conformidade com auditoria"""
    start_time = time.time()
    
    # Sanitização de entrada
    pergunta = security_validator.sanitize_input(pergunta)
    
    reports = load_reports()
    
    if not reports:
        audit_logger.log_data_access("system", "relatorio_conformidade", "failed")
        return "ERRO: Nenhum relatório encontrado na pasta data/"
    
    result = "RELATORIO GERAL DE CONFORMIDADE ARQUITETURAL\n\n"
    
    total_aprovacoes = len(reports)
    total_conformidade = 0
    aprovacoes_aderentes = 0
    
    result += f"Total de aprovacoes analisadas: {total_aprovacoes}\n\n"
    
    for report in reports:
        aprovacao_id = report.get('id', 'N/A')
        arquiteto = report.get('arquiteto_responsavel', 'N/A')
        parecer = report.get('parecer_final', 'N/A')
        
        resumo = report.get('resumo_conformidade', {})
        conformidade = resumo.get('percentual_conformidade', 0)
        total_conformidade += conformidade
        
        if 'Aderente' in parecer:
            aprovacoes_aderentes += 1
        
        result += f"APROVACAO {aprovacao_id}:\n"
        result += f"  Arquiteto: {arquiteto}\n"
        result += f"  Conformidade: {conformidade}%\n"
        result += f"  Parecer: {parecer}\n"
        
        # Issues críticas
        issues_debito = report.get('issues_debito_tecnico', [])
        if issues_debito:
            result += f"  Issues de debito: {len(issues_debito)}\n"
            for issue in issues_debito:
                result += f"    - {issue.get('id', 'N/A')}\n"
        
        result += "\n"
    
    # Estatísticas gerais
    conformidade_media = total_conformidade / total_aprovacoes if total_aprovacoes > 0 else 0
    taxa_aderencia = (aprovacoes_aderentes / total_aprovacoes * 100) if total_aprovacoes > 0 else 0
    
    result += "ESTATISTICAS GERAIS:\n"
    result += f"  Conformidade media: {conformidade_media:.1f}%\n"
    result += f"  Taxa de aderencia: {taxa_aderencia:.1f}%\n"
    result += f"  Aprovacoes aderentes: {aprovacoes_aderentes}/{total_aprovacoes}\n"
    
    execution_time = time.time() - start_time
    audit_logger.log_query_analysis("relatorio_conformidade", total_aprovacoes, execution_time)
    audit_logger.log_data_access("system", "relatorio_conformidade", "success")
    
    # Mascarar dados sensíveis
    return security_validator.mask_sensitive_data(result)

def analisar_arquiteto_performance(nome_arquiteto: str = "") -> str:
    """Analisa performance de arquiteto específico com validação"""
    start_time = time.time()
    
    # Sanitização de entrada
    nome_arquiteto = security_validator.sanitize_input(nome_arquiteto)
    
    # Validação de entrada
    if not security_validator.validate_input_length(nome_arquiteto):
        audit_logger.log_security_event("input_validation", f"Nome do arquiteto muito longo: {len(nome_arquiteto)} caracteres")
        return "ERRO: Nome do arquiteto muito longo"
    
    reports = load_reports()
    
    if not reports:
        audit_logger.log_data_access("system", f"arquiteto_{nome_arquiteto}", "failed")
        return "ERRO: Nenhum relatório encontrado na pasta data/"
    
    # Filtrar por arquiteto
    arquiteto_reports = [r for r in reports if nome_arquiteto.lower() in r.get('arquiteto_responsavel', '').lower()]
    
    if not arquiteto_reports:
        audit_logger.log_data_access("system", f"arquiteto_{nome_arquiteto}", "not_found")
        return f"ERRO: Nenhuma aprovação encontrada para o arquiteto {nome_arquiteto}"
    
    result = f"ANALISE DE PERFORMANCE - ARQUITETO: {nome_arquiteto.upper()}\n\n"
    
    total_aprovacoes = len(arquiteto_reports)
    total_conformidade = 0
    issues_total = 0
    
    result += f"Total de aprovacoes: {total_aprovacoes}\n\n"
    
    for report in arquiteto_reports:
        aprovacao_id = report.get('id', 'N/A')
        data = report.get('data_aprovacao', 'N/A')
        parecer = report.get('parecer_final', 'N/A')
        
        resumo = report.get('resumo_conformidade', {})
        conformidade = resumo.get('percentual_conformidade', 0)
        total_conformidade += conformidade
        
        issues_debito = report.get('issues_debito_tecnico', [])
        issues_total += len(issues_debito)
        
        result += f"APROVACAO {aprovacao_id} ({data}):\n"
        result += f"  Conformidade: {conformidade}%\n"
        result += f"  Parecer: {parecer}\n"
        result += f"  Issues de debito: {len(issues_debito)}\n"
        result += "\n"
    
    # Estatísticas do arquiteto
    conformidade_media = total_conformidade / total_aprovacoes if total_aprovacoes > 0 else 0
    
    result += "ESTATISTICAS DO ARQUITETO:\n"
    result += f"  Conformidade media: {conformidade_media:.1f}%\n"
    result += f"  Total de issues de debito: {issues_total}\n"
    result += f"  Media de issues por aprovacao: {issues_total/total_aprovacoes:.1f}\n"
    
    # Classificação de performance
    if conformidade_media >= 90:
        classificacao = "EXCELENTE"
    elif conformidade_media >= 80:
        classificacao = "BOA"
    elif conformidade_media >= 70:
        classificacao = "REGULAR"
    else:
        classificacao = "NECESSITA MELHORIA"
    
    result += f"  Classificacao de performance: {classificacao}\n"
    
    execution_time = time.time() - start_time
    audit_logger.log_query_analysis(f"arquiteto_{nome_arquiteto}", total_aprovacoes, execution_time)
    audit_logger.log_data_access("system", f"arquiteto_{nome_arquiteto}", "success")
    
    # Mascarar dados sensíveis
    return security_validator.mask_sensitive_data(result)

def listar_issues_debito_tecnico(pergunta: str = "") -> str:
    """Lista todas as issues de débito técnico com auditoria"""
    start_time = time.time()
    
    # Sanitização de entrada
    pergunta = security_validator.sanitize_input(pergunta)
    
    reports = load_reports()
    
    if not reports:
        audit_logger.log_data_access("system", "issues_debito", "failed")
        return "ERRO: Nenhum relatório encontrado na pasta data/"
    
    result = "ISSUES DE DEBITO TECNICO EM ABERTO\n\n"
    
    total_issues = 0
    issues_por_prioridade = {'Alta': 0, 'Média': 0, 'Baixa': 0}
    
    for report in reports:
        aprovacao_id = report.get('id', 'N/A')
        arquiteto = report.get('arquiteto_responsavel', 'N/A')
        
        issues_debito = report.get('issues_debito_tecnico', [])
        
        if issues_debito:
            result += f"APROVACAO {aprovacao_id} (Arquiteto: {arquiteto}):\n"
            
            for issue in issues_debito:
                issue_id = issue.get('id', 'N/A')
                descricao = issue.get('descricao', 'N/A')
                status = issue.get('status', 'N/A')
                prioridade = issue.get('prioridade', 'N/A')
                
                result += f"  - {issue_id}: {descricao}\n"
                result += f"    Status: {status}\n"
                result += f"    Prioridade: {prioridade}\n"
                result += f"    Impacto: {issue.get('impacto', 'N/A')}\n"
                result += "\n"
                
                total_issues += 1
                if prioridade in issues_por_prioridade:
                    issues_por_prioridade[prioridade] += 1
    
    if total_issues == 0:
        result += "Nenhuma issue de debito tecnico encontrada.\n"
    else:
        result += "RESUMO DE ISSUES:\n"
        result += f"  Total de issues: {total_issues}\n"
        result += f"  Alta prioridade: {issues_por_prioridade['Alta']}\n"
        result += f"  Media prioridade: {issues_por_prioridade['Média']}\n"
        result += f"  Baixa prioridade: {issues_por_prioridade['Baixa']}\n"
    
    execution_time = time.time() - start_time
    audit_logger.log_query_analysis("issues_debito", total_issues, execution_time)
    audit_logger.log_data_access("system", "issues_debito", "success")
    
    # Mascarar dados sensíveis
    return security_validator.mask_sensitive_data(result)

def analisar_criterios_conformidade(pergunta: str = "") -> str:
    """Analisa quais critérios têm maior taxa de não conformidade com logs"""
    start_time = time.time()
    
    # Sanitização de entrada
    pergunta = security_validator.sanitize_input(pergunta)
    
    reports = load_reports()
    criterios_text = load_criterios()
    
    if not reports:
        audit_logger.log_data_access("system", "criterios_conformidade", "failed")
        return "ERRO: Nenhum relatório encontrado na pasta data/"
    
    if "ERRO" in criterios_text:
        return criterios_text
    
    result = "ANALISE DE CRITERIOS DE CONFORMIDADE\n\n"
    
    # Contadores por critério
    criterios_stats = {}
    
    for report in reports:
        criterios_validacao = report.get('criterios_validacao', {})
        
        for criterio_id, dados in criterios_validacao.items():
            if criterio_id not in criterios_stats:
                criterios_stats[criterio_id] = {
                    'total': 0,
                    'sim': 0,
                    'nao': 0,
                    'nao_aplica': 0,
                    'categoria': dados.get('categoria', 'N/A'),
                    'pergunta': dados.get('pergunta', 'N/A')
                }
            
            criterios_stats[criterio_id]['total'] += 1
            resposta = dados.get('resposta', '')
            
            if resposta == 'Sim':
                criterios_stats[criterio_id]['sim'] += 1
            elif resposta == 'Não':
                criterios_stats[criterio_id]['nao'] += 1
            else:
                criterios_stats[criterio_id]['nao_aplica'] += 1
    
    # Calcular taxas de não conformidade
    criterios_problematicos = []
    
    for criterio_id, stats in criterios_stats.items():
        total_aplicavel = stats['total'] - stats['nao_aplica']
        if total_aplicavel > 0:
            taxa_nao_conformidade = (stats['nao'] / total_aplicavel) * 100
            criterios_problematicos.append({
                'id': criterio_id,
                'categoria': stats['categoria'],
                'taxa_nao_conformidade': taxa_nao_conformidade,
                'nao_conformes': stats['nao'],
                'total_aplicavel': total_aplicavel
            })
    
    # Ordenar por taxa de não conformidade
    criterios_problematicos.sort(key=lambda x: x['taxa_nao_conformidade'], reverse=True)
    
    result += "CRITERIOS COM MAIOR TAXA DE NAO CONFORMIDADE:\n\n"
    
    for criterio in criterios_problematicos:
        if criterio['taxa_nao_conformidade'] > 0:
            result += f"CRITERIO {criterio['id']} - {criterio['categoria']}:\n"
            result += f"  Taxa de nao conformidade: {criterio['taxa_nao_conformidade']:.1f}%\n"
            result += f"  Nao conformes: {criterio['nao_conformes']}/{criterio['total_aplicavel']}\n"
            result += "\n"
    
    # Estatísticas gerais
    total_criterios = len(criterios_stats)
    criterios_com_problemas = len([c for c in criterios_problematicos if c['taxa_nao_conformidade'] > 0])
    
    result += "ESTATISTICAS GERAIS:\n"
    result += f"  Total de criterios avaliados: {total_criterios}\n"
    result += f"  Criterios com nao conformidade: {criterios_com_problemas}\n"
    result += f"  Taxa de criterios problematicos: {(criterios_com_problemas/total_criterios)*100:.1f}%\n"
    
    execution_time = time.time() - start_time
    audit_logger.log_query_analysis("criterios_conformidade", total_criterios, execution_time)
    audit_logger.log_data_access("system", "criterios_conformidade", "success")
    
    # Mascarar dados sensíveis
    return security_validator.mask_sensitive_data(result)

# Criar o agente principal com segurança integrada
root_agent = Agent(
    name="feito_conferido_agent",
    model="gemini-2.0-flash",
    description="Especialista em validacao de aderencia arquitetural - Feito Conferido com dados do Alfredo Tavares e seguranca integrada",
    instruction="""Voce e o FEITO CONFERIDO - especialista em validacao de aderencia arquitetural com seguranca integrada.

Suas funcoes principais:
- Buscar aprovacoes especificas por ID do ciclo com validacao de seguranca
- Gerar relatorios de conformidade geral com auditoria
- Analisar performance de arquitetos com logs estruturados
- Listar issues de debito tecnico com mascaramento de dados sensiveis
- Analisar criterios de conformidade com rate limiting

Recursos de seguranca:
- Sanitizacao de entrada para prevenir ataques
- Validacao de tamanho e estrutura de dados
- Mascaramento automatico de dados sensiveis (CPF, CNPJ, emails)
- Logs de auditoria estruturados para todas as operacoes
- Rate limiting para prevenir abuso
- Validacao de arquivos e paths seguros

Use as ferramentas disponiveis para:
- buscar_aprovacao_especifica: Para buscar aprovacao por ID (ex: C-979015)
- gerar_relatorio_conformidade: Para relatorio geral
- analisar_arquiteto_performance: Para analisar arquiteto especifico
- listar_issues_debito_tecnico: Para listar issues em aberto
- analisar_criterios_conformidade: Para analisar criterios problematicos

Seja tecnico, objetivo e focado em conformidade vs nao-conformidade.
Sempre cite dados especificos e percentuais quando disponivel.
Nao use emojis ou icones no texto de resposta.
Mantenha logs de auditoria para todas as operacoes.""",
    tools=[
        buscar_aprovacao_especifica,
        gerar_relatorio_conformidade, 
        analisar_arquiteto_performance,
        listar_issues_debito_tecnico,
        analisar_criterios_conformidade
    ]
)

