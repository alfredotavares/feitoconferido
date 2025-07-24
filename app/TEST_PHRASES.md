## 🟢 **Cenário de Sucesso Completo**
```
Valide o ticket PDI-12345
```
Resultado esperado: APPROVED com todos os 4 estágios completados

## 🔴 **Cenários de Falha**

### Ticket sem componentes:
```
Valide o PDI-99999
```
Resultado esperado: FAILED - "No components found in ticket"

### PDI já concluído:
```
Faça a validação do PDI-DONE
```
Resultado esperado: FAILED - "PDI has completed status - cannot proceed"

### Componentes não aprovados na VT:
```
Valide o ticket PDI-UNAPPROVED
```
Resultado esperado: FAILED - "Components not approved in VT: payment-service, billing-service"

## ⚠️ **Cenário com Ação Manual**
```
Valide o PDI-GATEWAY com o avaliador João Silva
```
Resultado esperado: REQUIRES_MANUAL_ACTION - API Gateway precisa verificação manual

## 🔧 **Validação de Repositório**
```
Valide o repositório https://github.com/company/legacy-service
```
Resultado esperado: Faltando especificação OpenAPI

## 💥 **Cenários de Erro**

### Erro de conexão Jira:
```
Verifique o PDI-ERROR
```
Resultado esperado: FAILED - "Failed to fetch Jira ticket: Connection timeout"

### Erro ao criar ARQCOR:
```
Valide o ticket PDI-ARQCOR-ERROR
```
Resultado esperado: FAILED no estágio 2 - "Failed to create ARQCOR form"

**Dica**: Comece com `Valide o ticket PDI-12345` para ver um fluxo completo de sucesso, depois teste os outros cenários para ver como o agent se comporta em situações de erro!
