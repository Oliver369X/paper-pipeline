import { MissionNav } from '@/components/MissionNav'
import { Button } from '@/components/ui/button'
import { Card, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { apiGet, apiUrl } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Trans, useTranslation } from 'react-i18next'
import { Link, useParams, useSearchParams } from 'react-router-dom'

type LineEntry = {
  id: string
  source: 'sse' | 'run_log' | 'events_log'
  ts: string
  headline: string
  body: string
}

function formatBlock(rec: Record<string, unknown>): string {
  try {
    return JSON.stringify(rec, null, 2)
  } catch {
    return String(rec)
  }
}


export function LiveTerminalPage() {
  const { t } = useTranslation()
  const { id } = useParams<{ id: string }>()
  const [searchParams, setSearchParams] = useSearchParams()
  const initialRun = searchParams.get('run_id') ?? ''
  const [didAutoSse, setDidAutoSse] = useState(false)

  const [runIdInput, setRunIdInput] = useState(initialRun)
  const [sseActive, setSseActive] = useState(false)
  /** run_id fijado al pulsar Conectar (no cambia al editar el input). */
  const [sessionRunId, setSessionRunId] = useState<string | null>(null)
  const [lines, setLines] = useState<LineEntry[]>([])
  const [pollRunLog, setPollRunLog] = useState(true)
  const [pollEvents, setPollEvents] = useState(true)
  /** Pausa polling cuando la pestaña está en segundo plano (menos ruido en servidor y red). */
  const [tabVisible, setTabVisible] = useState(
    () => typeof document === 'undefined' || document.visibilityState === 'visible',
  )
  const [stickToBottom, setStickToBottom] = useState(true)
  const esRef = useRef<EventSource | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const runLogLenRef = useRef(0)
  const eventsLenRef = useRef(0)
  const lineSeq = useRef(0)

  const actorHeadline = useCallback(
    (rec: Record<string, unknown>): string => {
      const ev = String(rec.event ?? '')
      const step = String(rec.step ?? '')
      const dash = t('brain.dash')
      if (step.startsWith('perplexity:')) {
        return t('live.hlPerplexity', { rest: step.slice('perplexity:'.length) })
      }
      if (step.includes('notion')) return t('live.hlNotion', { step })
      if (step.includes('quality') || ev.includes('quality'))
        return t('live.hlQuality', { step: step || ev })
      if (step.includes('cursor') || ev.includes('cursor'))
        return t('live.hlCursor', { step: step || ev })
      if (ev === 'step_start' || ev === 'step_ok' || ev === 'step_skip' || ev === 'step_error') {
        return t('live.hlPipeline', { ev, step: step || dash })
      }
      if (ev === 'run_finished' || ev === 'run_error') return t('live.hlOrchestrator', { ev })
      if (ev === 'loop_finished' || ev === 'loop_error') return t('live.hlLoop', { ev })
      if (ev === 'stream_end') return t('live.hlSseEnd')
      if (ev === 'draft_snapshot') return t('live.hlDraft')
      const et = String(rec.event_type ?? rec.type ?? '')
      if (et) return t('live.hlEvent', { et })
      const mod = String(rec.module ?? '')
        .replace(/^paper_pipeline\./, '')
        .replace(/\.logger$/, '')
      if (mod) return t('live.hlModule', { mod, ev })
      return t('live.hlMessage', { ev: ev || t('live.fallbackMessage') })
    },
    [t],
  )

  useEffect(() => {
    if (didAutoSse) return
    if (searchParams.get('autoconnect') !== '1') return
    const r = searchParams.get('run_id')?.trim()
    if (!r || !id) return
    /* eslint-disable react-hooks/set-state-in-effect -- autoconectar SSE desde query (?autoconnect=1&run_id=) */
    setRunIdInput(r)
    setSessionRunId(r)
    setSseActive(true)
    setDidAutoSse(true)
    /* eslint-enable react-hooks/set-state-in-effect */
    setSearchParams((p) => {
      const n = new URLSearchParams(p)
      n.delete('autoconnect')
      return n
    })
  }, [id, searchParams, didAutoSse, setSearchParams])

  useEffect(() => {
    const onVis = () => setTabVisible(document.visibilityState === 'visible')
    document.addEventListener('visibilitychange', onVis)
    return () => document.removeEventListener('visibilitychange', onVis)
  }, [])

  const append = useCallback((source: LineEntry['source'], rec: Record<string, unknown>) => {
    const ts = String(rec.ts ?? new Date().toISOString())
    lineSeq.current += 1
    setLines((prev) => {
      const entry: LineEntry = {
        id: `${Date.now()}-${lineSeq.current}`,
        source,
        ts,
        headline: actorHeadline(rec),
        body: formatBlock(rec),
      }
      const next = [...prev, entry]
      return next.length > 2000 ? next.slice(-1500) : next
    })
  }, [actorHeadline])

  // --- SSE: mismo canal que Pipeline / Loop ---
  useEffect(() => {
    if (!id || !sessionRunId || !sseActive) {
      if (esRef.current) {
        esRef.current.close()
        esRef.current = null
      }
      return
    }
    const rid = sessionRunId
    const url = apiUrl(`/api/missions/${id}/events/${rid}`)
    const es = new EventSource(url)
    esRef.current = es
    append('sse', {
      event: 'client_connect',
      ts: new Date().toISOString(),
      detail: t('live.eventSourceDetail', { url }),
    })
    es.onmessage = (msg) => {
      try {
        const parsed = JSON.parse(msg.data) as Record<string, unknown>
        append('sse', parsed)
        if (parsed.event === 'stream_end') {
          es.close()
          esRef.current = null
          setSseActive(false)
          setSessionRunId(null)
        }
      } catch {
        append('sse', { event: 'parse_error', raw: msg.data, ts: new Date().toISOString() })
      }
    }
    es.onerror = () => {
      append('sse', {
        event: 'sse_transport_error',
        ts: new Date().toISOString(),
        detail: t('live.sseTransportError'),
      })
      es.close()
      esRef.current = null
      setSseActive(false)
      setSessionRunId(null)
    }
    return () => {
      es.close()
      esRef.current = null
    }
  }, [id, sessionRunId, sseActive, append, t])

  const pollRunMs = 4000
  const pollEventsMs = 5000

  const runLog = useQuery({
    queryKey: ['run-log', id],
    queryFn: () => apiGet<Record<string, unknown>[]>(`/api/missions/${id}/run-log`),
    enabled: Boolean(id) && pollRunLog,
    refetchInterval: tabVisible && pollRunLog ? pollRunMs : false,
  })

  const eventsLog = useQuery({
    queryKey: ['events-log', id],
    queryFn: () => apiGet<Record<string, unknown>[]>(`/api/missions/${id}/events-log`),
    enabled: Boolean(id) && pollEvents,
    refetchInterval: tabVisible && pollEvents ? pollEventsMs : false,
  })

  useEffect(() => {
    const rows = runLog.data
    if (!rows || !pollRunLog) return
    if (rows.length <= runLogLenRef.current) {
      if (rows.length < runLogLenRef.current) runLogLenRef.current = 0
      return
    }
    for (let i = runLogLenRef.current; i < rows.length; i += 1) {
      append('run_log', rows[i] ?? {})
    }
    runLogLenRef.current = rows.length
  }, [runLog.data, pollRunLog, append])

  useEffect(() => {
    const rows = eventsLog.data
    if (!rows || !pollEvents) return
    if (rows.length <= eventsLenRef.current) {
      if (rows.length < eventsLenRef.current) eventsLenRef.current = 0
      return
    }
    for (let i = eventsLenRef.current; i < rows.length; i += 1) {
      append('events_log', rows[i] ?? {})
    }
    eventsLenRef.current = rows.length
  }, [eventsLog.data, pollEvents, append])

  useEffect(() => {
    if (stickToBottom && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [lines, stickToBottom])

  const copyAll = useCallback(() => {
    const text = lines.map((l) => `--- ${l.source} ${l.ts}\n${l.headline}\n${l.body}\n`).join('\n')
    void navigator.clipboard.writeText(text)
  }, [lines])

  const clear = useCallback(() => {
    setLines([])
    // No reinyectar todo el historial en el siguiente poll
    runLogLenRef.current = runLog.data?.length ?? runLogLenRef.current
    eventsLenRef.current = eventsLog.data?.length ?? eventsLenRef.current
    lineSeq.current = 0
  }, [runLog.data?.length, eventsLog.data?.length])

  const stats = useMemo(() => {
    const c = { sse: 0, run_log: 0, events_log: 0 }
    for (const l of lines) c[l.source] += 1
    return c
  }, [lines])

  if (!id) return <p className="p-6 text-zinc-500">{t('common.missingId')}</p>

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <MissionNav missionId={id} />

      <Card className="mb-4 border-zinc-700 bg-zinc-950">
        <CardTitle className="text-lg">{t('live.title')}</CardTitle>
        <p className="mb-3 text-sm text-zinc-400">
          <Trans
            i18nKey="live.blurb"
            components={{
              strong: <strong className="text-zinc-300" />,
            }}
          />
        </p>

        <div className="flex flex-wrap gap-3 border-b border-zinc-800 pb-4">
          <div className="min-w-[200px] flex-1">
            <Label htmlFor="rid">{t('live.runIdLabel')}</Label>
            <Input
              id="rid"
              className="mt-1 font-mono text-sm"
              placeholder={t('live.runIdPlaceholder')}
              value={runIdInput}
              onChange={(e) => setRunIdInput(e.target.value)}
            />
          </div>
          <div className="flex flex-wrap items-end gap-2">
            <Button
              type="button"
              variant={sseActive ? 'default' : 'outline'}
              onClick={() => {
                if (sseActive) {
                  setSseActive(false)
                  setSessionRunId(null)
                  return
                }
                const rid = runIdInput.trim()
                if (!rid) return
                setSearchParams((p) => {
                  const n = new URLSearchParams(p)
                  n.set('run_id', rid)
                  return n
                })
                setSessionRunId(rid)
                setSseActive(true)
              }}
              disabled={!runIdInput.trim() && !sseActive}
            >
              {sseActive ? t('live.disconnectSse') : t('live.connectSse')}
            </Button>
            <label className="flex items-center gap-2 text-sm text-zinc-400">
              <input
                type="checkbox"
                checked={pollRunLog}
                onChange={(e) => setPollRunLog(e.target.checked)}
              />
              {t('live.pollRun', {
                sec: pollRunMs / 1000,
                paused: !tabVisible ? t('live.pausedHidden') : '',
              })}
            </label>
            <label className="flex items-center gap-2 text-sm text-zinc-400">
              <input
                type="checkbox"
                checked={pollEvents}
                onChange={(e) => setPollEvents(e.target.checked)}
              />
              {t('live.pollEvents', {
                sec: pollEventsMs / 1000,
                paused: !tabVisible ? t('live.pausedHidden') : '',
              })}
            </label>
            <label className="flex items-center gap-2 text-sm text-zinc-400">
              <input
                type="checkbox"
                checked={stickToBottom}
                onChange={(e) => setStickToBottom(e.target.checked)}
              />
              {t('live.autoScroll')}
            </label>
          </div>
        </div>

        <div className="mt-3 flex flex-wrap gap-2 text-xs text-zinc-500">
          <span>
            {t('live.linesStats', {
              n: lines.length,
              sse: stats.sse,
              run: stats.run_log,
              ev: stats.events_log,
            })}
          </span>
          <Button type="button" variant="ghost" className="h-7 text-xs" onClick={copyAll}>
            {t('live.copyAll')}
          </Button>
          <Button type="button" variant="ghost" className="h-7 text-xs" onClick={clear}>
            {t('live.clearView')}
          </Button>
          <Link to={`/missions/${id}/run`} className="text-violet-400 hover:underline">
            {t('live.goPipeline')}
          </Link>
          <Link to={`/missions/${id}/loop`} className="text-violet-400 hover:underline">
            {t('live.goLoop')}
          </Link>
        </div>
      </Card>

      <pre
        className="max-h-[min(70vh,720px)] overflow-auto rounded-md border border-zinc-800 bg-black p-3 font-mono text-[11px] leading-relaxed text-zinc-100"
        style={{ tabSize: 2 }}
      >
        {lines.length === 0 && (
          <span className="text-zinc-600">{t('live.emptyHint')}</span>
        )}
        {lines.map((l) => (
          <div key={l.id} className="mb-4 border-b border-zinc-900 pb-3 last:border-0">
            <div className="text-zinc-500">
              <span
                className={
                  l.source === 'sse'
                    ? 'text-cyan-400'
                    : l.source === 'run_log'
                      ? 'text-amber-400'
                      : 'text-green-400'
                }
              >
                [{l.source}]
              </span>{' '}
              <span className="text-zinc-600">{l.ts}</span>
            </div>
            <div className="text-zinc-300">{l.headline}</div>
            <div className="mt-1 whitespace-pre-wrap break-words text-zinc-400">{l.body}</div>
          </div>
        ))}
        <div ref={bottomRef} />
      </pre>
    </div>
  )
}
