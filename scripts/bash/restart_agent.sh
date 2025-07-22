#!/bin/bash
# Script para reiniciar agente que não responde
# Uso: ./restart_agent.sh
 
echo "Iniciando reinicialização do agente..."
 
# 1. Kill TODOS os processos relacionados
echo "Matando processos relacionados..."
sudo pkill -f "adk" 2>/dev/null
sudo pkill -f "uvicorn" 2>/dev/null
sudo pkill -f "playground" 2>/dev/null
sudo fuser -k 8501/tcp 2>/dev/null
 
# Aguardar um pouco para os processos terminarem
sleep 2
 
# Verificar se processos foram terminados
echo "Verificando se processos foram terminados..."
ps aux | grep -E "(adk|uvicorn|playground)" | grep -v grep || echo "Nenhum processo antigo encontrado"
 
# 2. Limpe completamente o cache
echo "Limpando cache..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
 
# Limpar cache do uv se existir
if command -v uv &> /dev/null; then 
    uv cache clean 2>/dev/null
fi
 
# 3. Aguarde mais tempo para garantir limpeza completa
echo "Aguardando limpeza completa..."
sleep 5
 
# 4. Verifique se nenhum processo está rodando
echo "Verificando processos restantes..."
REMAINING_PROCESSES=$(ps aux | grep -E "(adk|uvicorn|playground)" | grep -v grep)
 
if [ -n "$REMAINING_PROCESSES" ]; then 
    echo "Ainda existem processos rodando:"
    echo "$REMAINING_PROCESSES"
    echo "Forçando terminação..."
    sudo pkill -9 -f "adk" 2>/dev/null
    sudo pkill -9 -f "uvicorn" 2>/dev/null
    sudo pkill -9 -f "playground" 2>/dev/null
    sleep 3
else 
    echo "Nenhum processo encontrado"
fi
 
# 5. Teste uma última vez se está funcionando
echo "Testando funcionalidade básica..."
 
# Primeiro, tenta encontrar o diretório do projeto
PROJECT_DIR=""
if [ -f "app.py" ]; then 
    PROJECT_DIR="."
elif [ -f "*/app.py" ]; then 
    PROJECT_DIR=$(dirname $(find . -name "app.py" | head -1))
elif [ -f "src/app.py" ]; then 
    PROJECT_DIR="src"
elif [ -f "playground/app.py" ]; then 
    PROJECT_DIR="playground"
else 
    echo "Arquivo app.py não encontrado, pulando teste"
    PROJECT_DIR=""
fi
 
if [ -n "$PROJECT_DIR" ] && command -v uv &> /dev/null; then 
    echo "Executando teste no diretório: $PROJECT_DIR"
    cd "$PROJECT_DIR"
    TEST_RESULT=$(timeout 10 uv run python -c "
try:
    from app import root_agent
    result = root_agent('teste')
    print('Teste passou:', result)
except Exception as e:
    print('Erro no teste:', str(e))
" 2>&1)
    echo "$TEST_RESULT"
    cd - > /dev/null
else 
    echo "uv não encontrado ou app.py não localizado, pulando teste"
fi
 
# 6. Reinicie o playground
echo "Reiniciando playground..."
 
# Procurar por Makefile em diretórios comuns
MAKEFILE_DIR=""
if [ -f "Makefile" ]; then 
    MAKEFILE_DIR="."
elif [ -f "*/Makefile" ]; then 
    MAKEFILE_DIR=$(dirname $(find . -name "Makefile" | head -1))
elif [ -f "playground/Makefile" ]; then 
    MAKEFILE_DIR="playground"
elif [ -f "../Makefile" ]; then 
    MAKEFILE_DIR=".."
fi
 
if [ -n "$MAKEFILE_DIR" ] && grep -q "playground" "$MAKEFILE_DIR/Makefile" 2>/dev/null; then 
    echo "Executando make playground no diretório: $MAKEFILE_DIR"
    cd "$MAKEFILE_DIR"
    make playground
    cd - > /dev/null
else 
    echo "Makefile não encontrado ou target 'playground' não existe"
    echo "Comandos alternativos para tentar:"
    echo "   - uv run streamlit run app.py --port 8501"
    echo "   - python -m uvicorn app:app --host 0.0.0.0 --port 8501"
    echo "   - streamlit run app.py"
    if command -v uv &> /dev/null && [ -f "app.py" ]; then 
        echo "Tentando iniciar com uv run streamlit..."
        nohup uv run streamlit run app.py --port 8501 > /dev/null 2>&1 &
        echo "Comando executado em background"
    fi
fi
 
echo "Reinicialização concluída!"
 
# 7. Verificação final
echo "Verificação final dos processos:"
ps aux | grep -E "(adk|uvicorn|playground)" | grep -v grep || echo "Nenhum processo antigo encontrado"

# 8. Verificar se o servidor está respondendo
echo "Verificando se o servidor está respondendo na porta 8501..."
if nc -zv localhost 8501 2>/dev/null; then
    echo "Servidor está respondendo na porta 8501"
else
    echo "Servidor não está respondendo na porta 8501"
    echo "Tente acessar http://localhost:8501 no navegador"
fi
echo "Script de reinicialização concluído com sucesso!"
echo "Se o problema persistir, verifique os logs do servidor para mais detalhes."
echo "Obrigado por usar o script de reinicialização!"
echo "Script finalizado."