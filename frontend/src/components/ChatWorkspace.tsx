import { FormEvent, useMemo, useRef, useState } from 'react'
import { ApiError, sendSupportMessage } from '../api'
import { exampleQuestions } from '../data/academicResults'
import type { ChatMessage, SupportResponse } from '../types'
import { HumanIcon, SendIcon, SparkIcon } from './Icons'

interface Props {
  onResponse: (response: SupportResponse) => void
}

const initialMessage: ChatMessage = {
  id: 'intro',
  role: 'assistant',
  text: 'Olá! Esta é uma demonstração acadêmica. Posso orientar apenas com a FAQ fictícia; casos sem política autorizada são encaminhados a uma pessoa.',
}

export function ChatWorkspace({ onResponse }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([initialMessage])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const lastFailedMessage = useRef<string | null>(null)
  const canSend = useMemo(() => input.trim().length > 0 && !loading, [input, loading])

  async function submit(message: string) {
    const normalized = message.trim()
    if (!normalized || loading) return
    setError(null)
    setLoading(true)
    setInput('')
    setMessages((current) => [...current, { id: crypto.randomUUID(), role: 'user', text: normalized }])
    try {
      const response = await sendSupportMessage(normalized)
      setMessages((current) => [
        ...current,
        { id: crypto.randomUUID(), role: 'assistant', text: response.answer, response },
      ])
      onResponse(response)
      lastFailedMessage.current = null
    } catch (caught) {
      const message = caught instanceof ApiError ? caught.message : 'Ocorreu um erro inesperado.'
      setError(message)
      lastFailedMessage.current = normalized
    } finally {
      setLoading(false)
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    void submit(input)
  }

  return (
    <section className="chat-card" aria-labelledby="chat-title">
      <div className="chat-header">
        <div><span className="eyebrow">API local · dados sintéticos</span><h2 id="chat-title">Converse com o protótipo</h2></div>
        <span className="status-chip"><span className="status-dot" />LLM padrão: desligada</span>
      </div>

      <div className="example-strip" aria-label="Perguntas de exemplo">
        {exampleQuestions.map((example) => (
          <button key={example.label} type="button" onClick={() => void submit(example.text)} disabled={loading}>
            <span>{example.label}</span>{example.text}
          </button>
        ))}
      </div>

      <div className="message-list" aria-live="polite" aria-busy={loading}>
        {messages.map((message) => (
          <article className={`message ${message.role}`} key={message.id}>
            <div className="avatar" aria-hidden="true">{message.role === 'assistant' ? <SparkIcon /> : 'VC'}</div>
            <div>
              <span className="message-author">{message.role === 'assistant' ? 'SupportLab' : 'Você'}</span>
              <p>{message.text}</p>
              {message.response?.requires_human && (
                <div className="handoff"><HumanIcon /><span>Encaminhado para atendimento humano simulado</span></div>
              )}
            </div>
          </article>
        ))}
        {loading && (
          <div className="message assistant loading-message" role="status">
            <div className="avatar"><SparkIcon /></div>
            <div><span className="message-author">SupportLab</span><div className="typing"><span /><span /><span /></div></div>
          </div>
        )}
      </div>

      {error && (
        <div className="api-error" role="alert">
          <div><strong>API indisponível</strong><p>{error}</p></div>
          <button type="button" onClick={() => lastFailedMessage.current && void submit(lastFailedMessage.current)}>Tentar novamente</button>
        </div>
      )}

      <form className="composer" onSubmit={handleSubmit}>
        <label htmlFor="support-message">Mensagem para o suporte</label>
        <div className="composer-row">
          <textarea
            id="support-message"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault()
                if (canSend) void submit(input)
              }
            }}
            placeholder="Ex.: Meu cartão foi recusado..."
            rows={2}
            maxLength={2000}
          />
          <button className="send-button" type="submit" disabled={!canSend} aria-label="Enviar mensagem"><SendIcon /></button>
        </div>
        <small>Enter envia · Shift + Enter cria uma nova linha</small>
      </form>
    </section>
  )
}

