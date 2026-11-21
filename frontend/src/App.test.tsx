import { afterEach, describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'

afterEach(() => vi.restoreAllMocks())

const apiResponse = {
  correlation_id: '11111111-1111-1111-1111-111111111111',
  route: 'regra',
  intent: 'entrega',
  answer: 'Para acompanhar um pedido, use o canal autorizado.',
  requires_human: false,
  audit: {
    correlation_id: '11111111-1111-1111-1111-111111111111',
    route: 'regra',
    reason_code: 'AUTHORIZED_FAQ_TRACKING_GUIDANCE',
    duration_ms: 1.25,
    rule_id: 'FAQ-TRACKING-001',
    knowledge_source: 'knowledge/faq-exemplo.md',
    model_version: null,
    ml_confidence: null,
    ml_known_token_ratio: null,
    ml_fallback_reason: null,
    sources: [],
    llm_provider: null,
    llm_model: null,
    llm_prompt_tokens: null,
    llm_completion_tokens: null,
    llm_total_tokens: null,
    llm_estimated_cost_usd: null,
    safety_result: null,
  },
}

describe('App', () => {
  it('sends an example and displays explainability from the API contract', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(apiResponse), { status: 200, headers: { 'Content-Type': 'application/json' } }),
    )
    render(<App />)

    await userEvent.click(screen.getByRole('button', { name: /Entrega Onde vejo o rastreio/i }))

    expect(await screen.findByText('Para acompanhar um pedido, use o canal autorizado.')).toBeInTheDocument()
    expect(screen.getByText('Regra determinística')).toBeInTheDocument()
    expect(screen.getByText('AUTHORIZED_FAQ_TRACKING_GUIDANCE')).toBeInTheDocument()
    expect(screen.getByText('knowledge/faq-exemplo.md')).toBeInTheDocument()
    expect(screen.getByText(/Não acionada/)).toBeInTheDocument()
  })

  it('shows an unavailable API state', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('network'))
    render(<App />)

    await userEvent.click(screen.getByRole('button', { name: /Pagamento Meu cartão/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent('API indisponível')
    expect(screen.getByRole('button', { name: 'Tentar novamente' })).toBeInTheDocument()
  })
})
