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
**Etapa 3: recuperação e LLM controlado.** A API preserva regras e classificação,
recupera trechos da FAQ autorizada por TF-IDF e possui integração opcional com
LLM. A integração fica desligada por padrão e todo caso sem evidência verificável
é escalonado. Não há frontend ou consulta a sistemas reais.

## Próximos passos
- Implementar motor de regras e casos de teste.
- Avaliar classificador de intenções sobre exemplos sintéticos.
- Avaliar opcionalmente um LLM real autorizado, mantendo limites e saída segura.
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

Para reproduzir as métricas e a matriz de confusão do experimento:

```powershell
python scripts/evaluate_ml.py
python scripts/compare_routing.py
```

Os limiares experimentais podem ser configurados antes de iniciar a API:

```powershell
$env:ML_CONFIDENCE_THRESHOLD = "0.35"
$env:ML_MIN_KNOWN_TOKEN_RATIO = "0.20"
```

Metodologia, resultados observados e limitações estão em
`docs/avaliacao-ml.md`. Recuperação, integração opcional, controles e riscos do
LLM estão em `docs/avaliacao-llm.md`.

## Limites atuais

- Apenas orientação genérica de rastreio possui resposta automática autorizada.
- Trocas e reembolsos são reconhecidos, mas escalonados por falta de política autorizada.
- O classificador identifica cinco intenções, mas não autoriza respostas.
- Não existe consulta a pedidos, pagamentos, clientes ou serviços externos.
- No modo padrão não são usados dados pessoais reais, chaves ou chamadas de LLM.
- As probabilidades do modelo não são calibradas e o dataset é sintético.
- O LLM é opcional e desligado por padrão; os testes não fazem chamadas externas.
