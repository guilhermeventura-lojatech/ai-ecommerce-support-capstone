# Micro-capstone M1D1 — Atendimento inteligente em e-commerce

Projeto acadêmico de avaliação e prototipação de alternativas de IA para atendimento ao cliente.

## Contexto do caso
- E-commerce de médio porte com aproximadamente **25 mil solicitações mensais**.
- Atendimento atual realizado por pessoas, com tempo médio de resposta de **9 horas**.
- Dúvidas frequentes: status do pedido, trocas, prazo de entrega e reembolso.
- Objetivo: reduzir custo e tempo de resposta sem comprometer a qualidade.

## Alternativas avaliadas
1. Regras determinísticas e fluxos de atendimento.
2. Classificador de intenções baseado em Machine Learning.
3. Assistente baseado em LLM com fontes autorizadas.

**Recomendação do caso:** arquitetura híbrida, com regras, classificação e LLM controlado, com escalonamento humano.

## Estrutura
- `docs/` — análise, critérios, riscos e arquitetura.
- `knowledge/` — exemplos **fictícios** de FAQs para futura prova de conceito.
- `backend/` — espaço reservado para a API e os testes.
- `frontend/` — espaço reservado para interface demonstrativa.
- `examples/` — exemplos de solicitações sintéticas.

## Estado atual
**Etapa 1: documentação e estrutura inicial.** Ainda não há aplicação executável nem resultados de experimentos. Políticas de exemplo e métricas futuras não representam dados reais da empresa.

## Próximos passos
- Implementar motor de regras e casos de teste.
- Avaliar classificador de intenções sobre exemplos sintéticos.
- Opcionalmente integrar LLM com documentação autorizada e saída segura.
- Comparar desempenho, custos e riscos; registrar as evidências.

## Execução
Nenhuma configuração necessária nesta fase: os arquivos são Markdown e exemplos locais.
