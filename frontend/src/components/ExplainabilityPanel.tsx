import type { SupportResponse } from '../types'
import { InfoIcon, ShieldIcon } from './Icons'

interface Props {
  response: SupportResponse | null
}

const routeLabels = {
  regra: 'Regra determinística',
  humano: 'Escalonamento humano',
  ml: 'Machine Learning',
  llm: 'LLM fundamentada',
}

export function ExplainabilityPanel({ response }: Props) {
  if (!response) {
    return (
      <aside className="explain-panel empty-panel" aria-label="Explicabilidade">
        <div className="panel-heading"><InfoIcon /><h2>Por que esta resposta?</h2></div>
        <p>Envie uma pergunta para visualizar a trilha de decisão da API.</p>
        <div className="empty-trace" aria-hidden="true"><span /><span /><span /></div>
      </aside>
    )
  }

  const { audit } = response
  const confidence = audit.ml_confidence === null ? null : `${(audit.ml_confidence * 100).toFixed(1)}%`
  const llmStatus = response.route === 'llm'
    ? `${audit.llm_provider ?? 'provedor'} · ${audit.llm_model ?? 'modelo não informado'}`
    : 'Não acionada — modo seguro ou rota anterior'

  return (
    <aside className="explain-panel" aria-label="Explicabilidade da última resposta">
      <div className="panel-heading"><InfoIcon /><h2>Trilha de decisão</h2></div>
      <div className="trace-grid">
        <TraceItem label="Intenção" value={response.intent} />
        <TraceItem label="Confiança ML" value={confidence ?? 'Não aplicável'} />
        <TraceItem label="Rota final" value={routeLabels[response.route]} accent />
        <TraceItem label="Tempo" value={`${audit.duration_ms.toFixed(2)} ms`} />
      </div>

      <div className="reason-block">
        <span className="field-label">Reason code</span>
        <code>{audit.reason_code}</code>
        {audit.ml_fallback_reason && <code className="secondary-code">{audit.ml_fallback_reason}</code>}
      </div>

      <div className="source-block">
        <span className="field-label">Fontes autorizadas</span>
        {audit.sources.length > 0 ? (
          <ul>
            {audit.sources.map((source) => (
              <li key={source.source_id}>
                <span>{source.source_id}</span>
                <small>{source.source_path} · score {source.score.toFixed(3)}</small>
              </li>
            ))}
          </ul>
        ) : audit.knowledge_source ? (
          <div className="source-line">{audit.knowledge_source}</div>
        ) : (
          <p className="muted">Nenhuma fonte relevante recuperada.</p>
        )}
      </div>

      <div className="llm-status">
        <ShieldIcon />
        <div><span className="field-label">LLM</span><p>{llmStatus}</p></div>
      </div>
      <p className="correlation">ID de correlação: {response.correlation_id}</p>
    </aside>
  )
}

function TraceItem({ label, value, accent = false }: { label: string; value: string; accent?: boolean }) {
  return <div className={accent ? 'trace-item accent' : 'trace-item'}><span>{label}</span><strong>{value}</strong></div>
}

