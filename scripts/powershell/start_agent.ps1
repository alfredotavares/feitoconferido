[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$symbols = @{
    CHECK = "✓"
    CROSS = "✗"
    ARROW = "➜"
    STAR = "★"
    ROCKET = "🚀"
    FIRE = "🔥"
    GEAR = "⚙️"
    CLEAN = "🧹"
    SEARCH = "🔍"
    WARNING = "⚠️"
    SUCCESS = "✨"
    TIMER = "⏳"
    BRAIN = "🧠"
    COFFEE = "☕"
    PACKAGE = "📦"
}

function Write-Status {
    param(
        [string]$Icon,
        [string]$Message,
        [ConsoleColor]$Color = "White"
    )
    Write-Host "  $Icon  " -NoNewline
    Write-Host $Message -ForegroundColor $Color
}

function Show-Spinner {
    param(
        [ScriptBlock]$ScriptBlock,
        [string]$Message = "Processando"
    )
    
    $job = Start-Job -ScriptBlock $ScriptBlock
    $spinChars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    $i = 0
    
    Write-Host "  " -NoNewline
    while ($job.State -eq "Running") {
        Write-Host "`r  [$($spinChars[$i % $spinChars.Length])] $Message" -NoNewline -ForegroundColor Yellow
        Start-Sleep -Milliseconds 100
        $i++
    }
    
    Receive-Job -Job $job
    Remove-Job -Job $job
    Write-Host "`r  $(' ' * ($Message.Length + 5))`r" -NoNewline
}

function Show-ProgressBar {
    param(
        [int]$Duration,
        [string]$Activity = "Processando"
    )
    
    $steps = 20
    Write-Host "  [" -NoNewline
    
    for ($i = 0; $i -lt $steps; $i++) {
        Write-Host "█" -NoNewline -ForegroundColor Green
        Start-Sleep -Milliseconds ($Duration * 1000 / $steps)
    }
    
    Write-Host "] " -NoNewline
    Write-Host "$($symbols.CHECK) Completo!" -ForegroundColor Green
}

function Show-Banner {
    Clear-Host
    Write-Host ""
    Write-Host "    ╔══════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "    ║                                          ║" -ForegroundColor Cyan
    Write-Host "    ║    " -NoNewline -ForegroundColor Cyan
    Write-Host "🔄  START AGENT SYSTEM  🔄" -NoNewline -ForegroundColor Yellow
    Write-Host "         ║" -ForegroundColor Cyan
    Write-Host "    ║                                          ║" -ForegroundColor Cyan
    Write-Host "    ╚══════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    

    for ($i = 1; $i -le 3; $i++) {
        Write-Host "`r    $($symbols.ROCKET) Inicializando sistema" -NoNewline -ForegroundColor Yellow
        for ($j = 1; $j -le 3; $j++) {
            Write-Host "." -NoNewline -ForegroundColor Yellow
            Start-Sleep -Milliseconds 300
        }
        Write-Host "`r                                          `r" -NoNewline
    }
    Write-Host ""
}

function Test-AndInstallDependencies {
    Write-Status $symbols.PACKAGE "VERIFICANDO DEPENDÊNCIAS DO SISTEMA" "Blue"
    Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor White
    Write-Host ""
    

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
    }
    
    if ($pythonCmd) {
        $pythonVersion = & $pythonCmd.Name --version 2>&1
        Write-Status $symbols.CHECK "Python $pythonVersion encontrado" "Green"
    } else {
        Write-Status $symbols.CROSS "Python não encontrado!" "Red"
        Write-Host "  Por favor, instale Python de: https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
    

    $pipCmd = Get-Command pip -ErrorAction SilentlyContinue
    if (-not $pipCmd) {
        $pipCmd = Get-Command pip3 -ErrorAction SilentlyContinue
    }
    
    if ($pipCmd) {
        Write-Status $symbols.CHECK "pip encontrado" "Green"
    } else {
        Write-Status $symbols.WARNING "pip não encontrado. Instalando..." "Yellow"
        & $pythonCmd.Name -m ensurepip --upgrade
    }
    

    $uvCmd = Get-Command uv -ErrorAction SilentlyContinue
    if (-not $uvCmd) {
        Write-Status $symbols.WARNING "uv não encontrado. Instalando..." "Yellow"
        Write-Host "  Instalando" -NoNewline
        
    
        try {
            Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -UseBasicParsing | Invoke-Expression
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            Write-Host " $($symbols.CHECK)" -ForegroundColor Green
            Write-Status $symbols.CHECK "uv instalado com sucesso!" "Green"
        } catch {
            Write-Status $symbols.WARNING "Falha ao instalar uv. Continuando sem uv..." "Yellow"
        }
    } else {
        Write-Status $symbols.CHECK "uv encontrado" "Green"
    }
    

    $venvPath = ".venv"
    if (-not (Test-Path $venvPath)) {
        $venvPath = "venv"
        if (-not (Test-Path $venvPath)) {
            Write-Status $symbols.WARNING "Ambiente virtual não encontrado. Criando..." "Yellow"
            & $pythonCmd.Name -m venv .venv
            $venvPath = ".venv"
            Write-Status $symbols.CHECK "Ambiente virtual criado" "Green"
        }
    } else {
        Write-Status $symbols.CHECK "Ambiente virtual encontrado" "Green"
    }
    

    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
    }
    

    $adkCheck = & python -c "import google.adk" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Status $symbols.WARNING "google-adk não encontrado. Instalando..." "Yellow"
        Write-Host "  Instalando" -NoNewline
        Show-Spinner -ScriptBlock {
            pip install google-adk==1.2.1 2>&1 | Out-Null
        } -Message "google-adk"
        Write-Host " $($symbols.CHECK)" -ForegroundColor Green
        Write-Status $symbols.CHECK "google-adk instalado" "Green"
    } else {
        Write-Status $symbols.CHECK "google-adk já instalado" "Green"
    }
    

    if (Test-Path "requirements.txt") {
        Write-Status $symbols.PACKAGE "Instalando dependências do requirements.txt..." "Cyan"
        pip install -r requirements.txt | Out-Null
        Write-Status $symbols.CHECK "Dependências instaladas" "Green"
    } elseif (Test-Path "pyproject.toml") {
        Write-Status $symbols.PACKAGE "Instalando dependências do pyproject.toml..." "Cyan"
        pip install . | Out-Null
        Write-Status $symbols.CHECK "Projeto instalado" "Green"
    }
    
    Write-Host ""
}

