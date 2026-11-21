# Metodologia experimental

## 1. Objetivo

Medir um baseline reproduzível de classificação de intenção e comparar o
comportamento de regras isoladas, regras + ML com controles e ML bruto apenas
para diagnóstico. A metodologia não estima impacto financeiro ou operacional.

## 2. Classificação dos dados

| Categoria | Conteúdo |
| --- | --- |
| Dados do caso | 25.000 solicitações/mês, 9 horas de resposta, atendimento humano |
| Hipóteses | recorrência de dúvidas, utilidade de ML, benefício potencial de recuperação |
| Dados sintéticos | 125 mensagens, FAQ, exemplos, respostas e fila humana simulada |
| Resultados observados | métricas ML, matrizes, testes e build |
| Não medido | custo, CSAT, economia, resolução, reabertura, latência de produção |

## 3. Dataset

`data/intents_ecommerce_ptbr.csv` contém 125 mensagens sintéticas, balanceadas em
25 exemplos para cada classe:

- entrega;
- troca;
- reembolso;
- pagamento;
- cancelamento.

As frases variam contexto e construção; não são somente trocas mecânicas de
sinônimos. O carregador normaliza caixa, acentos e caracteres de palavra para
detectar duplicatas. IDs duplicados também geram erro.

## 4. Split e prevenção de vazamento

`train_test_split` é chamado duas vezes com `random_state=42` e estratificação:

1. 70% treino e 30% temporário;
2. temporário dividido igualmente entre validação e teste.

Tamanhos efetivos: 87 treino, 19 validação e 19 teste. Testes automatizados
confirmam reprodução, presença das cinco classes e disjunção dos IDs.

## 5. Pipeline e parâmetros

```text
mensagem
  -> TfidfVectorizer
     lowercase=true
     strip_accents=unicode
     ngram_range=(1,2)
     sublinear_tf=true
  -> LogisticRegression
     C=1.0
     class_weight=balanced
     max_iter=1000
     random_state=42
```

Não houve fine-tuning, embeddings externos ou otimização sobre o teste.

## 6. Protocolo de avaliação

O script `scripts/evaluate_ml.py`:

1. carrega e valida o dataset;
2. reproduz o split;
3. treina somente em treino;
4. mede validação e teste;
5. imprime JSON com métricas e matrizes.

Métricas:

- accuracy;
- precision macro;
- recall macro;
- macro F1;
- precision, recall e F1 por classe;
- matriz de confusão.

Macro F1 foi priorizada porque atribui igual peso às classes. O balanceamento do
dataset simplifica o experimento, mas não representa prevalência real.

## 7. Resultados preservados

| Conjunto | N | Accuracy | Precision macro | Recall macro | Macro F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Validação | 19 | 0,579 | 0,567 | 0,567 | 0,559 |
| Teste | 19 | 0,684 | 0,733 | 0,700 | 0,689 |

Matriz de teste:

```text
                 predita
real             ent  tro  ree  pag  can
entrega           3    0    0    0    1
troca             0    3    0    0    0
reembolso         0    1    2    1    0
pagamento         1    0    0    3    0
cancelamento      0    0    0    2    2
```

Diagonal: 13. Total: 19. Accuracy: `13/19 = 0,6842105263`.

## 8. Comparação de estratégias

`scripts/compare_routing.py` treina o classificador somente nos 87 casos de
treino e usa o conjunto de teste rotulado.

| Estratégia | Cobertura | Acertos | Observação |
| --- | ---: | ---: | --- |
| Regras | 4/19 | 3/19 | intenção desconhecida quando não há regra |
| Regras + ML seguro | 4/19 | 3/19 | 15 fallbacks após thresholds |
| Híbrido com ML bruto | 19/19 | 12/19 | diagnóstico; não é política segura |

A comparação não mede resolução automática. Algumas regras reconhecem a intenção,
mas deliberadamente escalam por falta de política.

## 9. Thresholds e fora de escopo

- confiança mínima: 0,35;
- razão mínima de tokens conhecidos: mensagens com valor ≤ 0,20 são rejeitadas.

Os thresholds são heurísticos. `predict_proba` não foi calibrado e não deve ser
interpretado como probabilidade operacional de acerto.

## 10. Recuperação e LLM

A recuperação foi testada com consultas controladas sobre três trechos da FAQ.
Foram medidos comportamento e fallback, não recall/precision de recuperação em um
corpus representativo.

A integração LLM foi testada apenas com dublês locais para contrato, limites,
timeout, citação, segurança e fallback. Não foram medidos qualidade, custo ou
latência de uma LLM real.

## 11. Testes de engenharia

- unitários: regras, dataset, classificador, recuperação e segurança;
- integração: endpoints, roteamento, CORS e contrato frontend;
- regressão: métricas, matriz, precedência e fallbacks;
- build: TypeScript e bundle Vite.

## 12. Reprodutibilidade

Na raiz:

```powershell
python scripts/evaluate_ml.py
python scripts/compare_routing.py
python -m pytest
```

No frontend:

```powershell
npm test
npm run build
```

## 13. Validade e ameaças

- **validade interna:** seed e split são reproduzíveis, mas o conjunto é pequeno;
- **validade externa:** não há dados reais, portanto generalização não foi testada;
- **validade de constructo:** acerto de intenção não equivale a resolução ou satisfação;
- **vazamento semântico:** frases sintéticas podem compartilhar padrões de autoria;
- **viés de seleção:** classes foram escolhidas e balanceadas artificialmente;
- **incerteza:** 19 casos produzem grande variância e não foram calculados intervalos;
- **efeito de threshold:** segurança reduziu cobertura a ponto de eliminar o ganho observado.

## 14. Metas versus resultados

Macro F1 ≥ 0,80 é uma meta futura candidata, não resultado. O resultado observado
foi 0,689. Nenhuma meta de negócio foi definida ou alcançada porque não existem
dados reais de custo, satisfação ou operação.
