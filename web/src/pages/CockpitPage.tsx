import { apiUrl } from '@/lib/api'
import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useParams } from 'react-router-dom'

type Json = Record<string, unknown> | unknown[] | null

async function fetchJson(url: string): Promise<Json> {
  const r = await fetch(url)
  if (r.status === 404) return null
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`)
  return r.json() as Promise<Json>
}

export function CockpitPage() {
  const { t } = useTranslation()
  const { id } = useParams<{ id: string }>()
  const [ledger, setLedger] = useState<unknown>(null)
  const [evidence, setEvidence] = useState<unknown>(null)
  const [publish, setPublish] = useState<Json>(null)
  const [triage, setTriage] = useState<Json>(null)
  const [loopStop, setLoopStop] = useState<Json>(null)
  const [metricsVal, setMetricsVal] = useState<Json>(null)
  const [safety, setSafety] = useState<Json>(null)
  const [objective, setObjective] = useState<Json>(null)
  const [memoryLatest, setMemoryLatest] = useState<Json>(null)
  const [memoryIndex, setMemoryIndex] = useState<Json>(null)
  const [goalSelection, setGoalSelection] = useState<Json>(null)
  const [goalsDoc, setGoalsDoc] = useState<Json>(null)
  const [workingMem, setWorkingMem] = useState<Json>(null)
  const [hypotheses, setHypotheses] = useState<Json>(null)
  const [agentDecision, setAgentDecision] = useState<Json>(null)
  const [perplexityCall, setPerplexityCall] = useState<Json>(null)
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    const base = apiUrl(`/api/missions/${id}`)
    void Promise.all([fetchJson(`${base}/ledger/latest`), fetchJson(`${base}/evidence/latest`)]).then(
      ([l, e]) => {
        setLedger(l)
        setEvidence(e)
        setErr(null)
      },
      (e) => setErr(String(e)),
    )

    void Promise.all([
      fetchJson(`${base}/publish/decision`),
      fetchJson(`${base}/triage/latest`),
      fetchJson(`${base}/loop/stop`),
      fetchJson(`${base}/metrics/validated`),
      fetchJson(`${base}/safety/latest`),
      fetchJson(`${base}/objective/latest`),
      fetchJson(`${base}/memory/latest`),
      fetchJson(`${base}/memory/index`),
      fetchJson(`${base}/goal-selection/latest`),
      fetchJson(`${base}/goals/latest`),
      fetchJson(`${base}/working-memory/latest`),
      fetchJson(`${base}/hypotheses/latest`),
      fetchJson(`${base}/agent/decisions/latest`),
      fetchJson(`${base}/perplexity/calls/latest`),
    ]).then(
      ([pub, tri, stop, met, safe, obj, memLatest, memIndex, goalSel, goals, wm, hyp, agDec, pplx]) => {
        setPublish(pub)
        setTriage(tri)
        setLoopStop(stop)
        setMetricsVal(met)
        setSafety(safe)
        setObjective(obj)
        setMemoryLatest(memLatest)
        setMemoryIndex(memIndex)
        setGoalSelection(goalSel)
        setGoalsDoc(goals)
        setWorkingMem(wm)
        setHypotheses(hyp)
        setAgentDecision(agDec)
        setPerplexityCall(pplx)
      },
    )
  }, [id])

  const dash = '—'

  return (
    <div className="mx-auto max-w-4xl space-y-4 p-6">
      <div className="flex items-center justify-between gap-2">
        <h1 className="text-xl font-semibold">{t('cockpit.title', { id })}</h1>
        <Link className="text-sm underline" to="/">
          {t('cockpit.home')}
        </Link>
      </div>
      {err && <p className="text-sm text-amber-700">{t('cockpit.err', { err })}</p>}
      <section>
        <h2 className="font-medium">{t('cockpit.ledger')}</h2>
        <pre className="mt-1 max-h-64 overflow-auto rounded border bg-zinc-950 p-2 text-xs text-zinc-100">
          {ledger ? JSON.stringify(ledger, null, 2) : dash}
        </pre>
      </section>
      <section>
        <h2 className="font-medium">{t('cockpit.evidence')}</h2>
        <pre className="mt-1 max-h-64 overflow-auto rounded border bg-zinc-950 p-2 text-xs text-zinc-100">
          {evidence ? JSON.stringify(evidence, null, 2) : dash}
        </pre>
      </section>
      <details className="rounded border border-zinc-700 bg-zinc-900/40 p-3 open:pb-4">
        <summary className="cursor-pointer font-medium text-zinc-200">{t('cockpit.publish')}</summary>
        <pre className="mt-2 max-h-48 overflow-auto rounded border bg-zinc-950 p-2 text-xs text-zinc-100">
          {publish ? JSON.stringify(publish, null, 2) : t('cockpit.missingPublish')}
        </pre>
      </details>
      <details className="rounded border border-zinc-700 bg-zinc-900/40 p-3 open:pb-4">
        <summary className="cursor-pointer font-medium text-zinc-200">{t('cockpit.triage')}</summary>
        <pre className="mt-2 max-h-48 overflow-auto rounded border bg-zinc-950 p-2 text-xs text-zinc-100">
          {triage ? JSON.stringify(triage, null, 2) : t('cockpit.missingTriage')}
        </pre>
      </details>
      <details className="rounded border border-zinc-700 bg-zinc-900/40 p-3 open:pb-4">
        <summary className="cursor-pointer font-medium text-zinc-200">{t('cockpit.loopStop')}</summary>
        <pre className="mt-2 max-h-48 overflow-auto rounded border bg-zinc-950 p-2 text-xs text-zinc-100">
          {loopStop ? JSON.stringify(loopStop, null, 2) : t('cockpit.missingStop')}
        </pre>
      </details>
      <details className="rounded border border-zinc-700 bg-zinc-900/40 p-3 open:pb-4">
        <summary className="cursor-pointer font-medium text-zinc-200">{t('cockpit.metrics')}</summary>
        <pre className="mt-2 max-h-48 overflow-auto rounded border bg-zinc-950 p-2 text-xs text-zinc-100">
          {metricsVal ? JSON.stringify(metricsVal, null, 2) : t('cockpit.missingMetrics')}
        </pre>
      </details>
      <details className="rounded border border-zinc-700 bg-zinc-900/40 p-3 open:pb-4">
        <summary className="cursor-pointer font-medium text-zinc-200">{t('cockpit.safety')}</summary>
        <pre className="mt-2 max-h-48 overflow-auto rounded border bg-zinc-950 p-2 text-xs text-zinc-100">
          {safety ? JSON.stringify(safety, null, 2) : t('cockpit.missingSafety')}
        </pre>
      </details>
      <details className="rounded border border-zinc-700 bg-zinc-900/40 p-3 open:pb-4">
        <summary className="cursor-pointer font-medium text-zinc-200">{t('cockpit.objective')}</summary>
        <pre className="mt-2 max-h-48 overflow-auto rounded border bg-zinc-950 p-2 text-xs text-zinc-100">
          {objective ? JSON.stringify(objective, null, 2) : t('cockpit.missingObjective')}
        </pre>
      </details>
      <details className="rounded border border-zinc-700 bg-zinc-900/40 p-3 open:pb-4">
        <summary className="cursor-pointer font-medium text-zinc-200">{t('cockpit.memory')}</summary>
        <pre className="mt-2 max-h-48 overflow-auto rounded border bg-zinc-950 p-2 text-xs text-zinc-100">
          {memoryLatest || memoryIndex
            ? JSON.stringify({ latest: memoryLatest, index: memoryIndex }, null, 2)
            : t('cockpit.missingMemory')}
        </pre>
      </details>
      <details className="rounded border border-zinc-700 bg-zinc-900/40 p-3 open:pb-4">
        <summary className="cursor-pointer font-medium text-zinc-200">{t('cockpit.goalSelection')}</summary>
        <pre className="mt-2 max-h-48 overflow-auto rounded border bg-zinc-950 p-2 text-xs text-zinc-100">
          {goalSelection ? JSON.stringify(goalSelection, null, 2) : t('cockpit.missingGoalSel')}
        </pre>
      </details>
      <details className="rounded border border-zinc-700 bg-zinc-900/40 p-3 open:pb-4">
        <summary className="cursor-pointer font-medium text-zinc-200">{t('cockpit.goalsTree')}</summary>
        <pre className="mt-2 max-h-48 overflow-auto rounded border bg-zinc-950 p-2 text-xs text-zinc-100">
          {goalsDoc ? JSON.stringify(goalsDoc, null, 2) : t('cockpit.missingGoals')}
        </pre>
      </details>
      <details className="rounded border border-zinc-700 bg-zinc-900/40 p-3 open:pb-4">
        <summary className="cursor-pointer font-medium text-zinc-200">{t('cockpit.workingMemory')}</summary>
        <pre className="mt-2 max-h-48 overflow-auto rounded border bg-zinc-950 p-2 text-xs text-zinc-100">
          {workingMem ? JSON.stringify(workingMem, null, 2) : t('cockpit.missingWM')}
        </pre>
      </details>
      <details className="rounded border border-zinc-700 bg-zinc-900/40 p-3 open:pb-4">
        <summary className="cursor-pointer font-medium text-zinc-200">{t('cockpit.hypotheses')}</summary>
        <pre className="mt-2 max-h-48 overflow-auto rounded border bg-zinc-950 p-2 text-xs text-zinc-100">
          {hypotheses ? JSON.stringify(hypotheses, null, 2) : t('cockpit.missingHyp')}
        </pre>
      </details>
      <details className="rounded border border-zinc-700 bg-zinc-900/40 p-3 open:pb-4">
        <summary className="cursor-pointer font-medium text-zinc-200">{t('cockpit.agentStep')}</summary>
        <pre className="mt-2 max-h-48 overflow-auto rounded border bg-zinc-950 p-2 text-xs text-zinc-100">
          {agentDecision ? JSON.stringify(agentDecision, null, 2) : t('cockpit.missingAgent')}
        </pre>
      </details>
      <details className="rounded border border-zinc-700 bg-zinc-900/40 p-3 open:pb-4">
        <summary className="cursor-pointer font-medium text-zinc-200">{t('cockpit.perplexityLast')}</summary>
        <pre className="mt-2 max-h-48 overflow-auto rounded border bg-zinc-950 p-2 text-xs text-zinc-100">
          {perplexityCall ? JSON.stringify(perplexityCall, null, 2) : t('cockpit.missingPplx')}
        </pre>
      </details>
    </div>
  )
}
