"""
Aplicação principal - Agente Feito Conferido integrado com ADK
Compatível com agent-starter-pack e Vertex AI Agent Engine
"""

import logging
from typing import Dict, Any

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from .feito_conferido_adk_agent import feito_conferido_adk_agent
    logger.info("FeitoConferidoADKAgent importado com sucesso")
except ImportError as e:
    logger.error(f"Erro ao importar FeitoConferidoADKAgent: {e}")
    feito_conferido_adk_agent = None

def handle_message(message: str, context: Dict[str, Any] = None) -> str:
    """
    Handler principal para mensagens do usuário
    Compatível com ADK Agent Engine e Vertex AI
    """
    try:
        if feito_conferido_adk_agent:
            response = feito_conferido_adk_agent.process_message(message)
            logger.info(f"Resposta gerada para: {message[:50]}...")
            return response
        else:
            return """
❌ **Erro:** Agente Feito Conferido não disponível.

🔧 **Funcionalidades básicas disponíveis:**
• Posso fornecer informações gerais
• Responder perguntas básicas sobre conformidade

Como posso ajudar você?
"""
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        return f"❌ Erro interno: {str(e)}"

# Função para compatibilidade com ADK
def main():
    """Função principal para testes locais"""
    print("🚀 Agente Feito Conferido - ADK Integration")
    print("=" * 50)
    
    if feito_conferido_adk_agent:
        print(f"✅ Agente carregado com {len(feito_conferido_adk_agent.reports_data)} relatórios")
        
        # Teste básico
        test_messages = [
            "Olá, quais dados você tem?",
            "Quais relatórios estão disponíveis?",
            "Análise de conformidade"
        ]
        
        for msg in test_messages:
            print(f"\n👤 Usuário: {msg}")
            response = handle_message(msg)
            print(f"🤖 Agente: {response[:200]}...")
    else:
        print("❌ Erro: Agente não pôde ser carregado")

if __name__ == "__main__":
    main()
