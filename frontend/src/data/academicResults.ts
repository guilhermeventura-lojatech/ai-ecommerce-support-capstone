export const intentLabels = ['Entrega', 'Troca', 'Reembolso', 'Pagamento', 'Cancelamento']

export const testMetrics = {
  sampleCount: 19,
  correct: 13,
  accuracy: 0.6842105263157895,
  macroPrecision: 0.7333333333333333,
  macroRecall: 0.7,
  macroF1: 0.6890476190476191,
}

export const confusionMatrix = [
  [3, 0, 0, 0, 1],
  [0, 3, 0, 0, 0],
  [0, 1, 2, 1, 0],
  [1, 0, 0, 3, 0],
  [0, 0, 0, 2, 2],
]

export const routingComparison = [
  {
    label: 'Regras isoladas',
    accuracy: 0.15789473684210525,
    coverage: 0.21052631578947367,
    correct: '3/19',
    safe: true,
  },
  {
    label: 'Regras + ML seguro',
    accuracy: 0.15789473684210525,
    coverage: 0.21052631578947367,
    correct: '3/19',
    safe: true,
  },
  {
    label: 'ML bruto diagnóstico',
    accuracy: 0.631578947368421,
    coverage: 1,
    correct: '12/19',
    safe: false,
  },
]

export const exampleQuestions = [
  { label: 'Entrega', text: 'Onde vejo o rastreio?' },
  { label: 'Troca', text: 'Posso trocar o produto que recebi?' },
  { label: 'Reembolso', text: 'Quando recebo meu reembolso?' },
  { label: 'Pagamento', text: 'Meu cartão foi recusado mesmo com limite' },
  { label: 'Cancelamento', text: 'Quero desistir da compra antes do envio' },
  { label: 'Fora de escopo', text: 'Qual a temperatura prevista para Marte amanhã?' },
]

