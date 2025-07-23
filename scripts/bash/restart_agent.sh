#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
BLINK='\033[5m'
REVERSE='\033[7m'
NC='\033[0m'

CHECK="✓"
CROSS="✗"
ARROW="➜"
STAR="★"
ROCKET="🚀"
FIRE="🔥"
GEAR="⚙️"
CLEAN="🧹"
SEARCH="🔍"
WARNING="⚠️"
SUCCESS="✨"
TIMER="⏳"
BRAIN="🧠"
COFFEE="☕"
PACKAGE="📦"

print_colored() {
    local color=$1
    local text=$2
    echo -e "${color}${text}${NC}"
}

show_spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

progress_bar() {
    local duration=$1
    local steps=20

    local step_duration_ms=$((duration * 1000 / steps))
    
    echo -n "["
    for ((i=0; i<$steps; i++)); do
        echo -n "█"
    
        sleep 0.$(printf "%03d" $step_duration_ms)
    done
    echo "] ${GREEN}${CHECK} Completo!${NC}"
}

show_banner() {
    clear
    echo
    print_colored "$CYAN" "    ╔══════════════════════════════════════════╗"
    print_colored "$CYAN" "    ║                                          ║"
    print_colored "$CYAN" "    ║    ${YELLOW}${BOLD}🔄  RESTART AGENT SYSTEM  🔄${NC}${CYAN}         ║"
    print_colored "$CYAN" "    ║                                          ║"
    print_colored "$CYAN" "    ╚══════════════════════════════════════════╝"
    echo
    

    for i in 1 2 3; do
        echo -ne "\r    ${YELLOW}${ROCKET} Inicializando sistema${NC}"
        for j in 1 2 3; do
            echo -n "."
            sleep 0.3
        done
        echo -ne "\r                                          \r"
    done
    echo
}

show_status() {
    local icon=$1
    local color=$2
    local message=$3
    echo -e "  ${icon}  ${color}${message}${NC}"
}

