import { Button } from '@/components/ui/button'
import { Card, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { API_BASE, apiGet, apiPost, apiUrl } from '@/lib/api'
import { useAppStore } from '@/store/useAppStore'
import {
  defaultMissionCreateBody,
  type MissionCreateBody,
  type MissionListItem,
} from '@/types/mission'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { Trans, useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

function apiBaseHostLabel(base: string): string {
  try {
    return new URL(base).host
  } catch {
    return base
  }
}

const codeErr = <code className="rounded bg-red-950/80 px-1 text-red-100" />

function FlagChips({
  flags,
  labels,
}: {
  flags: MissionListItem['flags_v2']
  labels: { epistemic: string; degradation: string; skills: string; triage: string }
}) {
  if (!flags) return null
  const on = [
    flags.enable_epistemic_injection && labels.epistemic,
    flags.enable_degradation_monitor && labels.degradation,
    flags.enable_skill_orchestrator && labels.skills,
    flags.enable_hypervisor_triage && labels.triage,
  ].filter(Boolean) as string[]
  if (on.length === 0) return null
  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      {on.map((label) => (
        <span
          key={label}
          className="rounded-full border border-violet-800/60 bg-violet-950/40 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-violet-200"
        >
          {label}
        </span>
      ))}
    </div>
  )
}

export function Home() {
  const { t } = useTranslation()
  const qc = useQueryClient()
  const pipelineRunning = useAppStore((s) => s.pipelineRunning)
  const [q, setQ] = useState('')
  const { data, isLoading, error } = useQuery({
    queryKey: ['missions'],
    queryFn: () => apiGet<MissionListItem[]>('/api/missions/'),
    refetchInterval: pipelineRunning ? 5000 : false,
  })

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: () => apiGet<{ status: string; version?: string }>('/api/health'),
    retry: 1,
    staleTime: 60_000,
  })

  const filtered = useMemo(() => {
    if (!data) return []
    const s = q.trim().toLowerCase()
    if (!s) return data
    return data.filter(
      (m) =>
        m.title.toLowerCase().includes(s) ||
        m.id.toLowerCase().includes(s) ||
        (m.description && m.description.toLowerCase().includes(s)),
    )
  }, [data, q])

  const create = useMutation({
    mutationFn: () => {
      const b = defaultMissionCreateBody()
      const { quality_gates, hypotheses, ...rest } = b
      void quality_gates
      void hypotheses
      return apiPost<{ id: string }>(
        '/api/missions/',
        rest as Omit<MissionCreateBody, 'quality_gates' | 'hypotheses'>,
      )
    },
    onSuccess: (res) => {
      void qc.invalidateQueries({ queryKey: ['missions'] })
      window.location.href = `/missions/${res.id}/edit`
    },
  })

  const flagLabels = {
    epistemic: t('flags.epistemic'),
    degradation: t('flags.degradation'),
    skills: t('flags.skills'),
    triage: t('flags.triage'),
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-white">{t('home.title')}</h1>
          <p className="mt-1 text-sm text-zinc-400">
            {API_BASE ? (
              <>
                {t('home.subtitleRemote')}{' '}
                <span className="text-zinc-500" title={API_BASE}>
                  ({apiBaseHostLabel(API_BASE)})
                </span>
                {' · '}
              </>
            ) : (
              <>{t('home.subtitleLocal')}</>
            )}
            {t('home.subtitlePipeline')}
          </p>
          {health?.status === 'ok' && (
            <p className="mt-2 text-xs text-zinc-500">
              {t('home.apiConnected')}{' '}
              <span className="text-emerald-400/90">{t('home.connected')}</span>
              {health.version ? (
                <>
                  {' '}
                  {t('home.versionPrefix')}
                  {health.version}
                </>
              ) : null}
            </p>
          )}
        </div>
        <Button onClick={() => create.mutate()} disabled={create.isPending}>
          {t('home.newMission')}
        </Button>
      </div>

      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Input
          type="search"
          placeholder={t('home.searchPlaceholder')}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-md border-zinc-700 bg-zinc-900/80"
          aria-label={t('home.filterMissionsAria')}
        />
        <Button
          type="button"
          variant="outline"
          className="shrink-0 text-sm"
          onClick={async () => {
            const r = await fetch(apiUrl('/api/missions/export.tsv'))
            if (!r.ok) return
            const blob = await r.blob()
            const a = document.createElement('a')
            a.href = URL.createObjectURL(blob)
            a.download = 'paper-pipeline-missions.tsv'
            a.click()
            URL.revokeObjectURL(a.href)
          }}
        >
          {t('home.exportTsv')}
        </Button>
      </div>

      {isLoading && <p className="text-zinc-500">{t('common.loading')}</p>}
      {error && (
        <div className="mb-6 rounded-lg border border-red-900/50 bg-red-950/35 p-4 text-sm">
          <p className="font-medium text-red-300">{t('home.errorTitle')}</p>
          <p className="mt-2 text-red-200/90">
            {API_BASE ? (
              <Trans
                i18nKey="home.errorRemote"
                components={{
                  code1: codeErr,
                  code2: codeErr,
                }}
              />
            ) : (
              <Trans
                i18nKey="home.errorLocal"
                components={{
                  code1: codeErr,
                  code2: codeErr,
                  code3: codeErr,
                  code4: codeErr,
                  code5: codeErr,
                  code6: codeErr,
                  code7: codeErr,
                  code8: codeErr,
                }}
              />
            )}
          </p>
          <p className="mt-2 text-xs text-zinc-500">
            {t('home.detailPrefix')}{' '}
            {error instanceof Error ? error.message : String(error)}
          </p>
        </div>
      )}

      <ul className="space-y-3">
        {filtered.map((m) => (
          <li key={m.id}>
            <Card>
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <CardTitle className="mb-0 text-base">{m.title}</CardTitle>
                  <p className="mt-1 font-mono text-xs text-zinc-500">{m.id}</p>
                  <FlagChips flags={m.flags_v2} labels={flagLabels} />
                  {m.last_error && (
                    <p className="mt-2 text-xs text-amber-400">
                      {t('home.lastError')} {m.last_error}
                    </p>
                  )}
                </div>
                <Link
                  to={`/missions/${m.id}/edit`}
                  className="shrink-0 text-sm text-violet-400 hover:underline"
                >
                  {t('home.open')}
                </Link>
              </div>
            </Card>
          </li>
        ))}
      </ul>

      {data?.length === 0 && !isLoading && (
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-8 text-center">
          <p className="text-zinc-300">{t('home.emptyTitle')}</p>
          <p className="mt-2 text-sm text-zinc-500">
            <Trans
              i18nKey="home.emptyHint"
              components={{ strong: <strong className="text-zinc-300" />, span: <span className="text-zinc-400" /> }}
            />
          </p>
        </div>
      )}

      {data && data.length > 0 && filtered.length === 0 && (
        <p className="text-sm text-zinc-500">{t('home.noSearchResults')}</p>
      )}
    </div>
  )
}
