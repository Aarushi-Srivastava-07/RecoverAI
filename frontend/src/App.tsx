import { Activity, ArrowUpRight, ShieldCheck } from 'lucide-react'
import { useEffect, useState } from 'react'

type Health = { status: string; service: string; environment: string }

export function PhaseOneApp() {
  const [health, setHealth] = useState<Health | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    fetch('/api/health')
      .then((response) => { if (!response.ok) throw new Error('Health check failed'); return response.json() as Promise<Health> })
      .then(setHealth).catch(() => setError(true))
  }, [])

  const connectionText = health
    ? `${health.service} is online (${health.environment}).`
    : error ? 'Backend unavailable. Start the API on port 8000.' : 'Checking the API health endpoint…'

  return <main className="min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-300 selection:text-slate-950">
    <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-8 sm:px-10">
      <nav className="flex items-center justify-between"><div className="flex items-center gap-3 font-semibold tracking-tight"><span className="grid size-9 place-items-center rounded-xl bg-cyan-300 text-slate-950"><Activity size={19} /></span>RecoverAI</div><span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-medium text-slate-300">Test mode foundation</span></nav>
      <section className="flex flex-1 items-center py-20"><div className="max-w-3xl"><p className="mb-5 text-sm font-semibold uppercase tracking-[0.2em] text-cyan-300">AI revenue recovery</p><h1 className="text-5xl font-semibold leading-[1.04] tracking-tight sm:text-7xl">A safer way to recover failed subscription revenue.</h1><p className="mt-7 max-w-2xl text-lg leading-8 text-slate-400">RecoverAI will pair recovery intelligence with deterministic controls, so every intervention remains transparent, bounded, and auditable.</p>
      <div className="mt-10 grid gap-4 sm:grid-cols-2"><div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5"><ShieldCheck className="mb-4 text-cyan-300" size={23} /><p className="font-medium">Safety-first by design</p><p className="mt-1 text-sm leading-6 text-slate-400">Recommendations will always pass through deterministic backend policy controls.</p></div><div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5"><ArrowUpRight className="mb-4 text-cyan-300" size={23} /><p className="font-medium">Backend connection</p><p className="mt-1 text-sm leading-6 text-slate-400">{connectionText}</p></div></div></div></section>
    </div>
  </main>
}

type Decision = { customer_id: string; recovery_probability: number; diagnosis: string; recommended_action: string; expected_recovery: number; reason: string; requires_human: boolean; policy_check: string; execution: { status: string } }
type Analytics = { revenue_at_risk:number; recovered_revenue:number; recovery_rate:number; total_failed_payments:number; pending_actions:number; escalations:number; baseline_recovered_revenue:number; recoverai_recovered_revenue:number; improvement_percentage:number }
type Recovery = { id:string; customer_id:string; amount:number; failure_reason:string; recovery_probability:number; action:string }
type Audit = { id:string; event:string; result:string; customer_id:string; detail:string }
const money = (value = 0) => `₹${Math.round(value).toLocaleString('en-IN')}`

