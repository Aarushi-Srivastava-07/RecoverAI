import { Activity, ArrowUpRight, ShieldCheck } from 'lucide-react'
import { useEffect, useState } from 'react'

type Health = { status: string; service: string; environment: string }

export default function App() {
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
