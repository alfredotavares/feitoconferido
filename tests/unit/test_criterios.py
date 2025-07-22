#!/usr/bin/env python3
import vertexai
from vertexai.reasoning_engines import ReasoningEngine

def test_criterios():
    print("🔧 Inicializando Vertex AI...")
    vertexai.init(project="gft-bu-gcp", location="us-central1")
    
    print("🤖 Conectando ao agente Feito Conferido...")
    engine = ReasoningEngine("4178188166013911040")
    
    tests = [
        "Analisar sistema PIX conforme critérios BACEN",
        "Verificar conformidade ETL com critérios de qualidade",
        "Análise mobile banking vs critérios de segurança",
        "Resumo geral: todos os sistemas vs todos os critérios"
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'='*60}")
        print(f"🔍 TESTE {i}: {test}")
        print(f"{'='*60}")
        
        try:
            result = engine.query(input={"query": test})
            print(result)
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        input("\n⏸️  Pressione ENTER para próximo teste...")

if __name__ == "__main__":
    test_criterios()
