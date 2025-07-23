# Guia Rápido de Solução de Problemas

Esta é uma lista de comandos essenciais para configurar o ambiente e corrigir problemas comuns de execução de scripts.

### 1. Instalar dependências de Python

Para resolver o erro `uv: No such file or directory`.
```bash
pip install uv
````

### 2\. Corrigir permissão de execução de scripts

Para resolver o erro `Permission denied`.

```bash
chmod +x [caminho_para_seu_script.sh]
```

### 3\. Corrigir quebras de linha (Formato Windows)

Para resolver o erro `cannot execute: required file not found` causado por caracteres `^M`.

**a. Instalar a ferramenta de correção:**

```bash
sudo apt-get update && sudo apt-get install -y dos2unix
```

**b. Converter o script (método de contorno):**

```bash
# Cria uma cópia corrigida
dos2unix < [script_original.sh] > [script_corrigido.sh]

# Substitui o original pelo corrigido
mv [script_corrigido.sh] [script_original.sh]

# Garante que a permissão de execução foi mantida
chmod +x [script_original.sh]
```
