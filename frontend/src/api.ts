import type { SupportResponse } from './types'

const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly kind: 'connection' | 'response',
  ) {
    super(message)
  }
}

export async function sendSupportMessage(message: string): Promise<SupportResponse> {
  let response: Response
  try {
    response = await fetch(`${API_URL}/support/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    })
  } catch {
    throw new ApiError(
      'Não foi possível conectar à API local. Confirme se o backend está em execução.',
      'connection',
    )
  }

  if (!response.ok) {
    throw new ApiError(`A API retornou o status ${response.status}.`, 'response')
  }
  return response.json() as Promise<SupportResponse>
}