check_and_install_deps() {
    show_status "$PACKAGE" "$BLUE${BOLD}" "VERIFICANDO DEPENDÊNCIAS DO SISTEMA"
    echo "  ${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    

    if ! command -v python3 &> /dev/null; then
        show_status "$CROSS" "$RED" "Python3 não encontrado!"
        exit 1
    else
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        show_status "$CHECK" "$GREEN" "Python $PYTHON_VERSION encontrado"
    fi
    

    if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
        show_status "$WARNING" "$YELLOW" "pip não encontrado. Instalando..."
        sudo apt-get update && sudo apt-get install -y python3-pip || {
            show_status "$CROSS" "$RED" "Falha ao instalar pip"
            exit 1
        }
    else
        show_status "$CHECK" "$GREEN" "pip encontrado"
    fi
    

    if ! command -v uv &> /dev/null; then
        show_status "$WARNING" "$YELLOW" "uv não encontrado. Instalando..."
        echo -n "  Instalando"
        (curl -LsSf https://astral.sh/uv/install.sh | sh) &
        pid=$!
        while kill -0 $pid 2>/dev/null; do
            echo -n "."
            sleep 0.5
        done
        echo " ${GREEN}${CHECK}${NC}"
        
    
        export PATH="$HOME/.cargo/bin:$PATH"
        
        if command -v uv &> /dev/null; then
            show_status "$CHECK" "$GREEN" "uv instalado com sucesso!"
        else
            show_status "$WARNING" "$YELLOW" "uv instalado mas não no PATH. Continuando sem uv..."
        fi
    else
        show_status "$CHECK" "$GREEN" "uv encontrado"
    fi
    

    if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
        show_status "$WARNING" "$YELLOW" "Ambiente virtual não encontrado. Criando..."
        python3 -m venv .venv
        show_status "$CHECK" "$GREEN" "Ambiente virtual criado"
    else
        show_status "$CHECK" "$GREEN" "Ambiente virtual encontrado"
    fi
    

    if [ -d ".venv" ]; then
        source .venv/bin/activate
    elif [ -d "venv" ]; then
        source venv/bin/activate
    fi
    

    if ! python3 -c "import google.adk" 2>/dev/null; then
        show_status "$WARNING" "$YELLOW" "google-adk não encontrado. Instalando..."
        echo -n "  Instalando"
        (pip install google-adk==1.2.1) &
        pid=$!
        while kill -0 $pid 2>/dev/null; do
            echo -n "."
            sleep 0.5
        done
        echo " ${GREEN}${CHECK}${NC}"
        show_status "$CHECK" "$GREEN" "google-adk instalado"
    else
        show_status "$CHECK" "$GREEN" "google-adk já instalado"
    fi
    

    if [ -f "requirements.txt" ]; then
        show_status "$PACKAGE" "$CYAN" "Instalando dependências do requirements.txt..."
        pip install -r requirements.txt > /dev/null 2>&1
        show_status "$CHECK" "$GREEN" "Dependências instaladas"
    elif [ -f "pyproject.toml" ]; then
        show_status "$PACKAGE" "$CYAN" "Instalando dependências do pyproject.toml..."
        pip install . > /dev/null 2>&1
        show_status "$CHECK" "$GREEN" "Projeto instalado"
    fi
    
    echo
}

show_banner

check_and_install_deps

show_status "$GEAR" "$BLUE${BOLD}" "INICIANDO PROCESSO DE REINICIALIZAÇÃO"
echo "  ${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

show_status "$FIRE" "$RED" "FASE 1: Eliminando processos antigos"
echo -n "  "
(
    sudo pkill -f "streamlit" 2>/dev/null
    sudo pkill -f "adk" 2>/dev/null
    sudo pkill -f "uvicorn" 2>/dev/null
    sudo pkill -f "playground" 2>/dev/null
    sudo pkill -f "app.py" 2>/dev/null
    sudo fuser -k 8501/tcp 2>/dev/null
) & show_spinner $!

show_status "$CHECK" "$GREEN" "Processos eliminados com sucesso!"
echo

show_status "$TIMER" "$YELLOW" "Aguardando finalização dos processos..."
echo -n "  "
progress_bar 2
echo

show_status "$SEARCH" "$CYAN" "Verificando processos remanescentes..."
PROCESSES=$(ps aux | grep -E "(streamlit|adk|uvicorn|playground|app.py)" | grep -v grep)
if [ -z "$PROCESSES" ]; then
    show_status "$CHECK" "$GREEN" "Nenhum processo antigo encontrado!"
else
    show_status "$WARNING" "$YELLOW" "Processos ainda ativos detectados"
fi
echo

show_status "$CLEAN" "$PURPLE" "FASE 2: Limpeza de cache e arquivos temporários"
echo -n "  Limpando"
(
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    find . -name "*.pyc" -delete 2>/dev/null
    
    if command -v uv &> /dev/null; then 
        uv cache clean 2>/dev/null
    fi
) & 
pid=$!
while kill -0 $pid 2>/dev/null; do
    echo -n "."
    sleep 0.5
done
echo " ${GREEN}${CHECK}${NC}"
echo

show_status "$COFFEE" "$YELLOW" "FASE 3: Preparando ambiente"
echo -n "  "
sleep 5 &
show_spinner $!
show_status "$CHECK" "$GREEN" "Ambiente preparado!"
echo

show_status "$SEARCH" "$CYAN" "FASE 4: Verificação final de processos"
REMAINING_PROCESSES=$(ps aux | grep -E "(streamlit|adk|uvicorn|playground|app.py)" | grep -v grep)

if [ -n "$REMAINING_PROCESSES" ]; then 
    show_status "$WARNING" "$YELLOW" "Forçando terminação de processos teimosos..."
    sudo pkill -9 -f "streamlit" 2>/dev/null
    sudo pkill -9 -f "adk" 2>/dev/null
    sudo pkill -9 -f "uvicorn" 2>/dev/null
    sudo pkill -9 -f "playground" 2>/dev/null
    sudo pkill -9 -f "app.py" 2>/dev/null
    sleep 3
    show_status "$CHECK" "$GREEN" "Processos eliminados forçadamente!"
else 
    show_status "$CHECK" "$GREEN" "Sistema limpo!"
fi
echo

show_status "$BRAIN" "$BLUE" "FASE 5: Testando funcionalidade básica"

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
    show_status "$CROSS" "$RED" "Arquivo app.py não encontrado"
    PROJECT_DIR=""
fi

if [ -n "$PROJECT_DIR" ]; then
    show_status "$CHECK" "$GREEN" "Projeto encontrado em: $PROJECT_DIR"
fi

if [ -n "$PROJECT_DIR" ] && command -v uv &> /dev/null; then 
    show_status "$GEAR" "$CYAN" "Executando teste de funcionalidade..."
    cd "$PROJECT_DIR"
    TEST_RESULT=$(timeout 10 uv run python -c "
try:
    from app import root_agent
    result = root_agent('teste')
    print('SUCESSO')
except Exception as e:
    print('ERRO')
" 2>&1)
    
    if [[ "$TEST_RESULT" == *"SUCESSO"* ]]; then
        show_status "$CHECK" "$GREEN" "Teste passou com sucesso!"
    else
        show_status "$WARNING" "$YELLOW" "Teste falhou (não crítico)"
    fi
    cd - > /dev/null
fi
echo

show_status "$ROCKET" "$PURPLE${BOLD}" "FASE 6: Iniciando aplicação"
echo "  ${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

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

STARTED=false

if [ -n "$MAKEFILE_DIR" ] && grep -q "playground" "$MAKEFILE_DIR/Makefile" 2>/dev/null; then 
    show_status "$GEAR" "$CYAN" "Iniciando via Makefile..."
    cd "$MAKEFILE_DIR"
    make playground
    STARTED=true
    cd - > /dev/null
else 
    if [ -n "$PROJECT_DIR" ]; then
        cd "$PROJECT_DIR"
        
    
        if command -v uv &> /dev/null && [ -f "app.py" ]; then 
            show_status "$GEAR" "$CYAN" "Iniciando com uv run streamlit..."
            nohup uv run streamlit run app.py --server.port 8501 > /tmp/streamlit.log 2>&1 &
            PID=$!
            show_status "$CHECK" "$GREEN" "Aplicação iniciada! (PID: $PID)"
            STARTED=true
            
    
        elif command -v streamlit &> /dev/null && [ -f "app.py" ]; then
            show_status "$GEAR" "$CYAN" "Iniciando com streamlit..."
            nohup streamlit run app.py --server.port 8501 > /tmp/streamlit.log 2>&1 &
            PID=$!
            show_status "$CHECK" "$GREEN" "Aplicação iniciada! (PID: $PID)"
            STARTED=true
            
    
        elif (command -v python || command -v python3) &> /dev/null && [ -f "app.py" ]; then
            PYTHON_CMD=$(command -v python3 || command -v python)
            show_status "$GEAR" "$CYAN" "Iniciando com $PYTHON_CMD -m streamlit..."
            nohup $PYTHON_CMD -m streamlit run app.py --server.port 8501 > /tmp/streamlit.log 2>&1 &
            PID=$!
            show_status "$CHECK" "$GREEN" "Aplicação iniciada! (PID: $PID)"
            STARTED=true
        fi
        
        cd - > /dev/null
    fi
fi

echo

if [ "$STARTED" = true ]; then
    show_status "$TIMER" "$YELLOW" "Aguardando servidor inicializar..."
    echo -n "  "
    progress_bar 5
fi
echo

echo
print_colored "$CYAN${BOLD}" "  ╔══════════════════════════════════════════╗"
print_colored "$CYAN${BOLD}" "  ║         VERIFICAÇÃO FINAL                ║"
print_colored "$CYAN${BOLD}" "  ╚══════════════════════════════════════════╝"
echo

PROCESS_COUNT=$(ps aux | grep -E "(streamlit|adk|uvicorn|playground)" | grep -v grep | wc -l)
if [ "$PROCESS_COUNT" -gt 0 ]; then
    show_status "$CHECK" "$GREEN" "Processos ativos: $PROCESS_COUNT"
else
    show_status "$WARNING" "$YELLOW" "Nenhum processo encontrado"
fi

show_status "$SEARCH" "$CYAN" "Verificando conectividade..."
if nc -zv localhost 8501 2>/dev/null; then
    show_status "$CHECK" "$GREEN${BOLD}" "Servidor ONLINE na porta 8501!"
elif command -v lsof &> /dev/null && lsof -i:8501 2>/dev/null; then
    show_status "$CHECK" "$GREEN${BOLD}" "Servidor RODANDO na porta 8501!"
elif timeout 2 bash -c 'cat < /dev/null > /dev/tcp/localhost/8501' 2>/dev/null; then
    show_status "$CHECK" "$GREEN${BOLD}" "Servidor RESPONDENDO na porta 8501!"
else
    show_status "$CROSS" "$RED" "Servidor não está respondendo"
    if [ -f /tmp/streamlit.log ]; then
        show_status "$WARNING" "$YELLOW" "Verificando logs..."
        tail -5 /tmp/streamlit.log
    fi
fi

echo
echo
print_colored "$GREEN${BOLD}" "  ╔══════════════════════════════════════════╗"
print_colored "$GREEN${BOLD}" "  ║                                          ║"
print_colored "$GREEN${BOLD}" "  ║    ${SUCCESS} REINICIALIZAÇÃO CONCLUÍDA! ${SUCCESS}     ║"
print_colored "$GREEN${BOLD}" "  ║                                          ║"
print_colored "$GREEN${BOLD}" "  ╚══════════════════════════════════════════╝"
echo
print_colored "$CYAN" "  🌐 URL: ${WHITE}${BOLD}http://localhost:8501${NC}"
print_colored "$CYAN" "  📋 Logs: ${WHITE}/tmp/streamlit.log${NC}"
echo
print_colored "$YELLOW${BLINK}" "  ${ROCKET} Seu agente está pronto! ${ROCKET}"
echo
echo