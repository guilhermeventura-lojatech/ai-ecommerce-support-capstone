export type Intent =
  | 'entrega'
  | 'troca'
  | 'reembolso'
  | 'pagamento'
  | 'cancelamento'
  | 'desconhecida'

export type Route = 'regra' | 'humano' | 'ml' | 'llm'

export interface SourceReference {
  source_id: string
  source_path: string
  score: number
}

export interface AuditRecord {
  correlation_id: string
  route: Route
  reason_code: string
  duration_ms: number
  rule_id: string | null
  knowledge_source: string | null
  model_version: string | null
  ml_confidence: number | null
  ml_known_token_ratio: number | null
  ml_fallback_reason: string | null
  sources: SourceReference[]
  llm_provider: string | null
  llm_model: string | null
  llm_prompt_tokens: number | null
  llm_completion_tokens: number | null
  llm_total_tokens: number | null
  llm_estimated_cost_usd: number | null
  safety_result: string | null
}

export interface SupportResponse {
  correlation_id: string
  route: Route
  intent: Intent
  answer: string
  requires_human: boolean
  audit: AuditRecord
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  text: string
  response?: SupportResponse
}

