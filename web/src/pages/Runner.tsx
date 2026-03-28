import { MissionNav } from '@/components/MissionNav'
import { Button } from '@/components/ui/button'
import { Card, CardTitle } from '@/components/ui/card'
import { apiPost, apiUrl } from '@/lib/api'
import { useAppStore } from '@/store/useAppStore'
import type { TFunction } from 'i18next'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useRef, useState } from 'react'
import { Trans, useTranslation } from 'react-i18next'
import { Link, useParams } from 'react-router-dom'

interface LogEvent {
  raw: Record<string, unknown>
  label: string
  status: 'info' | 'ok' | 'err'
}

function summarizeEvent(e: Record<string, unknown>, t: TFunction): LogEvent {
  const ev = String(e.event ?? 'message')
  if (ev === 'step_start') {
    return {
      raw: e,
      status: 'info',
      label: t('runner.stepStart', { step: String(e.step ?? '') }),
    }
  }
  if (ev === 'step_ok') {
    const dur = e.duration_s != null ? ` (${String(e.duration_s)}s)` : ''
    return {
      raw: e,
      status: 'ok',
      label: t('runner.stepOk', { step: String(e.step ?? ''), dur }),
    }
  }
  if (ev === 'step_skip') {
    return {
      raw: e,
      status: 'info',
      label: t('runner.stepSkip', { step: String(e.step ?? ''), reason: String(e.reason ?? '') }),
    }
  }
  if (ev === 'step_error') {
    return {
      raw: e,
      status: 'err',
      label: t('runner.stepError', { step: String(e.step ?? ''), error: String(e.error ?? '') }),
    }
  }
  if (ev === 'draft_snapshot') {
    const h = e.hash != null ? String(e.hash) : '—'
    return {
      raw: e,
      status: 'info',
      label: t('runner.draftSnapshot', { hash: h, chars: String(e.chars ?? '') }),
    }
  }
  if (ev === 'cursor_version') {
    return {
      raw: e,
      status: 'info',
      label: t('runner.cursorVersion', {
        agent: String(e.agent_bin ?? ''),
        version: String(e.version ?? '').slice(0, 80),
      }),
    }
  }
  if (ev === 'run_finished') {
    return {
      raw: e,
      status: 'ok',
      label: t('runner.runFinished', { code: String(e.exit_code ?? '') }),
    }
  }
  if (ev === 'run_error') {
    return {
      raw: e,
      status: 'err',
      label: t('runner.runError', { detail: String(e.detail ?? '') }),
    }
  }
  if (ev === 'stream_end') {
    return { raw: e, status: 'info', label: t('runner.streamEnd') }
  }
  return { raw: e, status: 'info', label: JSON.stringify(e) }
}

async function ensureNotify() {
  if (!('Notification' in window)) return
  if (Notification.permission === 'default') {
    await Notification.requestPermission()
  }
}

export function Runner() {
  const { t } = useTranslation()
  const { id } = useParams<{ id: string }>()
  const qc = useQueryClient()
  const setPipelineRunning = useAppStore((s) => s.setPipelineRunning)
  const [events, setEvents] = useState<LogEvent[]>([])
  const [runId, setRunId] = useState<string | null>(null)
  const esRef = useRef<EventSource | null>(null)

  const summarize = useCallback((e: Record<string, unknown>) => summarizeEvent(e, t), [t])

  const start = useMutation({
    mutationFn: () => apiPost<{ run_id: string }>(`/api/missions/${id}/run`),
    onSuccess: async (res) => {
      await ensureNotify()
      setEvents([])
      setRunId(res.run_id)
      setPipelineRunning(true)
      void qc.invalidateQueries({ queryKey: ['missions'] })
    },
  })

  useEffect(() => {
    if (!id || !runId) return
    const url = apiUrl(`/api/missions/${id}/events/${runId}`)
    const es = new EventSource(url)
    esRef.current = es
    es.onmessage = (msg) => {
      try {
        const parsed = JSON.parse(msg.data) as Record<string, unknown>
        if (parsed.event === 'stream_end') {
          es.close()
          setPipelineRunning(false)
          void qc.invalidateQueries({ queryKey: ['missions'] })
          void qc.invalidateQueries({ queryKey: ['mission', id] })
          return
        }
        setEvents((prev) => [...prev, summarize(parsed)])
        if (parsed.event === 'run_finished' && Notification.permission === 'granted') {
          new Notification(t('runner.notifyDone'), {
            body: t('runner.notifyExit', { code: String(parsed.exit_code) }),
          })
        }
        if (parsed.event === 'run_error' && Notification.permission === 'granted') {
          new Notification(t('runner.notifyDone'), { body: String(parsed.detail) })
        }
      } catch {
        /* ignore */
      }
    }
    es.onerror = () => {
      es.close()
      setPipelineRunning(false)
    }
    return () => {
      es.close()
      esRef.current = null
    }
  }, [id, runId, qc, setPipelineRunning, summarize, t])

  const lastRaw = events.length ? events[events.length - 1].raw : null
  const jsonl = events.map((e) => JSON.stringify(e.raw)).join('\n')

  function copyLast() {
    if (!lastRaw) return
    void navigator.clipboard.writeText(JSON.stringify(lastRaw, null, 2))
  }

  function downloadJsonl() {
    if (!runId || events.length === 0) return
    const blob = new Blob([jsonl], { type: 'application/x-ndjson' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `run-${runId}.jsonl`
    a.click()
    URL.revokeObjectURL(a.href)
  }

  if (!id) return <p className="p-6 text-zinc-500">{t('common.missingId')}</p>

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <MissionNav missionId={id} />
      <Card>
        <CardTitle>{t('runner.title')}</CardTitle>
        <p className="mb-4 text-sm text-zinc-500">
          <Trans i18nKey="runner.blurb" components={{ code: <code className="text-zinc-300" /> }} />
        </p>
        <Button onClick={() => start.mutate()} disabled={start.isPending}>
          {start.isPending ? t('runner.starting') : t('runner.run')}
        </Button>
        {start.isError && (
          <p className="mt-2 text-sm text-red-400">{(start.error as Error).message}</p>
        )}

        {runId && (
          <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-zinc-400">
            <span className="font-mono text-zinc-300">
              {t('runner.runId')} {runId}
            </span>
            <Link
              to={`/missions/${id}/live?run_id=${runId}&autoconnect=1`}
              className="rounded border border-zinc-600 px-2 py-1 text-violet-300 hover:bg-zinc-800"
            >
              {t('runner.liveLink')}
            </Link>
            <Button type="button" variant="outline" className="h-8 text-xs" onClick={copyLast}>
              {t('runner.copyLast')}
            </Button>
            <Button
              type="button"
              variant="outline"
              className="h-8 text-xs"
              disabled={events.length === 0}
              onClick={downloadJsonl}
            >
              {t('runner.downloadJsonl')}
            </Button>
          </div>
        )}

        <ul className="mt-6 max-h-[480px] space-y-2 overflow-auto rounded-md border border-zinc-800 bg-zinc-950 p-3 font-mono text-xs">
          {events.map((ev, i) => (
            <li
              key={`${i}-${ev.label}`}
              className={
                ev.status === 'ok'
                  ? 'text-emerald-400'
                  : ev.status === 'err'
                    ? 'text-red-400'
                    : 'text-zinc-300'
              }
            >
              {ev.label}
            </li>
          ))}
          {events.length === 0 && runId && (
            <li className="text-zinc-500">{t('runner.waiting')}</li>
          )}
        </ul>
      </Card>
    </div>
  )
}