export default function App() {
  const [scenario, setScenario] = useState('transient_failure')
  const [decision, setDecision] = useState<Decision | null>(null)
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [recoveries, setRecoveries] = useState<Recovery[]>([])
  const [audit, setAudit] = useState<Audit[]>([])
  const [loading, setLoading] = useState(false)
  const refresh = () => Promise.all(['/api/analytics', '/api/recoveries', '/api/audit'].map((url) => fetch(url).then((response) => response.json()))).then(([a, r, l]) => { setAnalytics(a); setRecoveries(r); setAudit(l) })
  useEffect(() => { refresh().catch(() => undefined) }, [])
  async function simulate() { setLoading(true); try { const response = await fetch(`/api/demo/simulate?scenario=${scenario}`, { method: 'POST' }); setDecision(await response.json()); await refresh() } finally { setLoading(false) } }
  return <main className="min-h-screen bg-slate-950 text-slate-100"><div className="mx-auto max-w-7xl px-6 py-8">
    <header className="flex flex-col justify-between gap-4 border-b border-slate-800 pb-6 sm:flex-row sm:items-center"><div><h1 className="text-2xl font-semibold text-cyan-300">RecoverAI</h1><p className="text-sm text-slate-400">Revenue recovery command center · DEMO / SIMULATION MODE</p></div><div className="flex gap-2"><select value={scenario} onChange={(event) => setScenario(event.target.value)} className="rounded-lg border border-slate-700 bg-slate-900 px-3 text-sm"><option value="transient_failure">Transient failure</option><option value="payment_method_issue">Payment method issue</option><option value="repeated_failure">Repeated failure</option><option value="high_value_customer">High-value customer</option><option value="max_attempts">Max attempts STOP</option></select><button onClick={simulate} disabled={loading} className="rounded-lg bg-cyan-300 px-4 py-2 text-sm font-semibold text-slate-950">{loading ? 'Simulating…' : 'Simulate Revenue Incident'}</button></div></header>
    <section className="grid grid-cols-2 gap-3 py-7 md:grid-cols-6">{[['Revenue at Risk', money(analytics?.revenue_at_risk)], ['Recovered', money(analytics?.recovered_revenue)], ['Recovery Rate', `${analytics?.recovery_rate ?? 0}%`], ['Failed', analytics?.total_failed_payments ?? 0], ['Pending', analytics?.pending_actions ?? 0], ['Escalations', analytics?.escalations ?? 0]].map(([name, value]) => <div key={String(name)} className="rounded-xl border border-slate-800 bg-slate-900 p-4"><p className="text-xs text-slate-400">{name}</p><p className="mt-2 text-xl font-semibold">{value}</p></div>)}</section>
    {decision && <section className="mb-6 rounded-xl border border-cyan-400/30 bg-cyan-400/5 p-5"><p className="text-xs font-semibold text-cyan-300">LATEST ML + POLICY DECISION</p><h2 className="mt-2 text-2xl font-semibold">{decision.recommended_action} · {decision.execution.status}</h2><p className="mt-2">{decision.diagnosis}</p><p className="mt-1 text-sm text-slate-400">{decision.reason}</p><div className="mt-4 grid grid-cols-2 gap-3 text-sm md:grid-cols-4"><span>Probability: <b>{(decision.recovery_probability * 100).toFixed(1)}%</b></span><span>Expected: <b>{money(decision.expected_recovery)}</b></span><span>Policy: <b>{decision.policy_check}</b></span><span>Human: <b>{decision.requires_human ? 'Required' : 'No'}</b></span></div></section>}
    <section className="grid gap-6 lg:grid-cols-2"><div className="rounded-xl border border-slate-800 bg-slate-900 p-5"><h2 className="font-semibold">Recovery Queue</h2><div className="mt-4 overflow-auto"><table className="w-full text-left text-sm"><thead className="text-slate-400"><tr><th>Customer</th><th>Amount</th><th>Failure</th><th>Probability</th><th>Action</th></tr></thead><tbody>{recoveries.map((item) => <tr className="border-t border-slate-800" key={item.id}><td className="py-3">{item.customer_id}</td><td>{money(item.amount)}</td><td>{item.failure_reason}</td><td>{(item.recovery_probability * 100).toFixed(0)}%</td><td className="text-cyan-300">{item.action}</td></tr>)}</tbody></table></div></div><div className="space-y-6"><div className="rounded-xl border border-slate-800 bg-slate-900 p-5"><h2 className="font-semibold">Baseline vs RecoverAI</h2><p className="mt-4 text-sm text-slate-400">Always retry: <b className="float-right text-slate-100">{money(analytics?.baseline_recovered_revenue)}</b></p><p className="mt-3 text-sm text-slate-400">RecoverAI: <b className="float-right text-cyan-300">{money(analytics?.recoverai_recovered_revenue)}</b></p><p className="mt-3 text-sm text-slate-400">Improvement: <b className="float-right text-slate-100">{analytics?.improvement_percentage ?? 0}%</b></p></div><div className="rounded-xl border border-slate-800 bg-slate-900 p-5"><h2 className="font-semibold">Audit Trail</h2>{audit.slice(0, 8).map((item) => <div className="mt-3 border-l border-cyan-400/60 pl-3 text-xs" key={item.id}><p>{item.event} <span className="text-cyan-300">{item.result}</span></p><p className="text-slate-500">{item.customer_id} · {item.detail}</p></div>)}</div></div></section>
  </div></main>
}
