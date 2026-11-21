# Evidências de implementação e validação

## 1. Escopo da evidência

Este documento registra resultados reproduzidos no repositório. Dados de negócio
do caso, dados sintéticos e resultados medidos são mantidos separados. Não há
evidência de produção, economia, CSAT, redução real de tempo ou qualidade de LLM
real.

## 2. Comandos executados

Na raiz:

```powershell
python -m pytest
python scripts/evaluate_ml.py
python scripts/compare_routing.py
```

No frontend:

```powershell
npm test
npm run build
```

Verificação integrada adicional:

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:5173/"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

## 3. Testes efetivos

### Backend

```text
......................................... [100%]
41 passed, 1 warning
```

O warning é `StarletteDeprecationWarning` no `TestClient` atual e não representa
falha funcional.

Cobertura comportamental demonstrada pelos testes:

- regras, respostas autorizadas e escalonamento;
- validação do contrato HTTP;
- precedência das regras;
- cinco intenções;
- split, duplicatas e vazamento;
- métricas e matriz reproduzíveis;
- baixa confiança e fora de escopo;
- recuperação e ausência de fonte;
- LLM desligada, timeout, limites e resposta inválida;
- citações, prazo inventado e prompt injection;
- CORS local e rejeição de origem externa.

Arquivos: [`backend/tests/`](../backend/tests/),
[`pyproject.toml`](../pyproject.toml).

### Frontend

```text
Test Files  3 passed (3)
Tests       6 passed (6)
```

Os testes verificam cliente HTTP e falha de conexão, chat com o contrato real,
explicabilidade e consistência dos resultados acadêmicos.

Arquivos: [`frontend/src/App.test.tsx`](../frontend/src/App.test.tsx),
[`frontend/src/api.test.ts`](../frontend/src/api.test.ts),
[`frontend/src/data/academicResults.test.ts`](../frontend/src/data/academicResults.test.ts).

### Build

```text
36 modules transformed
dist/index.html                  0.58 kB
dist/assets/index-*.css         18.52 kB
dist/assets/index-*.js         240.40 kB
build concluído
```

Arquivos: [`frontend/package.json`](../frontend/package.json),
[`frontend/vite.config.ts`](../frontend/vite.config.ts).

## 4. Dataset e classificador

- total: 125 mensagens sintéticas;
- classes: cinco;
- 25 exemplos por classe;
- seed: 42;
- split: 87 treino, 19 validação e 19 teste;
- duplicatas: rejeitadas por ID e mensagem normalizada.

Arquivos: [`data/intents_ecommerce_ptbr.csv`](../data/intents_ecommerce_ptbr.csv),
[`backend/app/ml/dataset.py`](../backend/app/ml/dataset.py).

### Resultados observados

| Conjunto | Accuracy | Precision macro | Recall macro | Macro F1 |
| --- | ---: | ---: | ---: | ---: |
| Validação | 0,578947 | 0,566667 | 0,566667 | 0,559365 |
| Teste | 0,684211 | 0,733333 | 0,700000 | 0,689048 |

Arquivo de cálculo: [`backend/app/ml/evaluation.py`](../backend/app/ml/evaluation.py).
Script: [`scripts/evaluate_ml.py`](../scripts/evaluate_ml.py).

## 5. Matriz de confusão

Ordem: entrega, troca, reembolso, pagamento, cancelamento.

| Real \ Predita | Entrega | Troca | Reembolso | Pagamento | Cancelamento |
| --- | ---: | ---: | ---: | ---: | ---: |
| Entrega | 3 | 0 | 0 | 0 | 1 |
| Troca | 0 | 3 | 0 | 0 | 0 |
| Reembolso | 0 | 1 | 2 | 1 | 0 |
| Pagamento | 1 | 0 | 0 | 3 | 0 |
| Cancelamento | 0 | 0 | 0 | 2 | 2 |

Total `19`; diagonal `13`; accuracy `13/19 = 0,6842105263`.

O frontend preserva os mesmos valores em
[`frontend/src/data/academicResults.ts`](../frontend/src/data/academicResults.ts).

## 6. Comparação das estratégias

| Estratégia | Cobertos | Acertos | Accuracy total | Cobertura |
| --- | ---: | ---: | ---: | ---: |
| Regras isoladas | 4 | 3 | 0,157895 | 0,210526 |
| Regras + ML seguro | 4 | 3 | 0,157895 | 0,210526 |
| Regras + ML bruto, diagnóstico | 19 | 12 | 0,631579 | 1,000000 |

O fluxo seguro rejeitou 15 casos. O ML bruto não é política de produção.

Script: [`scripts/compare_routing.py`](../scripts/compare_routing.py).

## 7. Evidência de API

### Regra autorizada

Entrada:

