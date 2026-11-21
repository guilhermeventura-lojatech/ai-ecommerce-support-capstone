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
**Etapa 1: fundação/backend.** Há uma API local com regras determinísticas
baseadas exclusivamente na FAQ fictícia e escalonamento humano simulado. Ainda
não há classificação ML, integração com LLM, consulta a sistemas de pedidos ou
resultados de experimentos. Políticas de exemplo e métricas futuras não
representam dados reais da empresa.

## Próximos passos
- Implementar motor de regras e casos de teste.
- Avaliar classificador de intenções sobre exemplos sintéticos.
- Opcionalmente integrar LLM com documentação autorizada e saída segura.
- Comparar desempenho, custos e riscos; registrar as evidências.

## Instalação e execução no Windows PowerShell

Requer Python 3.10 ou superior. A partir da raiz do repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
python -m uvicorn backend.app.main:app --reload
```

A API estará em `http://127.0.0.1:8000` e a documentação interativa em
`http://127.0.0.1:8000/docs`.

Exemplos em outro terminal PowerShell:

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/health"

$body = @{ message = "Onde vejo o rastreio?" } | ConvertTo-Json
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/support/messages" `
  -ContentType "application/json" `
  -Body $body
```

Para executar os testes automatizados:

```powershell
python -m pytest
```

## Limites da etapa 1

- Apenas orientação genérica de rastreio possui resposta automática autorizada.
- Trocas e reembolsos são reconhecidos, mas escalonados por falta de política autorizada.
- Demais casos são escalonados sem classificação automática.
- Não existe consulta a pedidos, pagamentos, clientes ou serviços externos.
- Não são usados dados pessoais reais, chaves de API, ML ou LLM.
