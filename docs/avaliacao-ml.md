# Avaliacao do classificador de intencoes — Etapa 2

## Objetivo e escopo

Esta etapa avalia um baseline local de classificacao de intencoes para suporte de
e-commerce. O modelo nao responde ao cliente, nao consulta sistemas reais e nao
autoriza fluxos por conta propria. Regras deterministicas continuam com
precedencia e toda intencao sem resposta autorizada pela FAQ e escalonada.

Todos os dados deste experimento sao **sinteticos**. Os resultados nao representam
desempenho em operacao nem dados reais de uma empresa.

## Dataset

O arquivo versionado `data/intents_ecommerce_ptbr.csv` contem 125 mensagens em
portugues brasileiro, distribuidas igualmente entre cinco classes:

| Intencao | Exemplos |
| --- | ---: |
| entrega | 25 |
| troca | 25 |
| reembolso | 25 |
| pagamento | 25 |
| cancelamento | 25 |

As mensagens foram escritas para variar contexto, construcao e vocabulario. O
carregador normaliza caixa, acentos e espacos para rejeitar duplicatas. IDs e
mensagens duplicados geram erro antes do treinamento.

## Metodologia reproduzivel

- Seed fixa: `42`.
- Divisao estratificada: 70% treino, 15% validacao e 15% teste.
- Tamanhos observados: 87 treino, 19 validacao e 19 teste.
- Nao ha IDs compartilhados entre os conjuntos.
- O teste automatizado verifica reproducibilidade, estratificacao e vazamento.
- Vetorizacao: TF-IDF de palavras, unigramas e bigramas, acentos normalizados e
  frequencia sublinear.
- Classificador: `LogisticRegression`, `C=1.0`, `class_weight="balanced"`,
  `max_iter=1000` e `random_state=42`.
- O experimento ajusta o modelo apenas no treino e mede validacao e teste.
- O adaptador da API treina em memoria com o dataset completo depois da avaliacao,
  para aproveitar todos os exemplos no uso demonstrativo.

Comando executado a partir da raiz:

```powershell
python scripts/evaluate_ml.py
```

## Resultados observados

Estes valores foram medidos no dataset sintetico versionado; nao sao metas.

| Conjunto | Accuracy | Precision macro | Recall macro | F1 macro |
| --- | ---: | ---: | ---: | ---: |
| Validacao (19) | 0,579 | 0,567 | 0,567 | 0,559 |
| Teste (19) | 0,684 | 0,733 | 0,700 | 0,689 |

Metricas por classe no teste:

| Classe | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| entrega | 0,750 | 0,750 | 0,750 |
| troca | 0,750 | 1,000 | 0,857 |
| reembolso | 1,000 | 0,500 | 0,667 |
| pagamento | 0,500 | 0,750 | 0,600 |
| cancelamento | 0,667 | 0,500 | 0,571 |

Matriz de confusao do teste. Linhas sao classes reais e colunas sao classes
preditas, na ordem `entrega`, `troca`, `reembolso`, `pagamento`, `cancelamento`:

| Real \ Predita | entrega | troca | reembolso | pagamento | cancelamento |
| --- | ---: | ---: | ---: | ---: | ---: |
| entrega | 3 | 0 | 0 | 0 | 1 |
| troca | 0 | 3 | 0 | 0 | 0 |
| reembolso | 0 | 1 | 2 | 1 | 0 |
| pagamento | 1 | 0 | 0 | 3 | 0 |
| cancelamento | 0 | 0 | 0 | 2 | 2 |

Os numeros exatos, inclusive a matriz de validacao, sao emitidos em JSON pelo
script de avaliacao.

## Roteamento e limiares experimentais

- `ML_CONFIDENCE_THRESHOLD=0.35`: abaixo desse valor, a intencao exposta pela API
  passa a `desconhecida` e o caso e escalonado.
- `ML_MIN_KNOWN_TOKEN_RATIO=0.20`: mensagens com proporcao de tokens conhecidos
  menor ou igual ao limiar sao tratadas como fora de escopo e escalonadas.
- Previsao aceita sem politica autorizada tambem e escalonada, embora a intencao
  seja registrada para rastreabilidade.

O limiar de 0,35 e uma configuracao heuristica do prototipo. Foi escolhido para
nao rejeitar automaticamente previsoes coerentes cujas probabilidades ficam
dispersas no pequeno dataset. Ele nao representa probabilidade calibrada nem
nivel de risco validado.

## Metas futuras, separadas dos resultados

Antes de qualquer piloto, uma meta candidata e macro F1 de pelo menos 0,80 em
dados representativos e revisados. Esta meta **nao foi atingida** pelo baseline
atual e nao deve ser apresentada como resultado observado.

## Limitacoes

- Dataset pequeno, sintetico e criado para o mesmo estudo.
- Conjuntos de validacao e teste possuem apenas 19 exemplos cada; pequenas
  mudancas alteram as metricas significativamente.
- Nao ha exemplos reais, erros de digitacao sistematicos, variacao regional ou
  mensagens com multiplas intencoes em quantidade representativa.
- `predict_proba` da regressao logistica nao foi calibrado. Seus valores servem
  apenas como sinal experimental de roteamento.
- A heuristica de tokens conhecidos nao e um detector geral de fora de escopo.
- A avaliacao mede classificacao, nao resolucao, seguranca, satisfacao ou economia.
- O modelo pode aprender artefatos do texto sintetico.
- Nenhuma previsao concede permissao para inventar politica, prazo, status ou
  informacao de pagamento.
