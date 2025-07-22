#!/usr/bin/env python3
import json
import os
from pathlib import Path

def analisar_base_dados():
    """Analisa base de dados existente e extrai padrões para critérios"""
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ Pasta data/ não encontrada")
        return {}
    
    dados_analisados = {}
    criterios_extraidos = {}
    
    print("🔍 Analisando arquivos da base de dados...")
    
    for json_file in data_dir.glob("*.json"):
        print(f"   📄 Processando: {json_file.name}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                dados_analisados[json_file.name] = data
                
                # Extrair padrões baseado no conteúdo
                extrair_criterios_do_arquivo(data, json_file.name, criterios_extraidos)
                
        except Exception as e:
            print(f"   ❌ Erro ao processar {json_file.name}: {e}")
    
    return dados_analisados, criterios_extraidos

def extrair_criterios_do_arquivo(data, filename, criterios):
    """Extrai critérios baseado nos dados existentes"""
    
    # === CRITÉRIOS PIX BASEADOS NOS DADOS ===
    if "pix" in filename.lower():
        if "requirements_compliance" in data:
            req_comp = data["requirements_compliance"]
            
            # Critério tempo de resposta
            if "bacen_req_001" in req_comp:
                req_001 = req_comp["bacen_req_001"]
                if "evidence" in req_001 and "P95" in req_001["evidence"]:
                    criterios.setdefault("pix_bacen", []).append({
                        "criterio": "Tempo de Resposta PIX",
                        "descricao": req_001.get("description", ""),
                        "limite": "10 segundos (P95)",
                        "evidencia_atual": req_001.get("evidence", ""),
                        "status_atual": req_001.get("status", ""),
                        "criticidade": "CRÍTICA"
                    })
            
            # Critério validação chaves
            if "bacen_req_002" in req_comp:
                req_002 = req_comp["bacen_req_002"]
                criterios.setdefault("pix_bacen", []).append({
                    "criterio": "Validação Chaves PIX",
                    "descricao": req_002.get("description", ""),
                    "gaps_identificados": req_002.get("gaps", []),
                    "status_atual": req_002.get("status", ""),
                    "criticidade": "CRÍTICA"
                })
        
        # Critérios técnicos PIX
        if "technical_design" in data:
            tech = data["technical_design"]
            criterios.setdefault("pix_tecnico", []).append({
                "criterio": "Coerência Arquitetural PIX",
                "score_minimo": 80,
                "score_atual": tech.get("coherence_score", 0),
                "arquitetura": tech.get("architecture", ""),
                "pontos_fortes": tech.get("strengths", []),
                "preocupacoes": tech.get("concerns", []),
                "criticidade": "ALTA"
            })
    
    # === CRITÉRIOS ETL BASEADOS NOS DADOS ===
    if "etl" in filename.lower():
        if "best_practices_analysis" in data:
            bp = data["best_practices_analysis"]
            
            # Qualidade de dados
            if "data_quality" in bp:
                dq = bp["data_quality"]
                criterios.setdefault("etl_qualidade", []).append({
                    "criterio": "Qualidade de Dados ETL",
                    "score_minimo": 85,
                    "score_atual": dq.get("score", 0),
                    "status_atual": dq.get("status", ""),
                    "praticas_obrigatorias": dq.get("practices", []),
                    "criticidade": "ALTA"
                })
            
            # Performance ETL
            if "performance" in bp:
                perf = bp["performance"]
                criterios.setdefault("etl_performance", []).append({
                    "criterio": "Performance ETL",
                    "score_minimo": 80,
                    "score_atual": perf.get("score", 0),
                    "metricas_atuais": perf.get("metrics", []),
                    "criticidade": "MÉDIA"
                })
            
            # Confiabilidade ETL
            if "reliability" in bp:
                rel = bp["reliability"]
                criterios.setdefault("etl_confiabilidade", []).append({
                    "criterio": "Confiabilidade ETL",
                    "score_minimo": 85,
                    "score_atual": rel.get("score", 0),
                    "gaps_criticos": rel.get("gaps", []),
                    "criticidade": "ALTA"
                })
    
    # === CRITÉRIOS MOBILE BASEADOS NOS DADOS ===
    if "mobile" in filename.lower():
        if "mobile_security" in data:
            ms = data["mobile_security"]
            
            # Armazenamento seguro
            if "data_storage" in ms:
                ds = ms["data_storage"]
                criterios.setdefault("mobile_storage", []).append({
                    "criterio": "Armazenamento Seguro Mobile",
                    "status_obrigatorio": "COMPLIANT",
                    "status_atual": ds.get("status", ""),
                    "issues_encontrados": ds.get("issues", []),
                    "criticidade": "CRÍTICA"
                })
        
        # Qualidade código mobile
        if "code_quality" in data:
            cq = data["code_quality"]
            criterios.setdefault("mobile_codigo", []).append({
                "criterio": "Qualidade Código Mobile",
                "score_minimo": 80,
                "score_atual": cq.get("overall_score", 0),
                "test_coverage_minimo": 75,
                "test_coverage_atual": cq.get("test_coverage", 0),
                "max_vulnerabilidades": 5,
                "vulnerabilidades_atuais": cq.get("vulnerabilities", 0),
                "security_rating_minimo": "B",
                "security_rating_atual": cq.get("security_rating", ""),
                "criticidade": "ALTA"
            })
    
    # === CRITÉRIOS BANKING COMPLIANCE ===
    if "banking_compliance" in data or "internet_banking" in filename.lower():
        if "banking_compliance" in data:
            bc = data["banking_compliance"]
            
            # PCI DSS
            if "pci_dss" in bc:
                pci = bc["pci_dss"]
                criterios.setdefault("compliance_pci", []).append({
                    "criterio": "Conformidade PCI DSS",
                    "score_minimo": 90,
                    "score_atual": pci.get("score", 0),
                    "status_obrigatorio": "COMPLIANT",
                    "status_atual": pci.get("status", ""),
                    "criticidade": "CRÍTICA"
                })
            
            # LGPD
            if "lgpd_compliance" in bc:
                lgpd = bc["lgpd_compliance"]
                criterios.setdefault("compliance_lgpd", []).append({
                    "criterio": "Conformidade LGPD",
                    "score_minimo": 85,
                    "score_atual": lgpd.get("score", 0),
                    "status_obrigatorio": "COMPLIANT", 
                    "status_atual": lgpd.get("status", ""),
                    "criticidade": "ALTA"
                })

def gerar_arquivos_criterios(criterios_extraidos):
    """Gera arquivos de critérios baseados nos dados analisados"""
    
    os.makedirs("criterios", exist_ok=True)
    
    for categoria, criterios_lista in criterios_extraidos.items():
        if not criterios_lista:
            continue
            
        arquivo_criterio = f"criterios/{categoria}.txt"
        
        with open(arquivo_criterio, 'w', encoding='utf-8') as f:
            f.write(f"CRITÉRIOS {categoria.upper().replace('_', ' ')}\n")
            f.write("=" * 50 + "\n")
            f.write(f"Gerado automaticamente baseado na análise da base de dados\n\n")
            
            for i, criterio in enumerate(criterios_lista, 1):
                f.write(f"{i}. {criterio['criterio'].upper()}:\n")
                
                if 'descricao' in criterio and criterio['descricao']:
                    f.write(f"   Descrição: {criterio['descricao']}\n")
                
                if 'score_minimo' in criterio:
                    f.write(f"   Score mínimo: {criterio['score_minimo']}%\n")
                    f.write(f"   Score atual: {criterio['score_atual']}%\n")
                
                if 'limite' in criterio:
                    f.write(f"   Limite: {criterio['limite']}\n")
                
                if 'status_obrigatorio' in criterio:
                    f.write(f"   Status obrigatório: {criterio['status_obrigatorio']}\n")
                    f.write(f"   Status atual: {criterio['status_atual']}\n")
                
                if 'gaps_identificados' in criterio and criterio['gaps_identificados']:
                    f.write(f"   Gaps identificados: {', '.join(criterio['gaps_identificados'])}\n")
                
                if 'issues_encontrados' in criterio and criterio['issues_encontrados']:
                    f.write(f"   Issues encontrados: {', '.join(criterio['issues_encontrados'])}\n")
                
                if 'evidencia_atual' in criterio and criterio['evidencia_atual']:
                    f.write(f"   Evidência atual: {criterio['evidencia_atual']}\n")
                
                f.write(f"   Criticidade: {criterio['criticidade']}\n\n")
        
        print(f"✅ Gerado: {arquivo_criterio}")

def main():
    print("🔍 Iniciando análise da base de dados...")
    
    dados, criterios = analisar_base_dados()
    
    print(f"\n📊 RESUMO DA ANÁLISE:")
    print(f"   📄 Arquivos processados: {len(dados)}")
    print(f"   📋 Categorias de critérios extraídos: {len(criterios)}")
    
    for categoria, lista in criterios.items():
        print(f"   • {categoria}: {len(lista)} critérios")
    
    print(f"\n📝 Gerando arquivos de critérios...")
    gerar_arquivos_criterios(criterios)
    
    print(f"\n✅ CRITÉRIOS GERADOS COM SUCESSO!")
    print(f"📁 Verifique a pasta criterios/ para os arquivos gerados")

if __name__ == "__main__":
    main()
