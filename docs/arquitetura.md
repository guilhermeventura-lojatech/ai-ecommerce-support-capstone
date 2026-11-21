# Arquitetura proposta (conceitual)

```mermaid
flowchart TD
    A[Mensagem do cliente] --> B[Regras e validações]
    B --> C{Caso determinístico resolvido?}
    C -->|Sim| D[Resposta padronizada]
    C -->|Não| E[Classificação de intenção]
    E --> F{Precisa de interpretação semântica?}
    F -->|Não| G[Fluxo estruturado]
    F -->|Sim| H[LLM com conteúdo autorizado]
    H --> I{Resposta fundamentada e segura?}
    I -->|Sim| J[Resposta ao cliente]
    I -->|Não| K[Escalonamento humano]
    G --> J
```

## Controles obrigatórios para futura implementação
- Consulta apenas a FAQs e políticas autorizadas; não inventar status, prazo ou reembolso de pedidos.
- Não incluir dados pessoais reais na prova de conceito.
- Resposta sem fonte suficiente deve levar ao atendimento humano.
- Registrar qual rota produziu a resposta e seus motivos.
- Definir limites de custo, testes e monitoramento antes do uso de API externa.
