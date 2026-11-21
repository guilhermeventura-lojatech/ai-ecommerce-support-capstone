import { confusionMatrix, intentLabels, routingComparison, testMetrics } from '../data/academicResults'
import { ChartIcon, ShieldIcon } from './Icons'

const percentage = (value: number) => `${(value * 100).toFixed(1)}%`

export function AcademicDashboard() {
  return (
    <section className="dashboard-section" id="evidencias" aria-labelledby="dashboard-title">
      <div className="section-heading">
        <div><span className="eyebrow">Evidências reproduzíveis</span><h2 id="dashboard-title">Resultados do baseline experimental</h2></div>
        <div className="synthetic-badge"><ShieldIcon />Dados 100% sintéticos</div>
      </div>

      <div className="metrics-grid">
        <Metric label="Accuracy de teste" value={percentage(testMetrics.accuracy)} detail={`${testMetrics.correct} acertos em ${testMetrics.sampleCount}`} />
        <Metric label="Macro F1" value={testMetrics.macroF1.toFixed(3)} detail="Meta futura 0,80 — não atingida" />
        <Metric label="Precision macro" value={testMetrics.macroPrecision.toFixed(3)} detail="Teste sintético estratificado" />
        <Metric label="Recall macro" value={testMetrics.macroRecall.toFixed(3)} detail="Cinco classes balanceadas" />
      </div>

      <div className="evidence-grid">
        <article className="matrix-card">
          <div className="card-title"><div><span>Matriz de confusão</span><h3>13 acertos em 19 casos</h3></div><ChartIcon /></div>
          <div className="matrix-scroll">
            <table>
              <caption>Linhas: classe real. Colunas: classe predita.</caption>
              <thead><tr><th scope="col">Real \ Predita</th>{intentLabels.map((label) => <th scope="col" key={label}>{label}</th>)}</tr></thead>
              <tbody>
                {confusionMatrix.map((row, rowIndex) => (
                  <tr key={intentLabels[rowIndex]}>
                    <th scope="row">{intentLabels[rowIndex]}</th>
                    {row.map((cell, columnIndex) => <td className={rowIndex === columnIndex ? 'diagonal' : cell > 0 ? 'error-cell' : ''} key={`${rowIndex}-${columnIndex}`}>{cell}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>

        <article className="comparison-card">
          <div className="card-title"><div><span>Comparação preliminar</span><h3>Segurança versus cobertura</h3></div><ShieldIcon /></div>
          <div className="comparison-list">
            {routingComparison.map((item) => (
              <div className="comparison-row" key={item.label}>
                <div className="comparison-label"><strong>{item.label}</strong>{!item.safe && <span>Somente diagnóstico</span>}<small>{item.correct} acertos</small></div>
                <div className="bar-group">
                  <Bar label="Accuracy" value={item.accuracy} unsafe={!item.safe} />
                  <Bar label="Cobertura" value={item.coverage} unsafe={!item.safe} />
                </div>
              </div>
            ))}
          </div>
          <p className="diagnostic-warning">O ML bruto ignora thresholds de segurança e não representa a política da API. Com os thresholds, o ML não aumentou a cobertura segura neste teste.</p>
        </article>
      </div>
    </section>
  )
}

function Metric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return <article className="metric-card"><span>{label}</span><strong>{value}</strong><p>{detail}</p></article>
}

function Bar({ label, value, unsafe }: { label: string; value: number; unsafe: boolean }) {
  return <div className="bar"><div><span>{label}</span><strong>{percentage(value)}</strong></div><div className="bar-track"><span className={unsafe ? 'unsafe' : ''} style={{ width: percentage(value) }} /></div></div>
}

