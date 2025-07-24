#!/usr/bin/make -f

.PHONY: playground

SHELL := /bin/bash

# Color definitions
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[1;37m
BOLD := \033[1m
BLINK := \033[5m
NC := \033[0m

# Symbol definitions
CHECK := ✓
ROCKET := 🚀
GEAR := ⚙️
PORT := 🌐
SUCCESS := ✨
TIMER := ⏳

# Helper functions
define print_banner
	@echo
	@echo -e "$(CYAN)    ╔══════════════════════════════════════════╗$(NC)"
	@echo -e "$(CYAN)    ║                                          ║$(NC)"
	@echo -e "$(CYAN)    ║    $(YELLOW)$(BOLD)🔄  ADK PLAYGROUND SYSTEM  🔄$(NC)$(CYAN)      ║$(NC)"
	@echo -e "$(CYAN)    ║                                          ║$(NC)"
	@echo -e "$(CYAN)    ╚══════════════════════════════════════════╝$(NC)"
	@echo
endef

define print_status
	@echo -e "  $(1)  $(2)$(3)$(NC)"
endef

define print_divider
	@echo -e "  $(WHITE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
endef

playground:
	$(call print_banner)
	
	@for i in 1 2 3; do \
		echo -ne "\r    $(YELLOW)$(ROCKET) Inicializando sistema ADK Playground$(NC)"; \
		for j in 1 2 3; do \
			echo -n "."; \
			sleep 0.1; \
		done; \
		echo -ne "\r                                          \r"; \
	done
	@echo
	
	$(call print_status,$(GEAR),$(BLUE)$(BOLD),CONFIGURANDO ADK PLAYGROUND)
	$(call print_divider)
	@echo
	
	$(call print_status,$(TIMER),$(YELLOW),Preparando ambiente de execução...)
	@sleep 1
	$(call print_status,$(CHECK),$(GREEN),Ambiente preparado!)
	@echo
	
	$(call print_status,$(ROCKET),$(PURPLE)$(BOLD),INICIANDO ADK PLAYGROUND)
	$(call print_divider)
	$(call print_status,$(PORT),$(CYAN),Servidor: $(WHITE)$(BOLD)http://localhost:8501$(NC))
	$(call print_status,$(GEAR),$(CYAN),Comando: $(WHITE)uv run adk web --port 8501$(NC))
	@echo
	
	@echo -e "$(GREEN)$(BOLD)  ╔══════════════════════════════════════════╗$(NC)"
	@echo -e "$(GREEN)$(BOLD)  ║                                          ║$(NC)"
	@echo -e "$(GREEN)$(BOLD)  ║    $(SUCCESS) ADK PLAYGROUND INICIADO! $(SUCCESS)        ║$(NC)"
	@echo -e "$(GREEN)$(BOLD)  ║                                          ║$(NC)"
	@echo -e "$(GREEN)$(BOLD)  ╚══════════════════════════════════════════╝$(NC)"
	@echo
	@echo -e "$(CYAN)  🌐 Acesse: $(WHITE)$(BOLD)http://localhost:8501$(NC)"
	@echo -e "$(CYAN)  📋 Comando: $(WHITE)make playground$(NC)"
	@echo -e "$(CYAN)  🛑 Parar: $(WHITE)Ctrl+C$(NC)"
	@echo
	@echo -e "$(YELLOW)$(BLINK)  $(ROCKET) ADK Playground está pronto! $(ROCKET)$(NC)"
	@echo
	@echo -e "$(CYAN)────────────────────────────────────────────────$(NC)"
	@echo
	uv run adk web --port 8501