# Script para reiniciar agente que não responde no PowerShell
# Uso: .\restart_agent.ps1

Write-Host "Iniciando reinicialização do agente..." -ForegroundColor Green

# 1. Kill TODOS os processos relacionados
Write-Host "Matando processos relacionados..." -ForegroundColor Yellow

$processNames = @("adk", "uvicorn", "playground", "streamlit")
foreach ($processName in $processNames) {
    Get-Process | Where-Object { $_.ProcessName -match $processName -or $_.CommandLine -match $processName } | ForEach-Object {
        try {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            Write-Host "Processo terminado: $($_.ProcessName) (PID: $($_.Id))" -ForegroundColor Red
        } catch {
            # Ignorar erros se o processo já não existir
        }
    }
}

# Liberar porta 8501
try {
    $connection = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
    if ($connection) {
        Stop-Process -Id $connection.OwningProcess -Force -ErrorAction SilentlyContinue
        Write-Host "Porta 8501 liberada" -ForegroundColor Red
    }
} catch {
    # Ignorar se a porta não estiver em uso
}

# Aguardar um pouco para os processos terminarem
Start-Sleep -Seconds 2

# Verificar se processos foram terminados
Write-Host "Verificando se processos foram terminados..." -ForegroundColor Yellow
$remainingProcesses = Get-Process | Where-Object { 
    $_.ProcessName -match "adk|uvicorn|playground|streamlit" -or 
    $_.CommandLine -match "adk|uvicorn|playground|streamlit" 
}

if ($remainingProcesses) {
    Write-Host "Processos ainda em execução:" -ForegroundColor Red
    $remainingProcesses | Format-Table Id, ProcessName, CPU -AutoSize
} else {
    Write-Host "Nenhum processo antigo encontrado" -ForegroundColor Green
}

# 2. Limpe completamente o cache
Write-Host "Limpando cache..." -ForegroundColor Yellow

# Limpar __pycache__ recursivamente
Get-ChildItem -Path . -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Limpar arquivos .pyc
Get-ChildItem -Path . -File -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

# Limpar cache do uv se existir
if (Get-Command uv -ErrorAction SilentlyContinue) {
    & uv cache clean 2>$null
    Write-Host "Cache do uv limpo" -ForegroundColor Green
}

# 3. Aguarde mais tempo para garantir limpeza completa
Write-Host "Aguardando limpeza completa..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 4. Verifique se nenhum processo está rodando
Write-Host "Verificando processos restantes..." -ForegroundColor Yellow
$stillRunning = Get-Process | Where-Object { 
    $_.ProcessName -match "adk|uvicorn|playground|streamlit" -or 
    $_.CommandLine -match "adk|uvicorn|playground|streamlit" 
}

if ($stillRunning) {
    Write-Host "Ainda existem processos rodando, forçando terminação..." -ForegroundColor Red
    $stillRunning | ForEach-Object {
        try {
            Stop-Process -Id $_.Id -Force -ErrorAction Stop
            Write-Host "Processo forçadamente terminado: $($_.ProcessName) (PID: $($_.Id))" -ForegroundColor Red
        } catch {
            Write-Host "Não foi possível terminar processo: $($_.ProcessName) (PID: $($_.Id))" -ForegroundColor DarkRed
        }
    }
    Start-Sleep -Seconds 3
} else {
    Write-Host "Nenhum processo encontrado" -ForegroundColor Green
}

# 5. Teste uma última vez se está funcionando
Write-Host "Testando funcionalidade básica..." -ForegroundColor Yellow

# Primeiro, tenta encontrar o arquivo app.py
$appPaths = @(
    ".\app.py",
    ".\src\app.py",
    ".\playground\app.py",
    (Get-ChildItem -Path . -File -Recurse -Filter "app.py" -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
)

$appPath = $null
foreach ($path in $appPaths) {
    if ($path -and (Test-Path $path)) {
        $appPath = $path
        break
    }
}

if ($appPath -and (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Executando teste no arquivo: $appPath" -ForegroundColor Cyan
    $projectDir = Split-Path -Parent $appPath
    Push-Location $projectDir
    
    $testScript = @"
try:
    from app import root_agent
    result = root_agent('teste')
    print('Teste passou:', result)
except Exception as e:
    print('Erro no teste:', str(e))
"@
    
    $testResult = & uv run python -c $testScript 2>&1
    Write-Host $testResult -ForegroundColor Cyan
    Pop-Location
} else {
    Write-Host "uv não encontrado ou app.py não localizado, pulando teste" -ForegroundColor Yellow
}

# 6. Reinicie o playground
Write-Host "Reiniciando playground..." -ForegroundColor Green

# Procurar por Makefile
$makefilePaths = @(
    ".\Makefile",
    ".\playground\Makefile",
    "..\Makefile",
    (Get-ChildItem -Path . -File -Recurse -Filter "Makefile" -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
)

$makefilePath = $null
foreach ($path in $makefilePaths) {
    if ($path -and (Test-Path $path)) {
        $content = Get-Content $path -ErrorAction SilentlyContinue
        if ($content -match "playground") {
            $makefilePath = $path
            break
        }
    }
}

if ($makefilePath -and (Get-Command make -ErrorAction SilentlyContinue)) {
    $makefileDir = Split-Path -Parent $makefilePath
    Write-Host "Executando make playground no diretório: $makefileDir" -ForegroundColor Cyan
    Push-Location $makefileDir
    & make playground
    Pop-Location
} else {
    Write-Host "Makefile não encontrado ou target 'playground' não existe" -ForegroundColor Yellow
    Write-Host "Comandos alternativos para tentar:" -ForegroundColor Cyan
    Write-Host "   - uv run streamlit run app.py --port 8501"
    Write-Host "   - python -m uvicorn app:app --host 0.0.0.0 --port 8501"
    Write-Host "   - streamlit run app.py"
    
    if ((Get-Command uv -ErrorAction SilentlyContinue) -and $appPath) {
        Write-Host "Tentando iniciar com uv run streamlit..." -ForegroundColor Green
        $appDir = Split-Path -Parent $appPath
        Push-Location $appDir
        Start-Process -FilePath "uv" -ArgumentList "run", "streamlit", "run", "app.py", "--port", "8501" -WindowStyle Hidden
        Pop-Location
        Write-Host "Comando executado em background" -ForegroundColor Green
    }
}

Write-Host "`nReinicialização concluída!" -ForegroundColor Green

# 7. Verificação final
Write-Host "`nVerificação final dos processos:" -ForegroundColor Yellow
$finalCheck = Get-Process | Where-Object { 
    $_.ProcessName -match "adk|uvicorn|playground|streamlit" -or 
    $_.CommandLine -match "adk|uvicorn|playground|streamlit" 
}

if ($finalCheck) {
    Write-Host "Processos em execução:" -ForegroundColor Cyan
    $finalCheck | Format-Table Id, ProcessName, CPU -AutoSize
} else {
    Write-Host "Nenhum processo encontrado" -ForegroundColor Green
}

# Verificar se a porta 8501 está sendo usada
try {
    $portCheck = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue
    if ($portCheck) {
        Write-Host "`nPorta 8501 está em uso pelo processo PID: $($portCheck.OwningProcess)" -ForegroundColor Green
    } else {
        Write-Host "`nPorta 8501 está livre" -ForegroundColor Yellow
    }
} catch {
    Write-Host "`nNão foi possível verificar o status da porta 8501" -ForegroundColor Yellow
}