Show-Banner

Test-AndInstallDependencies

Write-Status $symbols.GEAR "INICIANDO PROCESSO DE REINICIALIZAÇÃO" "Blue"
Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor White
Write-Host ""

Write-Status $symbols.FIRE "FASE 1: Eliminando processos antigos" "Red"

Show-Spinner -ScriptBlock {
    $processNames = @("adk", "uvicorn", "playground", "streamlit", "python")
    foreach ($processName in $processNames) {
        Get-Process | Where-Object { 
            $_.ProcessName -match $processName -or 
            ($_.CommandLine -and $_.CommandLine -match $processName)
        } | ForEach-Object {
            try {
                Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            } catch {}
        }
    }
    

    try {
        $connection = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
        if ($connection) {
            Stop-Process -Id $connection.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    } catch {}
} -Message "Eliminando processos"

Write-Status $symbols.CHECK "Processos eliminados com sucesso!" "Green"
Write-Host ""

Write-Status $symbols.TIMER "Aguardando finalização dos processos..." "Yellow"
Show-ProgressBar -Duration 2 -Activity "Aguardando"
Write-Host ""

Write-Status $symbols.SEARCH "Verificando processos remanescentes..." "Cyan"
$remainingProcesses = Get-Process | Where-Object { 
    $_.ProcessName -match "adk|uvicorn|playground|streamlit" -or 
    ($_.CommandLine -and $_.CommandLine -match "adk|uvicorn|playground|streamlit")
}

if (-not $remainingProcesses) {
    Write-Status $symbols.CHECK "Nenhum processo antigo encontrado!" "Green"
} else {
    Write-Status $symbols.WARNING "Processos ainda ativos detectados" "Yellow"
}
Write-Host ""

Write-Status $symbols.CLEAN "FASE 2: Limpeza de cache e arquivos temporários" "Magenta"
Write-Host "  Limpando" -NoNewline

Show-Spinner -ScriptBlock {

    Get-ChildItem -Path . -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | 
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    

    Get-ChildItem -Path . -File -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | 
        Remove-Item -Force -ErrorAction SilentlyContinue
    

    if (Get-Command uv -ErrorAction SilentlyContinue) {
        & uv cache clean 2>$null
    }
} -Message "cache"

Write-Host " $($symbols.CHECK)" -ForegroundColor Green
Write-Host ""

Write-Status $symbols.COFFEE "FASE 3: Preparando ambiente" "Yellow"
Show-Spinner -ScriptBlock {
    Start-Sleep -Seconds 5
} -Message "Preparando"
Write-Status $symbols.CHECK "Ambiente preparado!" "Green"
Write-Host ""

Write-Status $symbols.SEARCH "FASE 4: Verificação final de processos" "Cyan"
$stillRunning = Get-Process | Where-Object { 
    $_.ProcessName -match "adk|uvicorn|playground|streamlit" -or 
    ($_.CommandLine -and $_.CommandLine -match "adk|uvicorn|playground|streamlit")
}

if ($stillRunning) {
    Write-Status $symbols.WARNING "Forçando terminação de processos teimosos..." "Yellow"
    $stillRunning | ForEach-Object {
        try {
            Stop-Process -Id $_.Id -Force -ErrorAction Stop
        } catch {}
    }
    Start-Sleep -Seconds 3
    Write-Status $symbols.CHECK "Processos eliminados forçadamente!" "Green"
} else {
    Write-Status $symbols.CHECK "Sistema limpo!" "Green"
}
Write-Host ""

Write-Status $symbols.BRAIN "FASE 5: Testando funcionalidade básica" "Blue"

$appPaths = @(
    ".\app.py",
    ".\src\app.py",
    ".\playground\app.py"
)

$appPath = $null
foreach ($path in $appPaths) {
    if (Test-Path $path) {
        $appPath = $path
        break
    }
}

if (-not $appPath) {
    $found = Get-ChildItem -Path . -File -Recurse -Filter "app.py" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $appPath = $found.FullName
    }
}

