import { MissionNav } from '@/components/MissionNav'
import { Button } from '@/components/ui/button'
import { Card, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { apiPost, apiUrl } from '@/lib/api'
import { useAppStore } from '@/store/useAppStore'
import type { LoopRequestBody } from '@/types/mission'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { Trans, useTranslation } from 'react-i18next'
import { Link, useParams } from 'react-router-dom'

export function LoopControl() {
  const { t } = useTranslation()
  const { id } = useParams<{ id: string }>()
  const qc = useQueryClient()
  const setPipelineRunning = useAppStore((s) => s.setPipelineRunning)
  const [form, setForm] = useState<LoopRequestBody>({
    perplexity_section: null,
    perplexity_extra: '',
    include_notion: false,
    cursor_prompt: '',
    run_meta: true,
  })
  const [events, setEvents] = useState<string[]>([])
  const [runId, setRunId] = useState<string | null>(null)

  const start = useMutation({
    mutationFn: async () => {
      if ('Notification' in window && Notification.permission === 'default') {
        await Notification.requestPermission()
      }
      return apiPost<{ run_id: string }>(`/api/missions/${id}/loop`, form)
    },
    onSuccess: (res) => {
      setEvents([])
      setRunId(res.run_id)
      setPipelineRunning(true)
      void qc.invalidateQueries({ queryKey: ['missions'] })
    },
  })

  useEffect(() => {
    if (!id || !runId) return
    const es = new EventSource(apiUrl(`/api/missions/${id}/events/${runId}`))
    es.onmessage = (msg) => {
      try {
        const parsed = JSON.parse(msg.data) as Record<string, unknown>
        if (parsed.event === 'stream_end') {
          es.close()
          setPipelineRunning(false)
          void qc.invalidateQueries({ queryKey: ['missions'] })
          return
        }
        setEvents((prev) => [...prev, JSON.stringify(parsed)])
        if (
          (parsed.event === 'loop_finished' || parsed.event === 'loop_error') &&
          'Notification' in window &&
          Notification.permission === 'granted'
        ) {
          new Notification(t('loop.notifyLoop'), {
            body:
              parsed.event === 'loop_finished'
                ? t('runner.notifyExit', { code: String(parsed.exit_code) })
                : String(parsed.detail),
          })
        }
      } catch {
        /* ignore */
      }
    }
    es.onerror = () => {
      es.close()
      setPipelineRunning(false)
    }
    return () => es.close()
  }, [id, runId, qc, setPipelineRunning, t])

  if (!id) return <p className="p-6 text-zinc-500">{t('common.missingId')}</p>

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <MissionNav missionId={id} />
      <Card>
        <CardTitle>{t('loop.title')}</CardTitle>
        <p className="mb-4 text-sm text-zinc-500">
          <Trans i18nKey="loop.blurb" components={{ code: <code className="text-zinc-300" /> }} />
        </p>

        <div className="space-y-3">
          <div>
            <Label htmlFor="psec">{t('loop.perplexitySection')}</Label>
            <Input
              id="psec"
              placeholder={t('loop.perplexityPlaceholder')}
              value={form.perplexity_section ?? ''}
              onChange={(e) =>
                setForm({
                  ...form,
                  perplexity_section: e.target.value.trim() ? e.target.value.trim() : null,
                })
              }
            />
          </div>
          <div>
            <Label htmlFor="pex">{t('loop.perplexityExtra')}</Label>
            <textarea
              id="pex"
              className="min-h-[80px] w-full rounded-md border border-zinc-700 bg-zinc-900 px-2 py-1.5 text-sm"
              value={form.perplexity_extra}
              onChange={(e) => setForm({ ...form, perplexity_extra: e.target.value })}
            />
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={form.include_notion}
              onChange={(e) => setForm({ ...form, include_notion: e.target.checked })}
            />
            {t('loop.includeNotion')}
          </label>
          <div>
            <Label htmlFor="cur">{t('loop.cursorPrompt')}</Label>
            <textarea
              id="cur"
              className="min-h-[100px] w-full rounded-md border border-zinc-700 bg-zinc-900 px-2 py-1.5 text-sm"
              value={form.cursor_prompt}
              onChange={(e) => setForm({ ...form, cursor_prompt: e.target.value })}
            />
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={form.run_meta}
              onChange={(e) => setForm({ ...form, run_meta: e.target.checked })}
            />
            {t('loop.runMeta')}
          </label>

          <Button type="button" onClick={() => start.mutate()} disabled={start.isPending}>
            {start.isPending ? t('loop.launching') : t('loop.run')}
          </Button>
          {runId && (
            <Link
              to={`/missions/${id}/live?run_id=${runId}&autoconnect=1`}
              className="ml-2 inline-block rounded border border-zinc-600 px-2 py-1.5 text-sm text-violet-300 hover:bg-zinc-800"
            >
              {t('loop.liveLink')}
            </Link>
          )}
          {start.isError && (
            <p className="text-sm text-red-400">{(start.error as Error).message}</p>
          )}
        </div>

        <ul className="mt-6 max-h-[360px] space-y-1 overflow-auto rounded-md border border-zinc-800 bg-zinc-950 p-3 font-mono text-xs text-zinc-300">
          {events.map((line, i) => (
            <li key={i}>{line}</li>
          ))}
        </ul>
      </Card>
    </div>
  )
}
