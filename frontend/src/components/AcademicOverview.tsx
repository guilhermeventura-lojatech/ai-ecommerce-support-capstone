import { BookIcon, ShieldIcon, SparkIcon } from './Icons'

export function AcademicOverview() {
  return (
    <section className="overview-section" id="estudo" aria-labelledby="overview-title">
      <div className="section-heading"><div><span className="eyebrow">Leitura do caso</span><h2 id="overview-title">Da pressão operacional à arquitetura controlada</h2></div></div>
      <div className="problem-band">
        <div><span>Contexto acadêmico fornecido</span><strong>25 mil</strong><p>solicitações mensais</p></div>
        <div><span>Baseline fornecido</span><strong>9 horas</strong><p>de tempo médio de resposta</p></div>
        <div className="problem-copy"><h3>O problema</h3><p>Reduzir tempo e custo sem perder qualidade, confiança ou rastreabilidade. Não há dados reais de CSAT, economia ou taxa de resolução neste estudo.</p></div>
      </div>

      <div className="architecture-card">
        <div className="card-title"><div><span>Arquitetura</span><h3>Automação em camadas, humano como garantia</h3></div><SparkIcon /></div>
        <div className="architecture-flow" aria-label="Fluxo da arquitetura">
          {['Mensagem', 'Regras', 'ML', 'Recuperação', 'LLM opcional', 'Humano'].map((step, index) => (
            <div className={step === 'Humano' ? 'flow-step human-step' : 'flow-step'} key={step}><span>{index + 1}</span><strong>{step}</strong></div>
          ))}
        </div>
        <p>A precedência é conservadora: regras resolvem o que está autorizado; ML apenas classifica; recuperação limita o contexto; LLM fica desligada por padrão; exceções escalam.</p>
      </div>

      <div className="overview-grid">
        <article>
          <div className="mini-heading"><BookIcon /><h3>Alternativas avaliadas</h3></div>
          <ul className="clean-list"><li><strong>Regras:</strong> previsíveis e auditáveis, mas frágeis à variação.</li><li><strong>ML:</strong> amplia o roteamento, mas depende de rótulos e calibração.</li><li><strong>LLM:</strong> flexível em linguagem, porém exige fontes, limites e governança.</li></ul>
        </article>
        <article>
          <div className="mini-heading"><ShieldIcon /><h3>Cinco critérios de decisão</h3></div>
          <ol className="criteria-list"><li>Previsibilidade</li><li>Necessidade semântica</li><li>Complexidade proporcional</li><li>Volume e qualidade dos dados</li><li>Explicabilidade e auditoria</li></ol>
        </article>
        <article>
          <div className="mini-heading"><ShieldIcon /><h3>Riscos centrais</h3></div>
          <ul className="risk-list"><li><span>Alto</span>Alucinação e política incorreta</li><li><span>Alto</span>Privacidade e LGPD</li><li><span>Médio</span>Prompt injection e abuso</li><li><span>Médio</span>Custo variável de API</li></ul>
        </article>
      </div>

      <div className="conclusion-card"><span>Conclusão acadêmica</span><p>A evidência atual sustenta uma prova de conceito rastreável, não uma implantação. O baseline de ML ficou abaixo da meta futura, a LLM real não foi avaliada e qualquer avanço depende de políticas oficiais, dados representativos e avaliação humana.</p></div>
    </section>
  )
}

