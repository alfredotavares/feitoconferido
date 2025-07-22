import json

def debug_analisar_conformidade(input_data=None):
    """Função de debug para rastrear o erro"""
    print(f"=== DEBUG TOOL ===")
    print(f"Input recebido: {input_data}")
    print(f"Tipo do input: {type(input_data)}")
    
    if input_data:
        print(f"Input é string? {isinstance(input_data, str)}")
        print(f"Input é dict? {isinstance(input_data, dict)}")
        
    # Retornar sempre o mesmo formato
    return {
        "status": "success",
        "message": "Debug executado com sucesso",
        "input_info": str(type(input_data))
    }

# Testar a função
if __name__ == "__main__":
    result = debug_analisar_conformidade("teste")
    print("Resultado:", result)
