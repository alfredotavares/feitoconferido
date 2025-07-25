# Guia de Solução de Problemas - Ambiente Python e Scripts

Este guia apresenta soluções para os problemas mais comuns encontrados ao configurar e executar scripts Python em ambientes de desenvolvimento, especialmente em sistemas Unix/Linux.

## 📋 Índice de Problemas

- [1. Dependências Python Ausentes](#1-dependências-python-ausentes)
- [2. Permissões de Execução](#2-permissões-de-execução)
- [3. Problemas de Codificação (CRLF)](#3-problemas-de-codificação-crlf)
- [4. Exemplos Práticos](#4-exemplos-práticos)
- [5. Verificação e Diagnóstico](#5-verificação-e-diagnóstico)

---

## 1. Dependências Python Ausentes

### Problema
```bash
uv: No such file or directory
# ou
ModuleNotFoundError: No module named 'uv'
```

### Solução
```bash
# Instalar via pip
pip install uv

# Verificar instalação
uv --version
```

### Alternativas
```bash
# Para projetos que usam poetry
pip install poetry

# Para ambientes virtuais tradicionais
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

---

## 2. Permissões de Execução

### Problema
```bash
Permission denied
# ou
bash: ./script.sh: Permission denied
```

### Solução
```bash
# Conceder permissão de execução
chmod +x caminho/para/script.sh

# Verificar permissões atuais
ls -la caminho/para/script.sh
```

### Permissões Avançadas
```bash
# Apenas para o proprietário
chmod 744 script.sh

# Para proprietário e grupo
chmod 754 script.sh

# Recursivo para diretório
chmod -R +x diretorio/
```

---

## 3. Problemas de Codificação (CRLF)

### Problema
```bash
/bin/bash^M: bad interpreter: No such file or directory
# ou
cannot execute: required file not found
```

**Causa:** Arquivos criados no Windows contêm caracteres de quebra de linha incompatíveis (`\r\n` em vez de `\n`).

### Solução Completa

#### Passo 1: Instalar ferramenta de conversão
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y dos2unix

# CentOS/RHEL
sudo yum install dos2unix

# macOS
brew install dos2unix
```

#### Passo 2: Converter arquivo
```bash
# Método seguro (cria backup)
dos2unix -b script.sh

# Método direto (sem backup)
dos2unix script.sh
```

#### Passo 3: Restaurar permissões
```bash
chmod +x script.sh
```

### Método Alternativo (sem dos2unix)
```bash
# Usando sed
sed -i 's/\r$//' script.sh
chmod +x script.sh

# Usando tr
tr -d '\r' < script_original.sh > script_corrigido.sh
mv script_corrigido.sh script_original.sh
chmod +x script_original.sh
```

---

## 4. Exemplos Práticos

### Cenário 1: Script de inicialização de agente
```bash
# Problema comum com start_agent.sh
sudo apt-get update && sudo apt-get install -y dos2unix
dos2unix ./scripts/bash/start_agent.sh (ou tr -d '\r' < ./scripts/bash/start_agent.sh > ./scripts/bash/start_agent_fixed.sh)
mv ./scripts/bash/start_agent_fixed.sh ./scripts/bash/start_agent.sh
chmod +x ./scripts/bash/start_agent.sh

# Executar
./scripts/bash/start_agent.sh
```

### Cenário 2: Múltiplos scripts em um diretório
```bash
# Corrigir todos os scripts .sh em um diretório
find ./scripts -name "*.sh" -exec dos2unix {} \;
find ./scripts -name "*.sh" -exec chmod +x {} \;
```

### Cenário 3: Setup completo de projeto
```bash
#!/bin/bash
# Script de setup automático

echo "🔧 Configurando ambiente..."

# 1. Instalar dependências Python
pip install uv poetry

# 2. Corrigir scripts
echo "📝 Corrigindo formatação de scripts..."
find . -name "*.sh" -exec dos2unix {} \; 2>/dev/null || echo "dos2unix não encontrado, instalando..."
sudo apt-get update && sudo apt-get install -y dos2unix
find . -name "*.sh" -exec dos2unix {} \;

# 3. Aplicar permissões
echo "🔐 Aplicando permissões..."
find . -name "*.sh" -exec chmod +x {} \;

echo "✅ Setup concluído!"
```

---

## 5. Verificação e Diagnóstico

### Verificar tipo de arquivo
```bash
# Identificar tipo de quebra de linha
file script.sh
# Saída esperada: "ASCII text" (Unix) ou "ASCII text, with CRLF line terminators" (Windows)
```

### Verificar permissões
```bash
# Listar permissões detalhadas
ls -la script.sh
# Exemplo de saída: -rwxr-xr-x (executável)
```

### Verificar instalações Python
```bash
# Verificar Python e pip
python --version
pip --version

# Verificar ferramentas específicas
uv --version
poetry --version
```

### Debug de execução
```bash
# Executar com debug
bash -x script.sh

# Verificar shebang
head -1 script.sh
# Deve mostrar algo como: #!/bin/bash
```

---

## 🚨 Dicas de Prevenção

1. **Configure seu editor:** Use editores que preservem quebras de linha Unix (LF)
   - VS Code: Configure `"files.eol": "\n"`
   - Git: Configure `git config core.autocrlf false`

2. **Use templates:** Crie scripts sempre em ambiente Unix quando possível

3. **Automatize:** Inclua verificações no seu CI/CD pipeline

4. **Documente:** Mantenha um registro dos comandos utilizados para setup

---