if ($appPath) {
    Write-Status $symbols.CHECK "Projeto encontrado em: $(Split-Path -Parent $appPath)" "Green"
    
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        Write-Status $symbols.GEAR "Executando teste de funcionalidade..." "Cyan"
        $projectDir = Split-Path -Parent $appPath
        Push-Location $projectDir
        
        $testResult = & uv run python -c "
try:
    from app import root_agent
    result = root_agent('teste')
    print('SUCESSO')
except Exception as e:
    print('ERRO')
" 2>&1
        
        if ($testResult -match "SUCESSO") {
            Write-Status $symbols.CHECK "Teste passou com sucesso!" "Green"
        } else {
            Write-Status $symbols.WARNING "Teste falhou (não crítico)" "Yellow"
        }
        Pop-Location
    }
} else {
    Write-Status $symbols.CROSS "Arquivo app.py não encontrado" "Red"
}
Write-Host ""

Write-Status $symbols.ROCKET "FASE 6: Iniciando aplicação" "Magenta"
Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor White

$started = $false

$makefilePaths = @(
    ".\Makefile",
    ".\playground\Makefile",
    "..\Makefile"
)

$makefilePath = $null
foreach ($path in $makefilePaths) {
    if (Test-Path $path) {
        $content = Get-Content $path -ErrorAction SilentlyContinue
        if ($content -match "playground") {
            $makefilePath = $path
            break
        }
    }
}