```json
{"message":"Onde vejo o rastreio?"}
```

Saída observada, abreviada para omitir UUID e duração variáveis:

```json
{
  "route": "regra",
  "intent": "entrega",
  "requires_human": false,
  "audit": {
    "reason_code": "AUTHORIZED_FAQ_TRACKING_GUIDANCE",
    "rule_id": "FAQ-TRACKING-001",
    "knowledge_source": "knowledge/faq-exemplo.md"
  }
}
```

### Pagamento sem política autorizada

Entrada:

```json
{"message":"Meu cartao foi recusado mesmo com limite"}
```

Saída observada, abreviada:

```json
{
  "route": "humano",
  "intent": "pagamento",
  "requires_human": true,
  "audit": {
    "reason_code": "ML_INTENT_WITHOUT_AUTHORIZED_RESPONSE",
    "ml_confidence": 0.358479490420065,
    "ml_fallback_reason": "NO_AUTHORIZED_POLICY",
    "safety_result": "NO_RELEVANT_AUTHORIZED_SOURCE",
    "llm_provider": null
  }
}
```

### Baixa confiança

Entrada:

```json
{"message":"Qual a temperatura prevista para Marte amanha?"}
```

Saída observada, abreviada:

```json
{
  "route": "humano",
  "intent": "desconhecida",
  "requires_human": true,
  "audit": {
    "reason_code": "NO_AUTHORIZED_RULE_MATCH",
    "ml_confidence": 0.2994508901674483,
    "ml_fallback_reason": "LOW_CONFIDENCE"
  }
}
```

Implementação: [`backend/app/services/router.py`](../backend/app/services/router.py),
[`backend/app/services/rules.py`](../backend/app/services/rules.py),
[`backend/app/schemas.py`](../backend/app/schemas.py).

## 8. Recuperação e LLM

Evidências implementadas:

- três trechos autorizados com IDs estáveis;
- busca TF-IDF e cosseno;
- fonte ausente provoca fallback;
- `LLM_ENABLED=false` por padrão;
- dublês testam resposta estruturada, tokens, custo, timeout e limite;
- resposta sem citação ou com prazo inventado é rejeitada;
- prompt injection detectado antes da chamada.

Não há evidência de qualidade, latência ou custo de uma LLM real.

Arquivos: [`backend/app/knowledge/retriever.py`](../backend/app/knowledge/retriever.py),
[`backend/app/llm/provider.py`](../backend/app/llm/provider.py),
[`backend/app/llm/safety.py`](../backend/app/llm/safety.py),
[`docs/avaliacao-llm.md`](avaliacao-llm.md).

## 9. Frontend e integração local

Resultado observado em execução local:

```text
Frontend HTTP: 200
API HTTP: 200
Access-Control-Allow-Origin: http://127.0.0.1:5173
Caso de pagamento: route=humano, intent=pagamento, requires_human=true
LLM provider: null
```

O frontend mostra chat, escalonamento, explicabilidade, fontes, métricas e
narrativa acadêmica. Arquivos:
[`frontend/src/components/ChatWorkspace.tsx`](../frontend/src/components/ChatWorkspace.tsx),
[`frontend/src/components/ExplainabilityPanel.tsx`](../frontend/src/components/ExplainabilityPanel.tsx),
[`frontend/src/components/AcademicDashboard.tsx`](../frontend/src/components/AcademicDashboard.tsx).

## 10. Validação visual e screenshots

Não foram salvos screenshots em `docs/assets/`. O host de automação do navegador
estava indisponível na sessão de validação, portanto não houve inspeção visual
automatizada confiável. Foram verificadas estrutura responsiva em CSS, testes de
componentes, build e respostas HTTP. Essa evidência não substitui revisão manual
em desktop e mobile.

Nenhuma imagem foi inventada ou gerada para simular execução real.

## 11. Divergências identificadas

| Item | Estado real | Tratamento |
| --- | --- | --- |
| OpenAPI descreve “Etapa 1” | código atual inclui quatro etapas | registrado como metadado histórico |
| `/health.stage` é `foundation-backend` | não representa etapa final | preservado por compatibilidade |
| `avaliacao-llm.md` diz 39 testes | correto no marco da Etapa 3 | documentos finais registram 41 + 6 |
| LLM parece integrável | provedor real não foi testado | explicitamente classificado como opcional |
| Dashboard mostra métricas | valores são sintéticos e estáticos | teste confirma fidelidade aos scripts |

## 12. Limitações da evidência

- sem screenshots reais;
- sem teste de carga;
- sem cobertura de código calculada;
- sem scanner de segurança independente;
- sem avaliação com usuários;
- sem dados reais ou políticas oficiais;
- sem LLM real;
- sem métricas operacionais ou financeiras.
