# Recuperacao de conhecimento e LLM controlado — Etapa 3

## Escopo e estado observado

Esta etapa implementa recuperacao lexical sobre a FAQ ficticia autorizada e uma
integracao opcional com endpoint compativel com o formato de chat completions.
O LLM permanece **desligado por padrao**. Nenhuma API real ou paga foi chamada
durante a avaliacao e nenhuma resposta de duble de teste e apresentada como
resultado de um modelo real.

Os 39 testes passaram localmente. Eles demonstram controles de fluxo, nao
qualidade linguistica de um LLM externo.

## Arquitetura RAG simplificada

```text
mensagem
  -> regras deterministicas
  -> classificador ML e thresholds
  -> deteccao de prompt injection
  -> recuperacao TF-IDF na FAQ autorizada
  -> validacao de relevancia, intencao e ambiguidade
  -> LLM opcional com somente os trechos recuperados
  -> citacoes + verificacao lexical + bloqueio de alegacoes
  -> resposta ou escalonamento humano
```

A recuperacao transforma somente os tres itens de `knowledge/faq-exemplo.md` em
trechos identificados:

- `faq-001-acompanhar-pedido` — entrega;
- `faq-002-troca` — troca;
- `faq-003-reembolso` — reembolso.

Cada resultado inclui ID, caminho, intencao e similaridade por cosseno. O limiar
lexical e `0,18`, com no maximo dois trechos. Fonte ausente, fonte de outra
intencao ou resultados ambiguos provocam escalonamento.

## Fronteiras de confianca

- A FAQ e a unica fonte permitida nesta etapa.
- O caminho da fonte e fixo no codigo; a mensagem nao escolhe arquivos.
- Conteudo recuperado e mensagem do cliente sao delimitados como dados nao
  confiaveis, nunca como instrucoes.
- A chamada exige uma resposta JSON com texto e IDs de fontes citadas.
- Citacoes vazias ou desconhecidas sao rejeitadas.
- Uma verificacao lexical exige sobreposicao minima com o contexto.
- Valores monetarios, prazos numericos e afirmacoes de status individual sao
  bloqueados por validacao conservadora.
- Padroes evidentes de prompt injection sao escalonados antes da chamada.
- Qualquer falha, timeout, formato invalido ou rejeicao de seguranca retorna a
  mensagem segura de escalonamento.

Esses controles reduzem risco, mas nao provam fidelidade factual. Sobreposicao
lexical nao equivale a verificacao semantica, e listas de padroes podem ser
contornadas.

## Integracao opcional

Por padrao:

```text
LLM_ENABLED=false
```

Nesse modo, a aplicacao e todos os testes funcionam sem chave, rede ou pagamento.
Quando uma fonte relevante existe, a auditoria registra
`LLM_DISABLED_SAFE_FALLBACK` e encaminha a humano; nenhuma resposta simulada e
rotulada como LLM.

Para um experimento autorizado com endpoint compativel, configurar no PowerShell:

```powershell
$env:LLM_ENABLED = "true"
$env:LLM_PROVIDER = "openai_compatible"
$env:LLM_API_BASE_URL = "https://endpoint-autorizado.example/v1/chat/completions"
$env:LLM_API_KEY = "chave-fornecida-fora-do-git"
$env:LLM_MODEL = "modelo-autorizado"
$env:LLM_TIMEOUT_SECONDS = "10"
$env:LLM_MAX_CALLS = "20"
$env:LLM_MAX_INPUT_TOKENS = "2000"
$env:LLM_MAX_OUTPUT_TOKENS = "300"
$env:LLM_MAX_BUDGET_USD = "1.00"
```

A URL acima e apenas ilustrativa e nao e um servico configurado pelo projeto.
As credenciais ficam somente no ambiente e nao sao gravadas em logs ou auditoria.

Custos por milhao de tokens podem ser informados para estimativa:

```powershell
$env:LLM_INPUT_COST_PER_MILLION_TOKENS = "0"
$env:LLM_OUTPUT_COST_PER_MILLION_TOKENS = "0"
```

Com taxas iguais a zero, custo permanece desconhecido para fins praticos e nao
deve ser interpretado como gratuito. Chamadas e tokens ainda possuem limites. O
controle de orcamento e conservador e baseado nas taxas configuradas; sem taxas
corretas ele nao substitui limites do provedor.

## Auditoria

Quando aplicavel, a resposta registra:

- rota e motivo;
- duracao total e ID de correlacao;
- IDs, caminhos e scores das fontes;
- provedor e modelo;
- tokens de entrada, saida e total, se retornados;
- custo estimado, se houver taxas e consumo;
- resultado da verificacao de seguranca.

Chaves e cabecalhos de autenticacao nunca fazem parte do schema de auditoria.

## Resultados observados

- 39 testes aprovados, incluindo os 25 existentes.
- Recuperacao encontrou `faq-001-acompanhar-pedido` para uma consulta de
  acompanhamento e retornou lista vazia para assunto nao relacionado.
- LLM desabilitado produziu fallback com fonte rastreavel.
- Dublês locais confirmaram os caminhos de resposta fundamentada, timeout,
  citacao invalida, prazo inventado, limite de chamadas e prompt injection.
- Nenhuma metrica de qualidade, latencia ou custo de LLM real foi produzida.

Os resultados originais do ML permanecem em `docs/avaliacao-ml.md`, incluindo
accuracy de teste `13/19 = 0,6842` e macro F1 `0,689`.

## Riscos e limitacoes

- Base de conhecimento com apenas tres trechos ficticios.
- Recuperacao lexical e sensivel ao vocabulario e nao entende sinonimos de forma
  robusta.
- Classificador e thresholds continuam sendo um baseline sintetico.
- Nao ha calibracao probabilistica.
- Nao ha avaliacao com um LLM real nesta etapa.
- Validacao lexical pode rejeitar uma boa parafrase ou aceitar texto superficial.
- Deteccao de prompt injection por padroes nao cobre ataques desconhecidos.
- O contador de chamadas e orcamento vive somente na memoria do processo.
- Em multiplos processos, cada processo teria seu proprio contador.
- Custo depende de taxas configuradas manualmente e do consumo informado pelo
  provedor.
- A integracao nao realiza acoes nem consultas sobre pedidos reais.
- Uma fonte relevante ainda nao garante que exista informacao suficiente para
  resolver o caso do cliente.
