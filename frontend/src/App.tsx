import { useState } from 'react'
import type { SupportResponse } from './types'
import { AcademicDashboard } from './components/AcademicDashboard'
import { AcademicOverview } from './components/AcademicOverview'
import { ChatWorkspace } from './components/ChatWorkspace'
import { ExplainabilityPanel } from './components/ExplainabilityPanel'
import { SparkIcon } from './components/Icons'
import './styles.css'

export default function App() {
  const [latestResponse, setLatestResponse] = useState<SupportResponse | null>(null)

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#inicio" aria-label="SupportLab, início"><span><SparkIcon /></span><div><strong>SupportLab</strong><small>Micro-capstone de IA</small></div></a>
        <nav aria-label="Navegação principal"><a href="#demo">Demonstração</a><a href="#evidencias">Evidências</a><a href="#estudo">Estudo</a></nav>
        <span className="prototype-pill">Protótipo acadêmico</span>
      </header>

      <main id="inicio">
        <section className="hero">
          <div className="hero-copy"><span className="eyebrow">IA híbrida · explicável · local</span><h1>Atendimento inteligente, com limites visíveis.</h1><p>Uma experiência demonstrativa que combina regras determinísticas, classificação de intenção, recuperação autorizada e escalonamento humano.</p><div className="hero-notice"><span>Dados sintéticos</span><span>Sem sistemas reais</span><span>LLM desligada por padrão</span></div></div>
          <div className="hero-orbit" aria-hidden="true"><div className="orbit-center"><SparkIcon /><span>decisão</span></div><span className="orbit-tag tag-one">regras</span><span className="orbit-tag tag-two">ML</span><span className="orbit-tag tag-three">fontes</span><span className="orbit-ring" /></div>
        </section>

        <section className="demo-section" id="demo" aria-label="Demonstração do atendimento">
          <ChatWorkspace onResponse={setLatestResponse} />
          <ExplainabilityPanel response={latestResponse} />
        </section>

        <AcademicDashboard />
        <AcademicOverview />
      </main>

      <footer><div className="brand footer-brand"><span><SparkIcon /></span><div><strong>SupportLab</strong><small>Arquitetura experimental, não produção</small></div></div><p>Sem métricas de produção, dados pessoais ou chamadas externas por padrão.</p></footer>
    </div>
  )
}

