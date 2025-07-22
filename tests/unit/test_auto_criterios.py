#!/usr/bin/env python3
import vertexai
from vertexai.reasoning_engines import ReasoningEngine

def test_auto_criterios():
    print("🤖 Testando agente com critérios auto-gerados...")
    vertexai.init(project="gft-bu-gcp", location="us-central1")
    engine = ReasoningEngine("4178188166013911040")
    
    tests = [
        "Analisar PIX usando critérios auto-gerados",
        "Verificar ETL conforme critérios extraídos dos dados",
        "Mobile banking vs critérios baseados na própria análise", 
        "Resumo: todos os sistemas vs critérios auto-gerados"
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
        
        input(f"\n⏸️  Pressione ENTER para próximo teste...")

if __name__ == "__main__":
    test_auto_criterios()