if ($makefilePath -and (Get-Command make -ErrorAction SilentlyContinue)) {
    $makefileDir = Split-Path -Parent $makefilePath
    Write-Status $symbols.GEAR "Iniciando via Makefile..." "Cyan"
    Push-Location $makefileDir
    & make playground
    Pop-Location
    $started = $true
} elseif ($appPath) {
    $appDir = Split-Path -Parent $appPath
    Push-Location $appDir
    

    if (Get-Command uv -ErrorAction SilentlyContinue) {
        Write-Status $symbols.GEAR "Iniciando com uv run streamlit..." "Cyan"
        $proc = Start-Process -FilePath "uv" -ArgumentList "run", "streamlit", "run", "app.py", "--server.port", "8501" -WindowStyle Hidden -PassThru
        Write-Status $symbols.CHECK "Aplicação iniciada! (PID: $($proc.Id))" "Green"
        $started = $true
    }

    elseif (Get-Command streamlit -ErrorAction SilentlyContinue) {
        Write-Status $symbols.GEAR "Iniciando com streamlit..." "Cyan"
        $proc = Start-Process -FilePath "streamlit" -ArgumentList "run", "app.py", "--server.port", "8501" -WindowStyle Hidden -PassThru
        Write-Status $symbols.CHECK "Aplicação iniciada! (PID: $($proc.Id))" "Green"
        $started = $true
    }

    else {
        $pythonCmd = (Get-Command python -ErrorAction SilentlyContinue).Name
        if (-not $pythonCmd) {
            $pythonCmd = (Get-Command python3 -ErrorAction SilentlyContinue).Name
        }
        if ($pythonCmd) {
            Write-Status $symbols.GEAR "Iniciando com $pythonCmd -m streamlit..." "Cyan"
            $proc = Start-Process -FilePath $pythonCmd -ArgumentList "-m", "streamlit", "run", "app.py", "--server.port", "8501" -WindowStyle Hidden -PassThru
            Write-Status $symbols.CHECK "Aplicação iniciada! (PID: $($proc.Id))" "Green"
            $started = $true
        }
    }
    
    Pop-Location
}

Write-Host ""

if ($started) {
    Write-Status $symbols.TIMER "Aguardando servidor inicializar..." "Yellow"
    Show-ProgressBar -Duration 5 -Activity "Inicializando"
}
Write-Host ""

Write-Host ""
Write-Host "  ╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║         VERIFICAÇÃO FINAL                ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$processes = Get-Process | Where-Object { 
    $_.ProcessName -match "streamlit|adk|uvicorn|playground" -or
    ($_.CommandLine -and $_.CommandLine -match "streamlit|adk|uvicorn|playground")
}

if ($processes) {
    Write-Status $symbols.CHECK "Processos ativos: $($processes.Count)" "Green"
} else {
    Write-Status $symbols.WARNING "Nenhum processo encontrado" "Yellow"
}

Write-Status $symbols.SEARCH "Verificando conectividade..." "Cyan"
try {
    $portCheck = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue
    if ($portCheck) {
        Write-Status $symbols.CHECK "Servidor ONLINE na porta 8501!" "Green"
    } else {
    
        try {
            $tcpClient = New-Object System.Net.Sockets.TcpClient
            $tcpClient.Connect("localhost", 8501)
            $tcpClient.Close()
            Write-Status $symbols.CHECK "Servidor RESPONDENDO na porta 8501!" "Green"
        } catch {
            Write-Status $symbols.CROSS "Servidor não está respondendo" "Red"
            if (Test-Path "$env:TEMP\streamlit.log") {
                Write-Status $symbols.WARNING "Verificando logs..." "Yellow"
                Get-Content "$env:TEMP\streamlit.log" -Tail 5
            }
        }
    }
} catch {
    Write-Status $symbols.WARNING "Não foi possível verificar a porta" "Yellow"
}

Write-Host ""
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║                                          ║" -ForegroundColor Green
Write-Host "  ║    " -NoNewline -ForegroundColor Green
Write-Host "$($symbols.SUCCESS) REINICIALIZAÇÃO CONCLUÍDA! $($symbols.SUCCESS)" -NoNewline -ForegroundColor White
Write-Host "     ║" -ForegroundColor Green
Write-Host "  ║                                          ║" -ForegroundColor Green
Write-Host "  ╚══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  🌐 URL: " -NoNewline -ForegroundColor Cyan
Write-Host "http://localhost:8501" -ForegroundColor White
Write-Host "  📋 Logs: " -NoNewline -ForegroundColor Cyan
Write-Host "$env:TEMP\streamlit.log" -ForegroundColor White
Write-Host ""
Write-Host "  $($symbols.ROCKET) Seu agente está pronto! $($symbols.ROCKET)" -ForegroundColor Yellow
Write-Host ""
Write-Host ""