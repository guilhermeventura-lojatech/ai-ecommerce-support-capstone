import { describe, expect, it } from 'vitest'
import { confusionMatrix, routingComparison, testMetrics } from './academicResults'

describe('academic results', () => {
  it('preserves the recorded 19 examples and 13 correct predictions', () => {
    const total = confusionMatrix.flat().reduce((sum, value) => sum + value, 0)
    const diagonal = confusionMatrix.reduce((sum, row, index) => sum + row[index], 0)

    expect(total).toBe(19)
    expect(diagonal).toBe(13)
    expect(testMetrics.accuracy).toBeCloseTo(13 / 19)
    expect(testMetrics.macroF1).toBeCloseTo(0.6890476190476191)
  })

  it('marks raw ML as diagnostic and not safe policy', () => {
    const rawMl = routingComparison.find((item) => item.label === 'ML bruto diagnóstico')

    expect(rawMl).toMatchObject({ safe: false, correct: '12/19', coverage: 1 })
  })
})
