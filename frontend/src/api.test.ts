import { afterEach, describe, expect, it, vi } from 'vitest'
import { sendSupportMessage } from './api'

afterEach(() => vi.restoreAllMocks())

describe('sendSupportMessage', () => {
  it('posts the message to the local support endpoint', async () => {
    const payload = { correlation_id: 'abc', route: 'humano', intent: 'pagamento' }
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(payload), { status: 200, headers: { 'Content-Type': 'application/json' } }),
    )

    await expect(sendSupportMessage('Meu pagamento falhou')).resolves.toMatchObject(payload)
    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/support/messages',
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ message: 'Meu pagamento falhou' }) }),
    )
  })

  it('returns a clear connection error when the API is unavailable', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('network'))

    await expect(sendSupportMessage('Teste')).rejects.toEqual(
      expect.objectContaining({ kind: 'connection' }),
    )
  })
})
